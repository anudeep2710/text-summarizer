import os
import logging
from config.config import ConfigConstants
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
import tempfile

class VectorStoreManager:
    def __init__(self):
        """
        Initialize the vector store manager optimized for cloud deployment.
        Uses in-memory storage instead of persistent files.
        """
        self.embedding_model = HuggingFaceEmbeddings(model_name=ConfigConstants.EMBEDDING_MODEL_NAME)
        self.vector_store = None
        self.doc_id_filter = {}  # Track document IDs for filtering
        logging.info("Cloud-optimized VectorStoreManager initialized")

    def add_documents(self, documents):
        """
        Add new documents to the vector store (in-memory).
        
        Args:
            documents (list): List of dictionaries with 'text', 'source', and 'doc_id'.
        """
        if not documents:
            return

        texts = [doc['text'] for doc in documents]
        metadatas = [{'source': doc['source'], 'doc_id': doc['doc_id']} for doc in documents]
        
        # Track document IDs for filtering
        for doc in documents:
            doc_id = doc['doc_id']
            if doc_id not in self.doc_id_filter:
                self.doc_id_filter[doc_id] = True

        logging.info(f"Adding {len(texts)} documents to in-memory vector store")
        
        if not self.vector_store:
            self.vector_store = FAISS.from_texts(
                texts=texts,
                embedding=self.embedding_model,
                metadatas=metadatas
            )
        else:
            self.vector_store.add_texts(texts=texts, metadatas=metadatas)
        
        logging.info(f"Vector store updated in memory with {len(texts)} documents")

    def search(self, query, doc_id=None, k=5):
        """
        Search the vector store for documents similar to the query.
        
        Args:
            query (str): The query to search for.
            doc_id (str, optional): Filter results by document ID.
            k (int): Number of results to return.
            
        Returns:
            list: List of dictionaries with 'text', 'metadata', and 'score'.
        """
        if not self.vector_store:
            logging.warning("Vector store is empty, cannot search")
            return []
            
        # Create filter for specific document if doc_id is provided
        filter_dict = None
        if doc_id:
            filter_dict = {"doc_id": doc_id}
            
        # Perform the search
        try:
            results = self.vector_store.similarity_search_with_score(
                query, k=k, filter=filter_dict
            )
            
            # Format results
            formatted_results = []
            for doc, score in results:
                formatted_results.append({
                    'text': doc.page_content,
                    'metadata': doc.metadata,
                    'score': float(score)  # Convert to float for JSON serialization
                })
                
            return formatted_results
            
        except Exception as e:
            logging.error(f"Error searching vector store: {str(e)}")
            return []
