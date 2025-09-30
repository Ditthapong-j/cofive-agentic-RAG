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
from fastapi import FastAPI, File, UploadFile, HTTPException
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
    description="API for Agentic Retrieval-Augmented Generation System",
    version="1.0.0",
    lifespan=lifespan
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

# Pydantic models
class QueryRequest(BaseModel):
    query: str = Field(..., description="The question to ask")
    model: str = Field(default="gpt-4o-mini", description="AI model to use")
    temperature: float = Field(default=0.1, ge=0.0, le=2.0, description="Model temperature")

class QueryResponse(BaseModel):
    success: bool
    answer: str
    sources: List[str] = []
    model_used: str
    processing_time: float
    error: Optional[str] = None

class SystemStatus(BaseModel):
    status: str
    document_count: int
    agent_ready: bool
    api_key_configured: bool
    version: str = "1.0.0"

class UploadResponse(BaseModel):
    success: bool
    message: str
    files_processed: int
    total_documents: int

class InitResponse(BaseModel):
    success: bool
    message: str
    agent_ready: bool
    document_count: int

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
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0"
    }

@app.get("/status", response_model=SystemStatus)
async def get_system_status():
    """Get system status"""
    global rag_system
    
    if not rag_system:
        raise HTTPException(status_code=500, detail="RAG system not initialized")
    
    return SystemStatus(
        status="ready" if rag_system.is_agent_ready() else "needs_documents",
        document_count=rag_system.get_document_count(),
        agent_ready=rag_system.is_agent_ready(),
        api_key_configured=bool(os.getenv("OPENAI_API_KEY"))
    )

@app.post("/upload", response_model=UploadResponse)
async def upload_documents(files: List[UploadFile] = File(...)):
    """Upload documents to the system"""
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

@app.post("/initialize", response_model=InitResponse)
async def initialize_agent(
    model: str = "gpt-4o-mini",
    temperature: float = 0.1
):
    """Initialize the RAG agent"""
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

@app.post("/query", response_model=QueryResponse)
async def query_documents(request: QueryRequest):
    """Query the RAG system"""
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

@app.post("/reset")
async def reset_system():
    """Reset the system"""
    global rag_system
    
    try:
        rag_system = AgenticRAGSystem()
        return {"success": True, "message": "System reset successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error resetting system: {str(e)}")

@app.get("/models")
async def get_available_models():
    """Get available AI models"""
    return {
        "models": [
            "gpt-3.5-turbo",
            "gpt-4",
            "gpt-4-turbo",
            "gpt-4o",
            "gpt-4o-mini",
            "gpt-5-mini"
        ],
        "default": "gpt-5-mini"
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8003)
