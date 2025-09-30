"""
Tools for the Agentic RAG system.
"""
import logging
from typing import List, Any

try:
    from langchain.tools import Tool
    from langchain.schema import Document
    from .vector_store import VectorStoreManager
    DEPENDENCIES_AVAILABLE = True
except ImportError as e:
    logging.warning(f"Tools dependencies not available: {e}")
    DEPENDENCIES_AVAILABLE = False


def create_rag_tools(vector_store_manager: VectorStoreManager) -> List[Tool]:
    """Create tools for the RAG agent."""
    if not DEPENDENCIES_AVAILABLE:
        return []
    
    def search_documents(query: str) -> str:
        """Search for relevant documents."""
        try:
            docs = vector_store_manager.similarity_search(query, k=5)
            if not docs:
                return "No relevant documents found."
            
            result = "Found relevant documents:\n\n"
            for i, doc in enumerate(docs, 1):
                source = doc.metadata.get('source', 'Unknown')
                content = doc.page_content[:500] + "..." if len(doc.page_content) > 500 else doc.page_content
                result += f"Document {i} (Source: {source}):\n{content}\n\n"
            
            return result
        except Exception as e:
            return f"Error searching documents: {str(e)}"
    
    def get_document_count() -> str:
        """Get the number of documents in the knowledge base."""
        try:
            count = vector_store_manager.get_document_count()
            return f"The knowledge base contains {count} documents."
        except Exception as e:
            return f"Error getting document count: {str(e)}"
    
    def search_with_score(query: str) -> str:
        """Search for documents with relevance scores."""
        try:
            results = vector_store_manager.similarity_search_with_score(query, k=3)
            if not results:
                return "No relevant documents found."
            
            result = "Found relevant documents with scores:\n\n"
            for i, (doc, score) in enumerate(results, 1):
                source = doc.metadata.get('source', 'Unknown')
                content = doc.page_content[:300] + "..." if len(doc.page_content) > 300 else doc.page_content
                result += f"Document {i} (Score: {score:.3f}, Source: {source}):\n{content}\n\n"
            
            return result
        except Exception as e:
            return f"Error searching documents with scores: {str(e)}"
    
    tools = [
        Tool(
            name="search_documents",
            description="Search for relevant documents in the knowledge base based on a query. Use this to find information related to the user's question.",
            func=search_documents
        ),
        Tool(
            name="get_document_count",
            description="Get the total number of documents in the knowledge base.",
            func=get_document_count
        ),
        Tool(
            name="search_with_score",
            description="Search for documents with relevance scores. Use this when you need to know how relevant the results are.",
            func=search_with_score
        )
    ]
    
    return tools


def create_custom_tool(name: str, description: str, func: Any) -> Tool:
    """Create a custom tool."""
    if not DEPENDENCIES_AVAILABLE:
        raise ImportError("Tools dependencies not available")
    
    return Tool(
        name=name,
        description=description,
        func=func
    )
