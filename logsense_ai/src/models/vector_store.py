import os
import logging
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS

class LogVectorStore:
    """
    Manages embedding generation and vector storage using FAISS.
    """
    def __init__(self, index_path="data/processed/faiss_index"):
        self.logger = logging.getLogger(__name__)
        self.index_path = index_path
        self.embeddings = OpenAIEmbeddings()
        self.vector_store = None

    def add_texts(self, texts, metadatas=None):
        """
        Generates embeddings for a list of texts and adds them to the FAISS index.
        """
        if not texts:
            self.logger.warning("No texts provided to add_texts.")
            return

        self.logger.info(f"Adding {len(texts)} chunks to vector store...")
        try:
            if self.vector_store is None:
                # Initialize new store
                self.vector_store = FAISS.from_texts(texts, self.embeddings, metadatas=metadatas)
            else:
                self.vector_store.add_texts(texts, metadatas=metadatas)
            self.logger.info("Successfully added texts to FAISS.")
        except Exception as e:
            self.logger.error(f"Error adding texts to vector store: {e}")
            raise

    def save(self):
        """
        Persists the FAISS index to disk.
        """
        if self.vector_store:
            self.vector_store.save_local(self.index_path)
            self.logger.info(f"FAISS index saved to {self.index_path}")
        else:
            self.logger.warning("No vector store to save.")

    def load(self):
        """
        Loads the FAISS index from disk.
        """
        if os.path.exists(self.index_path):
            try:
                self.vector_store = FAISS.load_local(self.index_path, self.embeddings, allow_dangerous_deserialization=True)
                self.logger.info(f"FAISS index loaded from {self.index_path}")
            except Exception as e:
                self.logger.error(f"Error loading FAISS index: {e}")
        else:
            self.logger.warning(f"Index path {self.index_path} does not exist. Starting fresh.")
    
    def similarity_search(self, query, k=5):
        """
        Performs semantic search.
        """
        if not self.vector_store:
            self.logger.warning("Vector store not initialized. Returning empty results.")
            return []
        
        return self.vector_store.similarity_search(query, k=k)
