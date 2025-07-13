"""
SQL Agent

This module handles SQL queries, interacting with databases
and managing query execution and result formatting.
"""

import logging
import os
from typing import Dict, Any
import sqlite3
from langchain_openai import ChatOpenAI
from tabulate import tabulate

logger = logging.getLogger(__name__)


class SQLAgent:
    """
    Agent for handling SQL database queries.
    """

    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the SQL agent.

        Args:
            config: Configuration dictionary for SQL agent settings
        """
        self.config = config

        # Initialize database path
        self.db_path = os.path.join(
            config["agents"]["sql_agent"]["db_path"], "employees.db"
        )

        # Initialize LLM
        self.llm = ChatOpenAI(
            model=config["model_name"],
            temperature=config["temperature"],
            api_key=config["openai_key"],
        )

        logger.info("SQL Agent initialized")

    def _get_schema(self):
        return """
        Table: employees
        Columns:
        - id INTEGER PRIMARY KEY,
        - first_name TEXT NOT NULL,
        - last_name TEXT NOT NULL,
        - department TEXT NOT NULL,
        - salary REAL NOT NULL,
        - age INTEGER NOT NULL
    """

    def _generate_sql(self, question: str) -> str:
        messages = [
            {
                "role": "system",
                "content": f"""
                    You are a SQL expert. Use this schema:\n{self._get_schema()}
                    Return ONLY the SQL query without any explanation or markdown formatting.
                """,
            },
            {"role": "user", "content": f"Generate SQL for: {question}"},
        ]
        response = self.llm.invoke(messages)

        logger.debug(f"LLM response: {response}")

        # Extract content from LLM response
        if hasattr(response, "content"):
            sql = str(response.content)
            if not self._validate_sql(sql):
                return ""
            return sql
        else:
            logger.error(f"Unexpected LLM response format: {type(response)}")
            raise ValueError("Unexpected LLM response format")

    def _validate_sql(self, sql: str) -> bool:
        # Basic safety checks
        if any(word in sql.lower() for word in ["drop", "delete", "update", "insert"]):
            logger.error("Only SELECT queries are allowed")
            return False
        try:
            # Connect to database
            conn = sqlite3.connect(self.db_path)
            c = conn.cursor()

            # Try to execute the SQL
            c.execute("EXPLAIN " + sql)
            return True
        except Exception as e:
            logger.error(f"Invalid SQL query: {e}")
            return False
        finally:
            conn.close()

    def _execute_query(self, sql: str) -> list[Any] | str:
        conn = sqlite3.connect(self.db_path)
        try:
            cursor = conn.cursor()
            cursor.execute(sql)
            results = cursor.fetchall()
            return results
        except Exception as e:
            logger.error(f"Error executing SQL query: {e}")
            return ""
        finally:
            conn.close()

    def format_results(self, results):
        if not isinstance(results, list) or not results:
            return "No results found"

        # Define headers
        headers = ["ID", "First Name", "Last Name", "Department", "Salary", "Age"]

        # Return tabulated results
        return tabulate(results, headers=headers, tablefmt="grid")

    def process(
        self, query: str, params: Dict[str, Any] = {}, context: Dict[str, Any] = {}
    ) -> Dict[str, Any]:
        """
        Process a SQL-related query.

        Args:
            query: User's original query
            params: not in use
            context: not in use

        Returns:
            Dictionary with query results
        """

        sql = self._generate_sql(query)
        if not sql:
            return {
                "response": "I'm sorry, I couldn't generate a valid SQL query",
                "success": False,
            }
        results = self._execute_query(sql)
        if not results:
            return {
                "response": "I'm sorry, I couldn't execute the SQL query",
                "success": False,
            }
        return {"response": self.format_results(results), "success": True}
