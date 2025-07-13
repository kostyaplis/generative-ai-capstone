"""
QA Generator

This module handles generating answers to user questions using the LLM
based on retrieved document context.
"""

import logging
from typing import Dict, Any, List, Optional

from langchain_openai import ChatOpenAI
from langchain.chains import ConversationalRetrievalChain
from langchain.memory import ConversationBufferMemory

from document_qa.retriever import DocumentRetriever

logger = logging.getLogger(__name__)


class DocumentQA:
    """
    Handles answering questions based on document content.
    """

    def __init__(
        self, config: Dict[str, Any], retriever: Optional[DocumentRetriever] = None
    ):
        """
        Initialize the document QA component.

        Args:
            config: Configuration dictionary for QA settings
            retriever: Optional pre-initialized document retriever
        """
        self.config = config

        # Use provided retriever or create a new one
        if retriever:
            self.retriever = retriever
        else:
            self.retriever = DocumentRetriever(config)

        # Initialize LLM for generating answers
        self.llm = ChatOpenAI(
            model=config.get("model_name", "gpt-4"),
            temperature=config.get("temperature", 0),
            api_key=config.get("openai_key"),
        )

        # Initialize conversation memory
        self.memory = ConversationBufferMemory(
            memory_key="chat_history", return_messages=True, output_key="answer"
        )

        # Initialize the QA chain
        self.qa_chain = ConversationalRetrievalChain.from_llm(
            self.llm,
            retriever=self.retriever.get_retriever(),
            memory=self.memory,
            output_key="answer",
        )

        logger.info("Document QA initialized")

    def retrieve_relevant_context(
        self, query: str, top_k: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Retrieve relevant document chunks for a query.

        Args:
            query: User query to find relevant context for
            top_k: Number of relevant chunks to retrieve

        Returns:
            List of relevant document chunks
        """
        return self.retriever.retrieve_relevant_context(query, top_k)

    def answer_question(
        self, query: str, conversation_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Answer a question based on document content.

        Args:
            query: User question
            conversation_id: Optional conversation ID to maintain context

        Returns:
            Dictionary with answer and supporting context
        """
        try:
            # Get response from QA chain
            response = self.qa_chain.invoke({"question": query})

            # Get supporting documents
            supporting_docs = self.retrieve_relevant_context(query)

            # Format response
            result = {
                "answer": response["answer"],
                "sources": supporting_docs,
                "success": True,
            }

            logger.debug(f"Generated answer for question: {query}")
            return result

        except Exception as e:
            logger.error(f"Error generating answer: {e}")
            return {
                "answer": "I'm sorry, I couldn't generate an answer based on the document.",
                "sources": [],
                "success": False,
                "error": str(e),
            }

    def process(
        self, query: str, params: Dict[str, Any] = {}, context: Dict[str, Any] = {}
    ) -> Dict[str, Any]:
        """
        Process a document QA query.

        Args:
            query: User query text
            params: Optional parameters (unused)
            context: Optional conversation context

        Returns:
            Dictionary with answer and supporting context
        """
        conversation_id = context.get("conversation_id") if context else None
        result = self.answer_question(query, conversation_id)

        return {
            "response": result["answer"],
            "sources": result.get("sources", []),
            "success": result.get("success", False),
        }
