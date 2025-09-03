"""
Tools for Agentic RAG
"""
from typing import List, Optional, Any
from langchain_core.tools import BaseTool
from langchain_core.documents import Document
from pydantic import BaseModel, Field
import json
import requests
from datetime import datetime


class DocumentSearchInput(BaseModel):
    """Input for document search tool"""
    query: str = Field(description="Search query for documents")
    k: int = Field(default=4, description="Number of documents to return")


class DocumentSearchTool(BaseTool):
    """Tool for searching documents in vector store"""
    name: str = "document_search"
    description: str = "Search for relevant documents based on a query. Use this when you need to find information from the knowledge base."
    args_schema: type[BaseModel] = DocumentSearchInput
    vector_store_manager: object = None
    
    def __init__(self, vector_store_manager):
        super().__init__()
        object.__setattr__(self, 'vector_store_manager', vector_store_manager)
    
    def _run(self, query: str, k: int = 4) -> str:
        """Execute the document search"""
        try:
            docs = self.vector_store_manager.search(query, k)
            if not docs:
                return f"ไม่พบเอกสารที่เกี่ยวข้องกับคำค้นหา: '{query}' ในฐานข้อมูล"
            
            # Process and combine information from documents
            combined_content = []
            sources = []
            
            for i, doc in enumerate(docs, 1):
                source = doc.metadata.get("source", "Unknown")
                sources.append(source)
                content = doc.page_content.strip()
                
                # Add content with context
                combined_content.append(f"เอกสารที่ {i} ({source}):\n{content}")
            
            # Create comprehensive response
            result = f"ผลการค้นหาสำหรับ '{query}':\n\n"
            result += "\n\n".join(combined_content)
            result += f"\n\nแหล่งข้อมูล: {', '.join(set(sources))}"
            result += f"\n\n[หมายเหตุ: ข้อมูลข้างต้นมาจากเอกสารในระบบ กรุณาประมวลผลและตอบคำถามผู้ใช้โดยตรงจากข้อมูลเหล่านี้]"
            
            return result
        except Exception as e:
            return f"เกิดข้อผิดพลาดในการค้นหาเอกสารสำหรับ '{query}': {str(e)}"


class WebSearchInput(BaseModel):
    """Input for web search tool"""
    query: str = Field(description="Search query for web search")


class WebSearchTool(BaseTool):
    """Tool for searching the web for current information"""
    name: str = "web_search"
    description: str = "Search the web for current information when the knowledge base doesn't have relevant information."
    args_schema: type[BaseModel] = WebSearchInput
    
    def _run(self, query: str) -> str:
        """Execute web search (placeholder implementation)"""
        try:
            # This is a placeholder implementation
            # In a real scenario, you would integrate with a web search API like Google Custom Search, Bing, etc.
            return f"Web search for '{query}' would be performed here. This is a placeholder implementation."
        except Exception as e:
            return f"Error performing web search: {str(e)}"


class CalculatorInput(BaseModel):
    """Input for calculator tool"""
    expression: str = Field(description="Mathematical expression to calculate")


class CalculatorTool(BaseTool):
    """Tool for performing calculations"""
    name: str = "calculator"
    description: str = "Perform mathematical calculations. Use this for any mathematical operations."
    args_schema: type[BaseModel] = CalculatorInput
    
    def _run(self, expression: str) -> str:
        """Execute calculation"""
        try:
            # Safe evaluation of mathematical expressions
            allowed_names = {
                k: v for k, v in __builtins__.items() if k in ['abs', 'round', 'min', 'max', 'sum']
            }
            allowed_names.update({
                'pi': 3.14159265359,
                'e': 2.71828182846
            })
            
            result = eval(expression, {"__builtins__": {}}, allowed_names)
            return f"The result of {expression} is: {result}"
        except Exception as e:
            return f"Error calculating expression '{expression}': {str(e)}"


class DocumentSummaryInput(BaseModel):
    """Input for document summary tool"""
    query: str = Field(description="Topic or question to summarize documents about")


class DocumentSummaryTool(BaseTool):
    """Tool for getting summaries of documents"""
    name: str = "document_summary"
    description: str = "Get a summary of documents related to a specific topic or question."
    args_schema: type[BaseModel] = DocumentSummaryInput
    vector_store_manager: object = None
    llm: object = None
    
    def __init__(self, vector_store_manager, llm):
        super().__init__()
        object.__setattr__(self, 'vector_store_manager', vector_store_manager)
        object.__setattr__(self, 'llm', llm)
    
    def _run(self, query: str) -> str:
        """Execute document summary"""
        try:
            # Search for relevant documents
            docs = self.vector_store_manager.search(query, k=6)
            if not docs:
                return "No relevant documents found for summarization."
            
            # Combine document content
            combined_content = "\n\n".join([doc.page_content for doc in docs])
            
            # Create summary prompt
            summary_prompt = f"""
            Please provide a comprehensive summary of the following documents related to: {query}

            Documents:
            {combined_content}

            Summary:
            """
            
            # Generate summary using LLM
            summary = self.llm.predict(summary_prompt)
            return summary
            
        except Exception as e:
            return f"Error generating document summary: {str(e)}"


def get_tools(vector_store_manager, llm=None):
    """Get all available tools for the agent"""
    tools = [
        DocumentSearchTool(vector_store_manager),
        WebSearchTool(),
        CalculatorTool(),
    ]
    
    if llm:
        tools.append(DocumentSummaryTool(vector_store_manager, llm))
    
    return tools
