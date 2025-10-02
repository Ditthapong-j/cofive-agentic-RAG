"""
FastAPI Backend for Agentic RAG System
Provides REST API endpoints while preserving original functionality
"""
import os
import sys
import tempfile
import shutil
from datetime import datetime
from pathlib import Path
from typing import List, Optional

import uvicorn
from fastapi import FastAPI, File, UploadFile, HTTPException, Query, Body
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from contextlib import asynccontextmanager

# Add src to path for imports
sys.path.append(str(Path(__file__).parent.parent / "src"))

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

from src.document_loader import DocumentLoader
from src.vector_store import VectorStoreManager
from src.agentic_rag import AgenticRAG

# Global variable for RAG system
rag_system = None

# Lifespan event handler
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    global rag_system
    print("🚀 Starting Agentic RAG API...")
    
    # Check OpenAI API key
    if not os.getenv("OPENAI_API_KEY"):
        print("❌ OPENAI_API_KEY not found in environment variables")
        print("💡 Please set OPENAI_API_KEY environment variable")
    
    # Initialize system
    try:
        rag_system = AgenticRAGSystem()
        print("✅ RAG system initialized successfully")
    except Exception as e:
        print(f"❌ Failed to initialize RAG system: {e}")
    
    yield
    
    # Shutdown (optional cleanup)
    print("🛑 Shutting down Agentic RAG API...")

# FastAPI app
app = FastAPI(
    title="Agentic RAG API",
    description="""# 🚀 Agentic Retrieval-Augmented Generation System API

## 📖 Overview
A comprehensive API for document-based question answering using RAG (Retrieval-Augmented Generation) technology.

## ✨ Features
- 📄 **Document Management**: Upload, process, and manage documents (PDF, TXT, MD)
- 🤖 **AI Agent**: Initialize and configure AI agents with different models
- 💬 **Query Processing**: Ask questions about uploaded documents
- 🔧 **System Management**: Health checks, status monitoring, and system reset

## 🔄 Workflow
1. **Upload Documents** → Upload your files using `/upload`
2. **Initialize Agent** → Set up AI agent with `/initialize`
3. **Query Documents** → Ask questions with `/query`
4. **Manage System** → Monitor and reset using system endpoints

## 🧠 Supported AI Models
- gpt-3.5-turbo
- gpt-4
- gpt-4-turbo
- gpt-4o
- gpt-4o-mini
- gpt-5-mini (default)

## 🔑 Authentication
Requires `OPENAI_API_KEY` environment variable.

## 📚 Quick Start
1. Set your OpenAI API key: `export OPENAI_API_KEY=your_key_here`
2. Upload documents via `/upload` endpoint
3. Initialize agent via `/initialize` endpoint
4. Start querying via `/query` endpoint
    """,
    version="1.0.0",
    lifespan=lifespan,
    contact={
        "name": "Agentic RAG API Support",
        "email": "support@example.com",
        "url": "https://github.com/your-repo/agentic-rag"
    },
    license_info={
        "name": "MIT",
        "url": "https://opensource.org/licenses/MIT",
    },
    openapi_tags=[
        {
            "name": "Health",
            "description": "🏥 System health and status monitoring endpoints",
        },
        {
            "name": "Documents",
            "description": "📄 Document upload and management operations",
        },
        {
            "name": "Agent",
            "description": "🤖 AI agent initialization and configuration",
        },
        {
            "name": "Query",
            "description": "💬 Question answering and document querying",
        },
        {
            "name": "System",
            "description": "⚙️ System management and configuration",
        },
    ],
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global system instance
rag_system = None
doc_loader = DocumentLoader()

# Pydantic models with comprehensive examples and documentation
class QueryRequest(BaseModel):
    """Request model for querying documents"""
    query: str = Field(
        ..., 
        description="The question to ask about the uploaded documents",
        examples=[
            "What is the main topic of the documents?",
            "Summarize the key points from the uploaded files",
            "What are the conclusions mentioned in the research?",
            "List all the important dates mentioned"
        ]
    )
    model: str = Field(
        default="gpt-4o-mini", 
        description="AI model to use for processing the query",
        examples=["gpt-4o-mini", "gpt-4", "gpt-3.5-turbo"]
    )
    temperature: float = Field(
        default=0.1, 
        ge=0.0, 
        le=2.0, 
        description="Model temperature (0.0=focused, 2.0=creative)"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "query": "What are the main findings in the uploaded research papers?",
                "model": "gpt-4o-mini",
                "temperature": 0.1
            }
        }

