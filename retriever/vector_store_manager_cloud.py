import os
import logging
from config.config import ConfigConstants
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
import tempfile
from typing import Dict, Optional, List, Any
from .language_utils import detect_language, get_embedding_model_for_language

class VectorStoreManager:
    def __init__(self):
        """
        Initialize the vector store manager optimized for cloud deployment.
        Uses in-memory storage instead of persistent files.
        """
        # Default embedding model (English)
        self.default_embedding_model = HuggingFaceEmbeddings(model_name=ConfigConstants.EMBEDDING_MODEL_NAME)

        # Dictionary to store language-specific embedding models
        self.embedding_models: Dict[str, HuggingFaceEmbeddings] = {
            'en': self.default_embedding_model
        }

        # Dictionary to store language-specific vector stores
        self.vector_stores: Dict[str, Any] = {}

        # Default vector store (English)
        self.vector_store = None

        self.doc_id_filter = {}  # Track document IDs for filtering
        self.document_languages = {}  # Track document languages

        logging.info("Multilingual VectorStoreManager initialized")

    def get_embedding_model(self, lang_code: str) -> HuggingFaceEmbeddings:
        """
        Get or create an embedding model for the specified language.

        Args:
            lang_code (str): The language code

        Returns:
            HuggingFaceEmbeddings: The embedding model for the language
        """
        if lang_code not in self.embedding_models:
            # Get the appropriate model name for this language
            model_name = get_embedding_model_for_language(lang_code)

            # Create a new embedding model
            self.embedding_models[lang_code] = HuggingFaceEmbeddings(model_name=model_name)
            logging.info(f"Created new embedding model for {lang_code} using {model_name}")

        return self.embedding_models[lang_code]

    def add_documents(self, documents):
        """
        Add new documents to the vector store (in-memory).

        Args:
            documents (list): List of dictionaries with 'text', 'source', and 'doc_id'.
        """
        if not documents:
            return

        # Group documents by language
        documents_by_language = {}

        for doc in documents:
            # Detect language if not already in metadata
            if 'language' not in doc:
                lang_code, _ = detect_language(doc['text'])
                doc['language'] = lang_code
            else:
                lang_code = doc['language']

            # Initialize language group if needed
            if lang_code not in documents_by_language:
                documents_by_language[lang_code] = []

            # Add document to appropriate language group
            documents_by_language[lang_code].append(doc)

            # Track document ID and language
            doc_id = doc['doc_id']
            if doc_id not in self.doc_id_filter:
                self.doc_id_filter[doc_id] = True
            self.document_languages[doc_id] = lang_code

        # Process each language group separately
        for lang_code, lang_documents in documents_by_language.items():
            texts = [doc['text'] for doc in lang_documents]
            metadatas = [{'source': doc['source'], 'doc_id': doc['doc_id'], 'language': doc['language']}
                         for doc in lang_documents]

            # Get the appropriate embedding model for this language
            embedding_model = self.get_embedding_model(lang_code)

            logging.info(f"Adding {len(texts)} {lang_code} documents to in-memory vector store")

            # Create or update the vector store for this language
            if lang_code not in self.vector_stores or self.vector_stores[lang_code] is None:
                self.vector_stores[lang_code] = FAISS.from_texts(
                    texts=texts,
                    embedding=embedding_model,
                    metadatas=metadatas
                )
            else:
                self.vector_stores[lang_code].add_texts(texts=texts, metadatas=metadatas)

            # Update the default vector store if it's English
            if lang_code == 'en':
                self.vector_store = self.vector_stores[lang_code]

            logging.info(f"Vector store updated for language {lang_code} with {len(texts)} documents")

        # If we don't have an English vector store but have other languages, use the first one as default
        if self.vector_store is None and self.vector_stores:
            first_lang = next(iter(self.vector_stores))
            self.vector_store = self.vector_stores[first_lang]
            logging.info(f"Using {first_lang} vector store as default")

    def search(self, query, doc_id=None, k=5, query_language=None, target_language=None):
        """
        Search the vector store for documents similar to the query.

        Args:
            query (str): The query to search for.
            doc_id (str, optional): Filter results by document ID.
            k (int): Number of results to return.
            query_language (str, optional): Language code of the query. If None, it will be detected.
            target_language (str, optional): Language to search in. If None, search in all languages.

        Returns:
            list: List of dictionaries with 'text', 'metadata', and 'score'.
        """
        # Check if we have any vector stores
        if not self.vector_stores and not self.vector_store:
            logging.warning("Vector store is empty, cannot search")
            return []

        # Detect query language if not provided
        if not query_language:
            query_language, _ = detect_language(query)
            logging.info(f"Detected query language: {query_language}")

        # If doc_id is provided, get its language
        doc_language = None
        if doc_id and doc_id in self.document_languages:
            doc_language = self.document_languages[doc_id]
            logging.info(f"Document {doc_id} is in language: {doc_language}")

        # Determine which vector stores to search
        vector_stores_to_search = []

        if doc_id:
            # If searching a specific document, use its language vector store
            if doc_language and doc_language in self.vector_stores:
                vector_stores_to_search.append((doc_language, self.vector_stores[doc_language]))
            elif self.vector_store:
                # Fallback to default vector store
                vector_stores_to_search.append(('default', self.vector_store))
        elif target_language and target_language in self.vector_stores:
            # If target language is specified, use that vector store
            vector_stores_to_search.append((target_language, self.vector_stores[target_language]))
        elif query_language in self.vector_stores:
            # If no target language, use query language vector store
            vector_stores_to_search.append((query_language, self.vector_stores[query_language]))
            # Also search English if query is not in English
            if query_language != 'en' and 'en' in self.vector_stores:
                vector_stores_to_search.append(('en', self.vector_stores['en']))
        else:
            # Search all vector stores
            for lang, vs in self.vector_stores.items():
                vector_stores_to_search.append((lang, vs))

        # If no vector stores to search, use default
        if not vector_stores_to_search and self.vector_store:
            vector_stores_to_search.append(('default', self.vector_store))

        # Create filter for specific document if doc_id is provided
        filter_dict = None
        if doc_id:
            filter_dict = {"doc_id": doc_id}

        # Perform the search across all selected vector stores
        all_results = []

        for lang, vs in vector_stores_to_search:
            try:
                logging.info(f"Searching in {lang} vector store")
                results = vs.similarity_search_with_score(
                    query, k=k, filter=filter_dict
                )

                # Format results
                for doc, score in results:
                    all_results.append({
                        'text': doc.page_content,
                        'metadata': doc.metadata,
                        'score': float(score),  # Convert to float for JSON serialization
                        'source_language': doc.metadata.get('language', lang)
                    })
            except Exception as e:
                logging.error(f"Error searching {lang} vector store: {str(e)}")

        # Sort results by score (ascending order for FAISS)
        all_results.sort(key=lambda x: x['score'])

        # Limit to top k results
        return all_results[:k] if all_results else []
