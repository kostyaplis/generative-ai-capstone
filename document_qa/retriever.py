"""
Document Retriever

This module handles the retrieval of relevant document chunks from the vector store
to provide context for question answering.
"""

import logging
from typing import Dict, Any, List, Optional

from document_qa.indexer import DocumentIndexer

logger = logging.getLogger(__name__)


class DocumentRetriever:
    """
    Handles retrieval of relevant document context for queries.
    """

    def __init__(
        self, config: Dict[str, Any], indexer: Optional[DocumentIndexer] = None
    ):
        """
        Initialize the document retriever.

        Args:
            config: Configuration dictionary for retriever settings
            indexer: Optional pre-initialized document indexer
        """
        self.config = config

        # Use provided indexer or create a new one
        if indexer:
            self.indexer = indexer
        else:
            self.indexer = DocumentIndexer(config)

        self.default_top_k = config.get("retriever", {}).get("default_top_k", 5)
        self.vectorstore = self.indexer.get_vectorstore()
        logger.info("Document Retriever initialized")

    def retrieve_relevant_context(
        self, query: str, top_k: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Retrieve relevant document chunks for a query.

        Args:
            query: User query to find relevant context for
            top_k: Number of relevant chunks to retrieve (default: self.default_top_k)

        Returns:
            List of relevant document chunks with content and metadata
        """
        if top_k is None:
            top_k = self.default_top_k

        try:
            # Perform similarity search
            # Ensure top_k is an integer, not None
            k_value = top_k if top_k is not None else self.default_top_k
            documents = self.vectorstore.similarity_search(query, k=k_value)

            # Format results
            results = []
            for doc in documents:
                results.append(
                    {
                        "content": doc.page_content,
                        "metadata": doc.metadata,
                        "source": doc.metadata.get("source", "Unknown"),
                    }
                )

            logger.debug(
                f"Retrieved {len(results)} relevant document chunks for query: {query}"
            )
            return results

        except Exception as e:
            logger.error(f"Error retrieving relevant context: {e}")
            return []

    def get_retriever(self):
        """
        Get the underlying retriever for use in chains.

        Returns:
            FAISS retriever
        """
        return self.vectorstore.as_retriever(search_kwargs={"k": self.default_top_k})