class QueryResponse(BaseModel):
    """Response model for document queries"""
    success: bool = Field(description="Whether the query was processed successfully")
    answer: str = Field(description="AI-generated answer based on the documents")
    sources: List[str] = Field(default=[], description="List of source documents used")
    model_used: str = Field(description="The AI model that was used")
    processing_time: float = Field(description="Time taken to process the query in seconds")
    error: Optional[str] = Field(default=None, description="Error message if query failed")

    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "answer": "Based on the uploaded documents, the main findings include...",
                "sources": ["document1.pdf", "research_notes.txt"],
                "model_used": "gpt-4o-mini",
                "processing_time": 2.34,
                "error": None
            }
        }

class SystemStatus(BaseModel):
    """System status information"""
    status: str = Field(description="Current system status (ready/needs_documents/error)")
    document_count: int = Field(description="Number of uploaded documents")
    agent_ready: bool = Field(description="Whether AI agent is initialized and ready")
    api_key_configured: bool = Field(description="Whether OpenAI API key is configured")
    version: str = Field(default="1.0.0", description="API version")

    class Config:
        json_schema_extra = {
            "example": {
                "status": "ready",
                "document_count": 3,
                "agent_ready": True,
                "api_key_configured": True,
                "version": "1.0.0"
            }
        }

class UploadResponse(BaseModel):
    """Response model for document upload"""
    success: bool = Field(description="Whether upload was successful")
    message: str = Field(description="Upload result message")
    files_processed: int = Field(description="Number of files successfully processed")
    total_documents: int = Field(description="Total documents in the system after upload")

    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "message": "Successfully processed 2 files",
                "files_processed": 2,
                "total_documents": 5
            }
        }

class InitResponse(BaseModel):
    """Response model for agent initialization"""
    success: bool = Field(description="Whether initialization was successful")
    message: str = Field(description="Initialization result message")
    agent_ready: bool = Field(description="Whether agent is ready for queries")
    document_count: int = Field(description="Number of documents available to the agent")

    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "message": "Agent initialized successfully",
                "agent_ready": True,
                "document_count": 3
            }
        }

# System initialization
class AgenticRAGSystem:
    """Main system class that wraps the core functionality"""
    
    def __init__(self, vectorstore_path: str = "./vectorstore"):
        self.vectorstore_path = vectorstore_path
        self.vector_store_manager = VectorStoreManager(persist_directory=vectorstore_path)
        self.agent = None
        self.model_name = "gpt-4o-mini"
        self.temperature = 0.1
        
        # Try to load existing vector store
        self.vector_store_manager.load_existing_store()
    
    def add_documents(self, documents):
        """Add documents to the vector store"""
        return self.vector_store_manager.add_documents(documents)
    
    def get_document_count(self):
        """Get document count"""
        return self.vector_store_manager.get_document_count()
    
    def initialize_agent(self, model_name: str = None, temperature: float = None):
        """Initialize the agent"""
        if self.get_document_count() == 0:
            return False
        
        self.model_name = model_name or self.model_name
        self.temperature = temperature or self.temperature
        
        try:
            self.agent = AgenticRAG(
                vector_store_manager=self.vector_store_manager,
                model_name=self.model_name,
                temperature=self.temperature
            )
            return True
        except Exception as e:
            print(f"Agent initialization error: {e}")
            return False
    
    def is_agent_ready(self):
        """Check if agent is ready"""
        return self.agent is not None
    
    def query(self, question: str):
        """Query the system"""
        if not self.agent:
            raise ValueError("Agent not initialized")
        return self.agent.query(question)
    
    def set_model(self, model_name: str, temperature: float):
        """Set model configuration"""
        self.model_name = model_name
        self.temperature = temperature
        if self.agent:
            self.agent.llm.model_name = model_name
            self.agent.llm.temperature = temperature

