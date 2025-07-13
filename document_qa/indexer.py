"""
Document Indexer

This module handles loading PDF documents and indexing them into a vector store
for efficient retrieval and similarity search.
"""

import logging
import os
from typing import Dict, Any

from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS

logger = logging.getLogger(__name__)


class DocumentIndexer:
    """
    Handles loading, splitting, and indexing of documents for retrieval.
    """

    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the document indexer.

        Args:
            config: Configuration dictionary with indexer settings
        """
        self.config = config

        # Configuration
        self.documents_dir = config["document_qa"]["indexer"]["documents_dir"]
        self.db_directory = config["document_qa"]["indexer"]["db_directory"]
        self.chunk_size = config["document_qa"]["indexer"]["chunk_size"]
        self.chunk_overlap = config["document_qa"]["indexer"]["chunk_overlap"]

        # Create directories if they don't exist
        os.makedirs(self.documents_dir, exist_ok=True)
        os.makedirs(self.db_directory, exist_ok=True)

        # Initialize embeddings
        self.embeddings = OpenAIEmbeddings(api_key=config["openai_key"])

        # Load vector store if it exists, otherwise create it
        self.vectorstore = self._load_or_create_vectorstore()

        logger.info("Document Indexer initialized")

    def _load_or_create_vectorstore(self):
        """
        Load existing vector store or create a new one if it doesn't exist.

        Returns:
            FAISS vector store
        """
        try:
            # Try to load existing vector store
            if os.path.exists(os.path.join(self.db_directory, "index.faiss")):
                logger.info(f"Loading existing vector store from {self.db_directory}")
                return FAISS.load_local(
                    self.db_directory,
                    self.embeddings,
                    allow_dangerous_deserialization=True,
                )
            else:
                # Create new vector store by indexing documents
                return self._index_documents()
        except Exception as e:
            logger.error(f"Error loading vector store: {e}")
            # Fallback to creating a new one
            return self._index_documents()

    def _index_documents(self):
        """
        Index all documents in the documents directory.

        Returns:
            FAISS vector store
        """
        logger.info(f"Indexing documents from {self.documents_dir}")

        documents = []
        pdf_files = [f for f in os.listdir(self.documents_dir) if f.endswith(".pdf")]

        if not pdf_files:
            logger.warning(f"No PDF documents found in {self.documents_dir}")
            return FAISS.from_texts(["No documents available"], self.embeddings)

        # Load all PDF documents
        for pdf_file in pdf_files:
            try:
                file_path = os.path.join(self.documents_dir, pdf_file)
                logger.info(f"Loading document: {file_path}")

                # Load the PDF
                loader = PyPDFLoader(file_path)
                pdf_documents = loader.load()
                documents.extend(pdf_documents)

            except Exception as e:
                logger.error(f"Error loading {pdf_file}: {e}")

        # Split documents into chunks
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.chunk_size, chunk_overlap=self.chunk_overlap
        )
        chunks = text_splitter.split_documents(documents)

        # Create vector store
        vectorstore = FAISS.from_documents(chunks, self.embeddings)

        # Save the vector store for future use
        vectorstore.save_local(self.db_directory)

        logger.info(f"Indexed {len(chunks)} document chunks")
        return vectorstore

    def get_vectorstore(self):
        """
        Get the vector store for similarity search.

        Returns:
            FAISS vector store
        """
        return self.vectorstore

    def refresh_index(self):
        """
        Re-index all documents (for use when documents are updated).

        Returns:
            FAISS vector store
        """
        self.vectorstore = self._index_documents()
        return self.vectorstore
