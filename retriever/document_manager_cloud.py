import logging
import os
import tempfile
from typing import Any, Dict, List, Optional
import uuid
import hashlib
from data.pdf_reader import PDFReader
from retriever.chunk_documents import chunk_documents
from retriever.vector_store_manager_cloud import VectorStoreManager
from retriever.language_utils import detect_language, translate_text, translate_chunks

class DocumentManager:
    def __init__(self):
        self.pdf_reader = PDFReader()
        self.vector_manager = VectorStoreManager()
        self.uploaded_documents = {}  # filename -> doc_id mapping
        self.chunked_documents = {}   # filename -> chunks mapping
        self.document_ids = {}        # filename -> doc_id mapping
        self.document_languages = {}  # filename -> language mapping
        logging.info("Multilingual DocumentManager initialized")

    def process_document(self, file_content, filename):
        """
        Process an uploaded file from memory: read PDF, chunk, and store in vector store.

        Args:
            file_content (bytes): The binary content of the uploaded file
            filename (str): The name of the file

        Returns:
            (status_message, filename, doc_id)
        """
        try:
            if not file_content:
                return "No file content provided", None, None

            logging.info(f"Processing file: {filename}")

            # Save to temporary file for PDF processing
            with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as temp_file:
                temp_file.write(file_content)
                temp_path = temp_file.name

            try:
                # Read PDF content
                page_list = self.pdf_reader.read_pdf(temp_path)

                # Generate a unique document ID
                doc_id = str(uuid.uuid4())

                # Store mappings
                self.uploaded_documents[filename] = True
                self.document_ids[filename] = doc_id

                # Detect document language from the first page (if available)
                doc_language = 'en'  # Default to English
                if page_list and isinstance(page_list[0], str) and len(page_list[0].strip()) > 100:
                    doc_language, lang_name = detect_language(page_list[0])
                    logging.info(f"Detected document language: {lang_name} ({doc_language})")

                # Store document language
                self.document_languages[filename] = doc_language

                # Chunk the pages
                chunks = chunk_documents(page_list, doc_id, chunk_size=2000, chunk_overlap=300)

                # Add language information to chunks
                for chunk in chunks:
                    chunk['language'] = doc_language

                self.chunked_documents[filename] = chunks

                # Add chunks to vector store
                self.vector_manager.add_documents(chunks)

                return (
                    f"Successfully loaded {filename} with {len(page_list)} pages",
                    filename,
                    doc_id
                )
            finally:
                # Clean up temporary file
                try:
                    os.unlink(temp_path)
                except:
                    pass

        except Exception as e:
            logging.error(f"Error processing document: {str(e)}")
            return f"Error: {str(e)}", None, None

    def get_uploaded_documents(self):
        """Return the list of uploaded document filenames."""
        return list(self.uploaded_documents.keys())

    def get_chunks(self, filename):
        """Return chunks for a given filename."""
        return self.chunked_documents.get(filename, [])

    def get_document_id(self, filename):
        """Return the document ID for a given filename."""
        return self.document_ids.get(filename, None)

    def retrieve_top_k(self, query: str, selected_docs: List[str], k: int = 5,
                    query_language: Optional[str] = None, target_language: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Retrieve the top K chunks across the selected documents based on the user's query.

        Args:
            query (str): The user's query.
            selected_docs (List[str]): List of selected document filenames from the dropdown.
            k (int): Number of top results to return (default is 5).
            query_language (Optional[str]): Language code of the query. If None, it will be detected.
            target_language (Optional[str]): Language to translate results to. If None, no translation.

        Returns:
            List[Dict[str, Any]]: List of top K chunks with their text, metadata, and scores.
        """
        if not selected_docs:
            logging.warning("No documents selected for retrieval")
            return []

        # Detect query language if not provided
        if not query_language:
            query_language, lang_name = detect_language(query)
            logging.info(f"Detected query language: {lang_name} ({query_language})")

        all_results = []
        for filename in selected_docs:
            doc_id = self.get_document_id(filename)
            if not doc_id:
                logging.warning(f"No document ID found for filename: {filename}")
                continue

            # Get document language
            doc_language = self.document_languages.get(filename, 'en')

            # Search for relevant chunks within this document
            results = self.vector_manager.search(
                query,
                doc_id,
                k=k,
                query_language=query_language,
                target_language=doc_language
            )
            all_results.extend(results)

        # Sort all results by score in ascending order (FAISS scores) and take the top K
        all_results.sort(key=lambda x: x['score'])
        top_k_results = all_results[:k]

        # Translate results if needed
        if target_language and target_language != query_language:
            translated_results = []
            for result in top_k_results:
                source_lang = result.get('source_language', 'en')
                if source_lang != target_language:
                    translated_text = translate_text(result['text'], target_language, source_lang)
                    result['original_text'] = result['text']
                    result['text'] = translated_text
                    result['translated_from'] = source_lang
                    result['translated_to'] = target_language
                translated_results.append(result)
            top_k_results = translated_results

        # Log the list of retrieved documents
        logging.info(f"Retrieved top {len(top_k_results)} documents:")
        for i, result in enumerate(top_k_results, 1):
            doc_id = result['metadata'].get('doc_id', 'Unknown')
            filename = next((name for name, d_id in self.document_ids.items() if d_id == doc_id), 'Unknown')
            lang_info = f", Language: {result.get('source_language', 'Unknown')}"
            if 'translated_from' in result:
                lang_info += f" (Translated from {result['translated_from']} to {result['translated_to']})"
            logging.info(f"{i}. Filename: {filename}, Doc ID: {doc_id}, Score: {result['score']:.4f}{lang_info}, Text: {result['text'][:100]}...")

        return top_k_results

    def retrieve_summary_chunks(self, query: str, doc_id: str, k: int = 10,
                             query_language: Optional[str] = None, target_language: Optional[str] = None):
        """
        Retrieve chunks for document summary with multilingual support.

        Args:
            query (str): The query to search for.
            doc_id (str): The document ID to search in.
            k (int): Number of chunks to retrieve.
            query_language (Optional[str]): Language code of the query. If None, it will be detected.
            target_language (Optional[str]): Language to translate results to. If None, no translation.

        Returns:
            List of chunks for summary generation.
        """
        # Detect query language if not provided
        if not query_language:
            query_language, lang_name = detect_language(query)
            logging.info(f"Detected summary query language: {lang_name} ({query_language})")

        # Find the filename for this doc_id to get its language
        filename = next((name for name, d_id in self.document_ids.items() if d_id == doc_id), None)
        doc_language = None
        if filename:
            doc_language = self.document_languages.get(filename, 'en')
            logging.info(f"Document language for summary: {doc_language}")

        logging.info(f"Retrieving {k} chunks for summary: {query}, Document Id: {doc_id}")
        results = self.vector_manager.search(
            query,
            doc_id,
            k=k,
            query_language=query_language,
            target_language=doc_language
        )
        top_k_results = results[:k]

        # Translate results if needed
        if target_language and target_language != (doc_language or 'en'):
            translated_results = []
            for result in top_k_results:
                source_lang = result.get('source_language', doc_language or 'en')
                if source_lang != target_language:
                    translated_text = translate_text(result['text'], target_language, source_lang)
                    result['original_text'] = result['text']
                    result['text'] = translated_text
                    result['translated_from'] = source_lang
                    result['translated_to'] = target_language
                translated_results.append(result)
            top_k_results = translated_results

        logging.info(f"Retrieved {len(top_k_results)} chunks for summary")

        return top_k_results