# API Routes
@app.get(
    "/health",
    tags=["Health"],
    summary="🏥 Health Check",
    description="Check if the API is running and healthy",
    responses={
        200: {
            "description": "API is healthy",
            "content": {
                "application/json": {
                    "example": {
                        "status": "healthy",
                        "timestamp": "2025-10-02T14:30:22.123456",
                        "version": "1.0.0"
                    }
                }
            }
        }
    }
)
async def health_check():
    """🏥 Check if the API is running and healthy.
    
    Returns basic health information including:
    - Service status
    - Current timestamp
    - API version
    
    This endpoint can be used for:
    - Load balancer health checks
    - Monitoring system status
    - Uptime verification
    """
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0"
    }

@app.get(
    "/status",
    response_model=SystemStatus,
    tags=["Health"],
    summary="📊 System Status",
    description="Get detailed system status and configuration",
    responses={
        200: {
            "description": "System status retrieved successfully",
            "content": {
                "application/json": {
                    "example": {
                        "status": "ready",
                        "document_count": 5,
                        "agent_ready": True,
                        "api_key_configured": True,
                        "version": "1.0.0"
                    }
                }
            }
        },
        500: {"description": "RAG system not initialized"}
    }
)
async def get_system_status():
    """📊 Get detailed system status and configuration.
    
    Returns comprehensive system information including:
    - **System Status**: ready, needs_documents, or error
    - **Document Count**: Number of uploaded documents
    - **Agent Status**: Whether AI agent is initialized
    - **API Key Status**: Whether OpenAI API key is configured
    - **Version**: Current API version
    
    **Status Values:**
    - `ready`: System is fully operational
    - `needs_documents`: No documents uploaded yet
    - `error`: System configuration issues
    
    Raises:
        HTTPException: 500 if RAG system not initialized
    """
    global rag_system
    
    if not rag_system:
        raise HTTPException(status_code=500, detail="RAG system not initialized")
    
    return SystemStatus(
        status="ready" if rag_system.is_agent_ready() else "needs_documents",
        document_count=rag_system.get_document_count(),
        agent_ready=rag_system.is_agent_ready(),
        api_key_configured=bool(os.getenv("OPENAI_API_KEY"))
    )

@app.post(
    "/upload",
    response_model=UploadResponse,
    tags=["Documents"],
    summary="📤 Upload Documents",
    description="Upload one or more documents to the system for processing",
    responses={
        200: {
            "description": "Documents uploaded successfully",
            "content": {
                "application/json": {
                    "example": {
                        "success": True,
                        "message": "Successfully processed 2 files",
                        "files_processed": 2,
                        "total_documents": 5
                    }
                }
            }
        },
        400: {"description": "No files provided or invalid file types"},
        500: {"description": "RAG system not initialized or processing error"}
    }
)
async def upload_documents(
    files: List[UploadFile] = File(
        ...,
        description="List of files to upload",
        examples=[
            {
                "summary": "PDF Document",
                "description": "Upload a PDF file",
                "value": "document.pdf"
            },
            {
                "summary": "Text File",
                "description": "Upload a text file",
                "value": "notes.txt"
            }
        ]
    )
):
    """📤 Upload one or more documents to the system.
    
    **Supported file types:**
    - 📄 **PDF** (.pdf) - Portable Document Format
    - 📝 **Text** (.txt) - Plain text files
    - 📋 **Markdown** (.md) - Markdown formatted text
    
    **Process:**
    1. Files are validated for supported formats
    2. Content is extracted and processed
    3. Documents are split into chunks
    4. Chunks are embedded and stored in vector database
    
    **Features:**
    - Multiple file upload support
    - Automatic content extraction
    - Smart text chunking
    - Vector embedding generation
    
    Args:
        files: List of files to upload (multipart/form-data)
        
    Returns:
        UploadResponse: Upload results with processing statistics
        
    Raises:
        HTTPException: 
            - 400: No files provided or invalid file types
            - 500: System not initialized or processing error
    """
    global rag_system
    
    if not rag_system:
        raise HTTPException(status_code=500, detail="RAG system not initialized")
    
    if not files:
        raise HTTPException(status_code=400, detail="No files provided")
    
    processed_files = 0
    total_docs_before = rag_system.get_document_count()
    
    for file in files:
        # Validate file type
        allowed_types = ['.pdf', '.txt', '.md']
        file_ext = Path(file.filename).suffix.lower()
        if file_ext not in allowed_types:
            continue
        
        # Create temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix=f"_{file.filename}") as temp_file:
            shutil.copyfileobj(file.file, temp_file)
            temp_path = temp_file.name
        
        try:
            # Load document
            if file_ext == '.pdf':
                documents = doc_loader.load_pdf(temp_path)
            else:
                documents = doc_loader.load_text(temp_path)
            
            if documents:
                rag_system.add_documents(documents)
                processed_files += 1
        except Exception as e:
            print(f"Error processing {file.filename}: {e}")
        finally:
            os.unlink(temp_path)
    
    total_docs_after = rag_system.get_document_count()
    
    return UploadResponse(
        success=True,
        message=f"Successfully processed {processed_files} files",
        files_processed=processed_files,
        total_documents=total_docs_after
    )

@app.post(
    "/initialize",
    response_model=InitResponse,
    tags=["Agent"],
    summary="🤖 Initialize AI Agent",
    description="Initialize the RAG agent with specified model and parameters",
    responses={
        200: {
            "description": "Agent initialized successfully",
            "content": {
                "application/json": {
                    "example": {
                        "success": True,
                        "message": "Agent initialized successfully",
                        "agent_ready": True,
                        "document_count": 3
                    }
                }
            }
        },
        400: {"description": "No documents available"},
        500: {"description": "System not initialized or agent creation failed"}
    }
)
async def initialize_agent(
    model: str = Query(
        default="gpt-4o-mini",
        description="AI model to use for the agent",
        examples=["gpt-4o-mini", "gpt-4", "gpt-3.5-turbo"]
    ),
    temperature: float = Query(
        default=0.1,
        ge=0.0,
        le=2.0,
        description="Model temperature (0.0-2.0). Lower values = more focused, higher = more creative"
    )
):
    """🤖 Initialize the RAG agent with specified model and temperature.
    
    **Prerequisites:**
    - At least one document must be uploaded first
    - OpenAI API key must be configured
    
    **Parameters:**
    - **Model**: Choose from available OpenAI models
    - **Temperature**: Controls response creativity (0.0 = deterministic, 2.0 = very creative)
    
    **Available Models:**
    - `gpt-3.5-turbo` - Fast and cost-effective
    - `gpt-4` - High quality reasoning
    - `gpt-4-turbo` - Latest GPT-4 with improved performance
    - `gpt-4o` - Optimized for various tasks
    - `gpt-4o-mini` - Lightweight version (recommended)
    - `gpt-5-mini` - Next generation model
    
    **Temperature Guidelines:**
    - `0.0-0.3`: Focused, deterministic responses
    - `0.3-0.7`: Balanced creativity and consistency
    - `0.7-1.0`: More creative and varied responses
    - `1.0-2.0`: Highly creative but potentially inconsistent
    
    Args:
        model: AI model to use (default: gpt-4o-mini)
        temperature: Model temperature 0.0-2.0 (default: 0.1)
        
    Returns:
        InitResponse: Initialization result with agent status
        
    Raises:
        HTTPException:
            - 400: No documents available
            - 500: System not initialized or agent creation failed
    """
    global rag_system
    
    if not rag_system:
        raise HTTPException(status_code=500, detail="RAG system not initialized")
    
    doc_count = rag_system.get_document_count()
    if doc_count == 0:
        raise HTTPException(status_code=400, detail="No documents available. Upload documents first.")
    
    success = rag_system.initialize_agent(model, temperature)
    
    return InitResponse(
        success=success,
        message="Agent initialized successfully" if success else "Agent initialization failed",
        agent_ready=rag_system.is_agent_ready(),
        document_count=doc_count
    )

@app.post(
    "/query",
    response_model=QueryResponse,
    tags=["Query"],
    summary="💬 Query Documents",
    description="Ask questions about uploaded documents using AI",
    responses={
        200: {
            "description": "Query processed successfully",
            "content": {
                "application/json": {
                    "example": {
                        "success": True,
                        "answer": "Based on the uploaded documents, the main topics include...",
                        "sources": ["document1.pdf", "notes.txt"],
                        "model_used": "gpt-4o-mini",
                        "processing_time": 2.34,
                        "error": None
                    }
                }
            }
        },
        400: {"description": "Agent not ready (upload documents and initialize first)"},
        500: {"description": "System not initialized or query processing error"}
    }
)
async def query_documents(
    request: QueryRequest = Body(
        ...,
        examples=[
            {
                "summary": "Simple Question",
                "description": "Ask a basic question about the documents",
                "value": {
                    "query": "What is the main topic of the uploaded documents?",
                    "model": "gpt-4o-mini",
                    "temperature": 0.1
                }
            },
            {
                "summary": "Creative Query",
                "description": "Ask for creative analysis with higher temperature",
                "value": {
                    "query": "Summarize the key insights and provide actionable recommendations",
                    "model": "gpt-4",
                    "temperature": 0.7
                }
            }
        ]
    )
):
    """💬 Ask questions about the uploaded documents using AI.
    
    **How it works:**
    1. Your question is processed by the AI agent
    2. Relevant document chunks are retrieved from the vector database
    3. The AI generates an answer based on the retrieved context
    4. Sources and metadata are returned with the response
    
    **Prerequisites:**
    - Documents must be uploaded via `/upload`
    - Agent must be initialized via `/initialize`
    
    **Query Types:**
    - **Factual Questions**: "What is mentioned about X?"
    - **Summarization**: "Summarize the main points"
    - **Analysis**: "What are the key insights?"
    - **Comparison**: "Compare X and Y from the documents"
    - **Extraction**: "List all mentions of Z"
    
    **Model Selection:**
    - Use `gpt-4o-mini` for fast, cost-effective queries
    - Use `gpt-4` for complex reasoning and analysis
    - Adjust temperature based on desired creativity level
    
    **Response Format:**
    - **Answer**: AI-generated response based on document content
    - **Sources**: List of documents that contributed to the answer
    - **Processing Time**: Time taken to process the query
    - **Model Used**: Actual model used for the query
    
    Args:
        request: Query request containing question and model parameters
        
    Returns:
        QueryResponse: Answer with sources, processing time, and metadata
        
    Raises:
        HTTPException:
            - 400: Agent not ready (upload documents and initialize first)
            - 500: System not initialized or query processing error
    """
    global rag_system
    
    start_time = datetime.now()
    
    if not rag_system:
        raise HTTPException(status_code=500, detail="RAG system not initialized")
    
    if not rag_system.is_agent_ready():
        raise HTTPException(status_code=400, detail="Agent not ready. Upload documents and initialize first.")
    
    try:
        # Update model settings if different
        rag_system.set_model(request.model, request.temperature)
        
        # Query the system
        result = rag_system.query(request.query)
        
        # Calculate processing time
        processing_time = (datetime.now() - start_time).total_seconds()
        
        # Extract sources from memory if available
        sources = []
        if rag_system.agent and hasattr(rag_system.agent, '_extract_sources_from_memory'):
            try:
                sources = rag_system.agent._extract_sources_from_memory()
            except Exception:
                sources = []
        
        return QueryResponse(
            success=result["success"],
            answer=result["answer"],
            sources=sources,
            model_used=request.model,
            processing_time=processing_time,
            error=result.get("error")
        )
        
    except Exception as e:
        processing_time = (datetime.now() - start_time).total_seconds()
        return QueryResponse(
            success=False,
            answer=f"Error processing query: {str(e)}",
            sources=[],
            model_used=request.model,
            processing_time=processing_time,
            error=str(e)
        )

@app.post(
    "/reset",
    tags=["System"],
    summary="🔄 Reset System",
    description="Reset the entire system to initial state",
    responses={
        200: {
            "description": "System reset successfully",
            "content": {
                "application/json": {
                    "example": {
                        "success": True,
                        "message": "System reset successfully"
                    }
                }
            }
        },
        500: {"description": "Error resetting system"}
    }
)
async def reset_system():
    """🔄 Reset the entire system to initial state.
    
    **This operation will:**
    - Clear all uploaded documents
    - Reset the AI agent
    - Reinitialize the vector store
    - Clear all memory and cache
    
    **Warning:** This action cannot be undone. All uploaded documents and configurations will be lost.
    
    **Use cases:**
    - Starting fresh with new documents
    - Clearing system after errors
    - Development and testing
    
    Returns:
        dict: Success message and status
        
    Raises:
        HTTPException: 500 if reset operation failed
    """
    global rag_system
    
    try:
        rag_system = AgenticRAGSystem()
        return {"success": True, "message": "System reset successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error resetting system: {str(e)}")

@app.get(
    "/models",
    tags=["System"],
    summary="🧠 Available AI Models",
    description="Get list of available AI models and default configuration",
    responses={
        200: {
            "description": "Available models retrieved successfully",
            "content": {
                "application/json": {
                    "example": {
                        "models": [
                            "gpt-3.5-turbo",
                            "gpt-4",
                            "gpt-4o-mini"
                        ],
                        "default": "gpt-4o-mini",
                        "descriptions": {
                            "gpt-3.5-turbo": "Fast and cost-effective",
                            "gpt-4": "High quality reasoning",
                            "gpt-4o-mini": "Optimized and lightweight"
                        }
                    }
                }
            }
        }
    }
)
async def get_available_models():
    """🧠 Get list of available AI models and the default model.
    
    **Model Descriptions:**
    - **gpt-3.5-turbo**: Fast, cost-effective, good for simple queries
    - **gpt-4**: High-quality reasoning, best for complex analysis
    - **gpt-4-turbo**: Enhanced GPT-4 with improved performance
    - **gpt-4o**: Optimized for various tasks and efficiency
    - **gpt-4o-mini**: Lightweight version, good balance of speed and quality
    - **gpt-5-mini**: Next generation model with advanced capabilities
    
    **Selection Guidelines:**
    - Use `gpt-4o-mini` for most general purposes (recommended)
    - Use `gpt-4` for complex reasoning and detailed analysis
    - Use `gpt-3.5-turbo` for simple queries and cost optimization
    
    Returns:
        dict: Available models list, default model, and descriptions
    """
    return {
        "models": [
            "gpt-3.5-turbo",
            "gpt-4",
            "gpt-4-turbo",
            "gpt-4o",
            "gpt-4o-mini",
            "gpt-5-mini"
        ],
        "default": "gpt-4o-mini",
        "descriptions": {
            "gpt-3.5-turbo": "Fast and cost-effective model for simple queries",
            "gpt-4": "High-quality reasoning model for complex analysis",
            "gpt-4-turbo": "Enhanced GPT-4 with improved performance and speed",
            "gpt-4o": "Optimized model for various tasks and efficiency",
            "gpt-4o-mini": "Lightweight optimized model, good balance of speed and quality",
            "gpt-5-mini": "Next generation model with advanced capabilities"
        },
        "recommendations": {
            "general_use": "gpt-4o-mini",
            "complex_analysis": "gpt-4",
            "cost_optimization": "gpt-3.5-turbo",
            "latest_features": "gpt-5-mini"
        }
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8003)
