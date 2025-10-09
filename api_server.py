"""
FastAPI Backend for Agentic RAG System
Provides REST API endpoints while preserving original functionality
"""
import os
import sys
import tempfile
import shutil
import uuid
import json
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
- 🤖 **AI Agent**: Automatically initialized when documents are uploaded
- 💬 **Query Processing**: Ask questions about uploaded documents
- 🔧 **System Management**: Health checks, status monitoring, and system reset

## 🔄 Workflow
1. **Upload Documents** → Upload your files using `/upload`
2. **Query Documents** → Ask questions with `/query` (agent auto-initializes)
3. **Manage System** → Monitor and reset using system endpoints

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
2. Upload documents via `/upload` endpoint (agent auto-initializes)
3. Start querying via `/query` endpoint
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
            "name": "Query",
            "description": "💬 Question answering and document querying",
        },
        {
            "name": "System",
            "description": "⚙️ System management, configuration, and AI instructions",
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
    tags: Optional[List[str]] = Field(
        default=None,
        description="Filter documents by tags (e.g., ['research', 'AI'])"
    )
    metadata_filter: Optional[dict] = Field(
        default=None,
        description="Filter documents by metadata (e.g., {'author': 'John', 'year': 2024})"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "query": "What are the main findings in the uploaded research papers?",
                "model": "gpt-4o-mini",
                "temperature": 0.1,
                "tags": ["research", "AI"],
                "metadata_filter": {"year": 2024, "category": "technical"}
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

class DocumentUploadRequest(BaseModel):
    """Request model for document upload with metadata"""
    tags: Optional[List[str]] = Field(
        default=None,
        description="Tags to categorize the document (e.g., ['research', 'AI', 'technical'])"
    )
    metadata: Optional[dict] = Field(
        default=None,
        description="Additional metadata for the document (e.g., {'author': 'John', 'year': 2024})"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "tags": ["research", "AI", "machine-learning"],
                "metadata": {
                    "author": "John Doe",
                    "year": 2024,
                    "category": "technical",
                    "department": "R&D"
                }
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

# Document CRUD Models
class DocumentInfo(BaseModel):
    """Document information model"""
    id: str = Field(description="Unique document identifier")
    filename: str = Field(description="Original filename")
    file_type: str = Field(description="File extension (pdf, txt, md)")
    file_size: Optional[int] = Field(default=None, description="File size in bytes")
    upload_time: str = Field(description="Upload timestamp (ISO format)")
    chunk_count: int = Field(description="Number of text chunks")
    content_preview: Optional[str] = Field(default=None, description="First 200 characters of content")
    tags: Optional[List[str]] = Field(default=None, description="Document tags")
    metadata: Optional[dict] = Field(default=None, description="Document metadata")

    class Config:
        json_schema_extra = {
            "example": {
                "id": "doc_12345678",
                "filename": "research_paper.pdf",
                "file_type": "pdf",
                "file_size": 1024000,
                "upload_time": "2025-10-02T14:30:22.123456",
                "chunk_count": 15,
                "content_preview": "This research paper discusses the implementation of...",
                "tags": ["research", "AI", "machine-learning"],
                "metadata": {"author": "John Doe", "year": 2024}
            }
        }

class DocumentListResponse(BaseModel):
    """Response model for listing documents"""
    success: bool = Field(description="Whether the request was successful")
    documents: List[DocumentInfo] = Field(description="List of document information")
    total_count: int = Field(description="Total number of documents")

    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "documents": [
                    {
                        "id": "doc_12345678",
                        "filename": "research_paper.pdf",
                        "file_type": "pdf",
                        "file_size": 1024000,
                        "upload_time": "2025-10-02T14:30:22.123456",
                        "chunk_count": 15,
                        "content_preview": "This research paper discusses..."
                    }
                ],
                "total_count": 3
            }
        }

class DocumentDeleteResponse(BaseModel):
    """Response model for document deletion"""
    success: bool = Field(description="Whether deletion was successful")
    message: str = Field(description="Deletion result message")
    deleted_document_id: str = Field(description="ID of the deleted document")
    remaining_count: int = Field(description="Number of documents remaining")

    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "message": "Document deleted successfully",
                "deleted_document_id": "doc_12345678",
                "remaining_count": 2
            }
        }

# Instruction Settings Models
class InstructionSettings(BaseModel):
    """Model for system instruction settings"""
    system_instruction: str = Field(
        default="คุณเป็น AI ที่ตอบคำถามแบบสั้นมาก ไม่เกิน 300 ตัวอักษรเด็ดขาด ห้ามใช้รายการ ห้ามใช้หัวข้อ ห้ามใช้ดาว ตอบเป็นประโยคเดียวต่อเนื่อง กระชับ ตรงประเด็น เหมาะสำหรับการฟังทางโทร",
        description="System instruction that guides AI behavior"
    )
    response_length: str = Field(
        default="short",
        description="Length of responses (short/medium/long/detailed)"
    )
    show_similarity_scores: bool = Field(
        default=True,
        description="Whether to show similarity scores for retrieved documents"
    )
    max_chunks: int = Field(
        default=5,
        ge=1,
        le=20,
        description="Maximum number of document chunks to retrieve"
    )
    similarity_threshold: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
        description="Minimum similarity score for chunk inclusion"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "system_instruction": "You are an expert research assistant. Provide detailed, accurate answers based on the documents. Always cite sources and explain your reasoning.",
                "response_length": "detailed",
                "show_similarity_scores": True,
                "max_chunks": 8,
                "similarity_threshold": 0.1
            }
        }

class InstructionSettingsResponse(BaseModel):
    """Response model for instruction settings operations"""
    success: bool = Field(description="Whether the operation was successful")
    message: str = Field(description="Operation result message")
    settings: Optional[InstructionSettings] = Field(default=None, description="Current settings")

    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "message": "Settings updated successfully",
                "settings": {
                    "system_instruction": "You are an expert research assistant...",
                    "response_length": "detailed",
                    "show_similarity_scores": True,
                    "max_chunks": 8,
                    "similarity_threshold": 0.1
                }
            }
        }

class EnhancedQueryResponse(BaseModel):
    """Enhanced response model for document queries with similarity scores"""
    success: bool = Field(description="Whether the query was processed successfully")
    answer: str = Field(description="AI-generated answer based on the documents")
    sources: List[str] = Field(default=[], description="List of source documents used")
    similarity_scores: Optional[List[dict]] = Field(default=None, description="Document chunks with similarity scores")
    model_used: str = Field(description="The AI model that was used")
    processing_time: float = Field(description="Time taken to process the query in seconds")
    chunks_retrieved: int = Field(description="Number of document chunks retrieved")
    settings_used: Optional[dict] = Field(default=None, description="Settings used for this query")
    error: Optional[str] = Field(default=None, description="Error message if query failed")

    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "answer": "Based on the uploaded documents, the main findings include...",
                "sources": ["document1.pdf", "research_notes.txt"],
                "similarity_scores": [
                    {
                        "source": "document1.pdf",
                        "content": "This section discusses the main findings...",
                        "score": 0.89
                    }
                ],
                "model_used": "gpt-4o-mini",
                "processing_time": 2.34,
                "chunks_retrieved": 5,
                "settings_used": {
                    "response_length": "medium",
                    "max_chunks": 5
                },
                "error": None
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
        
        # Document tracking
        self.uploaded_documents = {}  # document_id -> DocumentInfo
        self.document_chunks = {}     # document_id -> list of chunks
        self.document_counter = 0     # For generating unique IDs
        
        # Instruction settings
        self.settings_file = "instruction_settings.json"
        self.current_settings = self._load_settings()
        
        # Performance optimization: Cache for metadata lookups
        self._metadata_cache = {}
        
        # Try to load existing vector store
        self.vector_store_manager.load_existing_store()
    
    def _load_settings(self) -> InstructionSettings:
        """Load instruction settings from JSON file"""
        try:
            if os.path.exists(self.settings_file):
                with open(self.settings_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    return InstructionSettings(**data)
        except Exception as e:
            print(f"Error loading settings: {e}")
        
        # Return optimized default settings for speed (2-3 seconds target)
        return InstructionSettings(
            system_instruction="คุณเป็น AI ที่ตอบคำถามแบบสั้นกระชับ ตรงประเด็น อ้างอิงจากเอกสารที่มี",
            response_length="short",
            show_similarity_scores=False,
            max_chunks=3,
            similarity_threshold=0.2
        )
    
    def _save_settings(self, settings: InstructionSettings) -> bool:
        """Save instruction settings to JSON file"""
        try:
            with open(self.settings_file, 'w', encoding='utf-8') as f:
                json.dump(settings.dict(), f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"Error saving settings: {e}")
            return False
    
    def update_settings(self, settings: InstructionSettings) -> bool:
        """Update current instruction settings"""
        if self._save_settings(settings):
            self.current_settings = settings
            # Reinitialize agent if it exists to apply new settings
            if self.agent:
                self.initialize_agent(self.model_name, self.temperature)
            return True
        return False
    
    def get_settings(self) -> InstructionSettings:
        """Get current instruction settings"""
        return self.current_settings
    
    def _get_length_instruction(self, length: str) -> str:
        """Get instruction based on response length setting"""
        length_instructions = {
            "short": "คำสั่งสำคัญ: ตอบให้สั้นที่สุด ไม่เกิน 300 ตัวอักษรเด็ดขาด! ห้ามใช้รายการ ห้ามใช้เลขหัวข้อ ห้ามใช้ขีดกลาง ห้ามใช้ ** ห้ามใช้ดาว ตอบเป็นข้อความเดียวต่อเนื่อง ไม่มีการจัดรูปแบบใดๆ กระชับ ตรงประเด็น เหมาะสำหรับการฟังทางโทร นับตัวอักษรก่อนตอบ หยุดเมื่อถึง 300 ตัวอักษร STOP AT 300 CHARACTERS!",
            "medium": "Provide a balanced response with key details (2-4 paragraphs).",
            "long": "Give a comprehensive response with detailed explanations (4-6 paragraphs).",
            "detailed": "Provide an exhaustive, detailed analysis with all relevant information, examples, and thorough explanations."
        }
        return length_instructions.get(length, length_instructions["short"])
    
    def _generate_document_id(self) -> str:
        """Generate a unique document ID"""
        self.document_counter += 1
        return f"doc_{self.document_counter:08d}"
    
    def add_documents(self, documents, filename: str = None, file_size: int = None, tags: List[str] = None, metadata: dict = None):
        """Add documents to the vector store with tracking (optimized)"""
        doc_id = self._generate_document_id()
        
        # Determine file type
        file_type = "unknown"
        if filename:
            file_ext = Path(filename).suffix.lower()
            if file_ext in ['.pdf', '.txt', '.md']:
                file_type = file_ext[1:]  # Remove the dot
        
        # Prepare metadata once for all chunks (optimization)
        common_metadata = {
            'document_id': doc_id,
            'filename': filename or f"document_{doc_id}"
        }
        
        if tags:
            common_metadata['tags'] = tags
        
        if metadata:
            common_metadata.update(metadata)
        
        # Add metadata to all chunks efficiently
        for doc in documents:
            if not hasattr(doc, 'metadata') or doc.metadata is None:
                doc.metadata = {}
            doc.metadata.update(common_metadata)
        
        # Store document info
        content_preview = None
        if documents and len(documents) > 0:
            # Get preview from first document
            first_doc_content = documents[0].page_content if hasattr(documents[0], 'page_content') else str(documents[0])
            content_preview = first_doc_content[:200] + "..." if len(first_doc_content) > 200 else first_doc_content
        
        doc_info = DocumentInfo(
            id=doc_id,
            filename=filename or f"document_{doc_id}",
            file_type=file_type,
            file_size=file_size,
            upload_time=datetime.now().isoformat(),
            chunk_count=len(documents),
            content_preview=content_preview,
            tags=tags,
            metadata=metadata
        )
        
        # Store in tracking dictionaries
        self.uploaded_documents[doc_id] = doc_info
        self.document_chunks[doc_id] = documents
        
        # Cache metadata for fast lookups
        if tags or metadata:
            self._metadata_cache[doc_id] = {
                'tags': tags or [],
                'metadata': metadata or {}
            }
        
        # Add to vector store
        result = self.vector_store_manager.add_documents(documents)
        
        # Auto-initialize agent if not already initialized
        if not self.agent and self.get_document_count() > 0:
            self.initialize_agent()
        
        return result
    
    def get_documents(self) -> List[DocumentInfo]:
        """Get list of all uploaded documents"""
        return list(self.uploaded_documents.values())
    
    def get_document(self, doc_id: str) -> Optional[DocumentInfo]:
        """Get specific document by ID"""
        return self.uploaded_documents.get(doc_id)
    
    def delete_document(self, doc_id: str) -> bool:
        """Delete a specific document"""
        if doc_id not in self.uploaded_documents:
            return False
        
        try:
            # Remove from tracking
            del self.uploaded_documents[doc_id]
            if doc_id in self.document_chunks:
                del self.document_chunks[doc_id]
            
            # Note: Vector store doesn't support selective deletion
            # In a production system, you'd need to rebuild the vector store
            # For now, we just remove from our tracking
            
            return True
        except Exception as e:
            print(f"Error deleting document {doc_id}: {e}")
            return False
    
    def clear_all_documents(self) -> bool:
        """Clear all documents and reset the system"""
        try:
            self.uploaded_documents.clear()
            self.document_chunks.clear()
            self.document_counter = 0
            self.agent = None
            self._metadata_cache.clear()  # Clear cache
            
            # Reinitialize vector store
            self.vector_store_manager = VectorStoreManager(persist_directory=self.vectorstore_path)
            
            return True
        except Exception as e:
            print(f"Error clearing documents: {e}")
            return False
    
    def get_document_count(self):
        """Get document count"""
        return len(self.uploaded_documents)
    
    def initialize_agent(self, model_name: str = None, temperature: float = None):
        """Initialize the agent with current settings"""
        if self.get_document_count() == 0:
            return False
        
        self.model_name = model_name or self.model_name
        self.temperature = temperature or self.temperature
        
        try:
            # Initialize agent without system_instruction parameter
            # We'll handle instructions through the query process instead
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
    
    def query_with_similarity(self, question: str, tags: List[str] = None, metadata_filter: dict = None):
        """Query the system with similarity scores and optional filtering (optimized)"""
        if not self.agent:
            raise ValueError("Agent not initialized")
        
        # Get relevant documents with similarity scores
        try:
            # Check if vector store is initialized
            if not self.vector_store_manager.vector_store:
                return {
                    "success": False,
                    "answer": "ไม่สามารถตอบคำถามได้ เนื่องจากระบบเก็บข้อมูลยังไม่พร้อม",
                    "similarity_scores": None,
                    "chunks_retrieved": 0,
                    "settings_used": {
                        "response_length": self.current_settings.response_length,
                        "max_chunks": self.current_settings.max_chunks,
                        "similarity_threshold": self.current_settings.similarity_threshold,
                        "show_similarity_scores": self.current_settings.show_similarity_scores
                    },
                    "error": "Vector store not initialized"
                }
            
            # Optimize: Only get more docs if filtering is needed
            search_k = self.current_settings.max_chunks
            if tags or metadata_filter:
                # Get 2x docs only when filtering to ensure we have enough after filtering
                search_k = min(self.current_settings.max_chunks * 2, 20)  # Cap at 20 to prevent slowdown
            
            # Perform similarity search with optimized k
            docs_with_scores = self.vector_store_manager.vector_store.similarity_search_with_score(
                question, 
                k=search_k
            )
            
            # Fast filtering by tags and metadata if provided
            if tags or metadata_filter:
                filtered_docs = []
                for doc, score in docs_with_scores:
                    # Early threshold check for speed
                    if score < self.current_settings.similarity_threshold:
                        continue
                    
                    doc_metadata = getattr(doc, 'metadata', {})
                    
                    # Check tags (fast OR check)
                    if tags:
                        doc_tags = doc_metadata.get('tags', [])
                        if not doc_tags or not any(tag in doc_tags for tag in tags):
                            continue
                    
                    # Check metadata filter (fast AND check)
                    if metadata_filter:
                        if not all(doc_metadata.get(k) == v for k, v in metadata_filter.items()):
                            continue
                    
                    filtered_docs.append((doc, score))
                    
                    # Stop early if we have enough results
                    if len(filtered_docs) >= self.current_settings.max_chunks:
                        break
                
                docs_with_scores = filtered_docs
            else:
                # No filtering - just apply threshold
                docs_with_scores = [
                    (doc, score) for doc, score in docs_with_scores 
                    if score >= self.current_settings.similarity_threshold
                ][:self.current_settings.max_chunks]
            
            filtered_docs = docs_with_scores
            
            # Check if we have relevant documents
            if len(filtered_docs) == 0:
                return {
                    "success": False,
                    "answer": "ไม่สามารถตอบคำถามได้ เนื่องจากไม่พบข้อมูลที่เกี่ยวข้องในเอกสาร",
                    "similarity_scores": None,
                    "chunks_retrieved": 0,
                    "settings_used": {
                        "response_length": self.current_settings.response_length,
                        "max_chunks": self.current_settings.max_chunks,
                        "similarity_threshold": self.current_settings.similarity_threshold,
                        "show_similarity_scores": self.current_settings.show_similarity_scores
                    },
                    "error": "No relevant documents found above similarity threshold"
                }
            
            # Prepare similarity information (optimized)
            similarity_info = []
            if self.current_settings.show_similarity_scores:
                for doc, score in filtered_docs:
                    doc_metadata = getattr(doc, 'metadata', {})
                    
                    # Extract info efficiently
                    source = doc_metadata.get('filename') or doc_metadata.get('source', 'Unknown')
                    doc_tags = doc_metadata.get('tags')
                    
                    # Extract custom metadata (exclude system fields) - optimized
                    system_fields = {'source', 'filename', 'document_id', 'tags'}
                    doc_metadata_filtered = {k: v for k, v in doc_metadata.items() if k not in system_fields} if doc_metadata else None
                    
                    similarity_info.append({
                        "source": source,
                        "content": doc.page_content[:150] + "..." if len(doc.page_content) > 150 else doc.page_content,
                        "score": round(float(score), 3),
                        "tags": doc_tags,
                        "metadata": doc_metadata_filtered if doc_metadata_filtered else None
                    })
            
            # Create enhanced question with instructions
            enhanced_question = f"""CRITICAL INSTRUCTION - MUST FOLLOW EXACTLY:
{self.current_settings.system_instruction}

STRICT LENGTH REQUIREMENT - THIS IS MANDATORY:
{self._get_length_instruction(self.current_settings.response_length)}

RULES YOU MUST FOLLOW:
- If response_length is "short": MAXIMUM 300 characters, NO EXCEPTIONS
- NO bullet points, NO numbered lists, NO formatting
- Write as one continuous paragraph only
- Count characters before responding
- Stop writing when you reach the limit

IMPORTANT: Always base your answers on the provided document context and cite your sources clearly.

User Question: {question}"""
            
            # Query the agent with enhanced question
            result = self.agent.query(enhanced_question)
            
            # Post-process answer for length control
            if self.current_settings.response_length == "short":
                # Enforce strict length limit for short responses
                original_answer = result["answer"]
                if len(original_answer) > 300:
                    # Cut at word boundary near 300 characters
                    truncated = original_answer[:300]
                    last_space = truncated.rfind(' ')
                    if last_space > 250:  # Only cut at space if it's not too early
                        result["answer"] = truncated[:last_space] + "..."
                    else:
                        result["answer"] = truncated[:297] + "..."
            
            # Add similarity information to result
            result["similarity_scores"] = similarity_info if self.current_settings.show_similarity_scores else None
            result["chunks_retrieved"] = len(filtered_docs)
            result["settings_used"] = {
                "response_length": self.current_settings.response_length,
                "max_chunks": self.current_settings.max_chunks,
                "similarity_threshold": self.current_settings.similarity_threshold,
                "show_similarity_scores": self.current_settings.show_similarity_scores
            }
            
            return result
            
        except Exception as e:
            # Don't answer when similarity search fails
            import traceback
            traceback.print_exc()
            
            # Check if we have any documents at all
            if self.get_document_count() == 0:
                return {
                    "success": False,
                    "answer": "ไม่สามารถตอบคำถามได้ เนื่องจากไม่มีเอกสารในระบบ กรุณาอัพโหลดเอกสารก่อน",
                    "similarity_scores": None,
                    "chunks_retrieved": 0,
                    "settings_used": {
                        "response_length": self.current_settings.response_length,
                        "max_chunks": self.current_settings.max_chunks,
                        "similarity_threshold": self.current_settings.similarity_threshold,
                        "show_similarity_scores": self.current_settings.show_similarity_scores
                    },
                    "error": "No documents available in system"
                }
            
            # For other errors, don't answer
            return {
                "success": False,
                "answer": "ไม่สามารถตอบคำถามได้ เนื่องจากเกิดข้อผิดพลาดในการค้นหาข้อมูล",
                "similarity_scores": None,
                "chunks_retrieved": 0,
                "settings_used": {
                    "response_length": self.current_settings.response_length,
                    "max_chunks": self.current_settings.max_chunks,
                    "similarity_threshold": self.current_settings.similarity_threshold,
                    "show_similarity_scores": self.current_settings.show_similarity_scores
                },
                "error": f"Search system error: {str(e)}"
            }
    
    def query(self, question: str, tags: List[str] = None, metadata_filter: dict = None):
        """Legacy query method for backward compatibility"""
        return self.query_with_similarity(question, tags=tags, metadata_filter=metadata_filter)
    
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
    description="Upload one or more documents to the system for processing with optional tags and metadata",
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
    ),
    tags: Optional[str] = Query(
        default=None,
        description="Comma-separated tags (e.g., 'research,AI,technical')"
    ),
    metadata: Optional[str] = Query(
        default=None,
        description="JSON string of metadata (e.g., '{\"author\":\"John\",\"year\":2024}')"
    )
):
    """📤 Upload one or more documents to the system with optional tags and metadata.
    
    **Supported file types:**
    - 📄 **PDF** (.pdf) - Portable Document Format
    - 📝 **Text** (.txt) - Plain text files
    - 📋 **Markdown** (.md) - Markdown formatted text
    
    **Tags and Metadata:**
    - **Tags**: Categories for easy filtering (e.g., 'research', 'AI', 'technical')
    - **Metadata**: Additional information (e.g., author, year, department, category)
    - Both are optional but recommended for better organization and filtering
    
    **Process:**
    1. Files are validated for supported formats
    2. Content is extracted and processed
    3. Documents are split into chunks
    4. Tags and metadata are attached to each chunk
    5. Chunks are embedded and stored in vector database
    
    **Features:**
    - Multiple file upload support
    - Automatic content extraction
    - Smart text chunking
    - Vector embedding generation
    - Tag and metadata support for filtering
    
    **Example Usage:**
    ```
    curl -X POST "http://localhost:8003/upload?tags=research,AI&metadata={\"author\":\"John\",\"year\":2024}" \
         -F "files=@paper1.pdf" \
         -F "files=@paper2.pdf"
    ```
    
    Args:
        files: List of files to upload (multipart/form-data)
        tags: Comma-separated tags (optional)
        metadata: JSON string of metadata (optional)
        
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
    
    # Parse tags
    tags_list = None
    if tags:
        tags_list = [tag.strip() for tag in tags.split(',') if tag.strip()]
    
    # Parse metadata
    metadata_dict = None
    if metadata:
        try:
            metadata_dict = json.loads(metadata)
        except json.JSONDecodeError:
            raise HTTPException(status_code=400, detail="Invalid metadata JSON format")
    
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
                rag_system.add_documents(
                    documents, 
                    filename=file.filename, 
                    file_size=file.size,
                    tags=tags_list,
                    metadata=metadata_dict
                )
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
    "/query",
    response_model=EnhancedQueryResponse,
    tags=["Query"],
    summary="💬 Query Documents",
    description="Ask questions about uploaded documents using AI with enhanced features including tag and metadata filtering",
    responses={
        200: {
            "description": "Query processed successfully",
            "content": {
                "application/json": {
                    "example": {
                        "success": True,
                        "answer": "Based on the uploaded documents, the main topics include...",
                        "sources": ["document1.pdf", "notes.txt"],
                        "similarity_scores": [
                            {
                                "source": "document1.pdf",
                                "content": "This section discusses...",
                                "score": 0.89,
                                "tags": ["research", "AI"],
                                "metadata": {"author": "John", "year": 2024}
                            }
                        ],
                        "model_used": "gpt-4o-mini",
                        "processing_time": 2.34,
                        "chunks_retrieved": 5,
                        "settings_used": {
                            "response_length": "medium",
                            "max_chunks": 5
                        },
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
                "summary": "Filtered by Tags",
                "description": "Ask a question and filter by specific tags",
                "value": {
                    "query": "What are the key findings in AI research?",
                    "model": "gpt-4o-mini",
                    "temperature": 0.1,
                    "tags": ["research", "AI"],
                    "metadata_filter": None
                }
            },
            {
                "summary": "Filtered by Metadata",
                "description": "Ask a question and filter by metadata",
                "value": {
                    "query": "What did John write about?",
                    "model": "gpt-4o-mini",
                    "temperature": 0.1,
                    "tags": None,
                    "metadata_filter": {"author": "John", "year": 2024}
                }
            },
            {
                "summary": "Creative Query with Filters",
                "description": "Ask for creative analysis with filtering",
                "value": {
                    "query": "Summarize the key insights and provide recommendations",
                    "model": "gpt-4",
                    "temperature": 0.7,
                    "tags": ["technical"],
                    "metadata_filter": {"department": "R&D"}
                }
            }
        ]
    )
):
    """💬 Ask questions about the uploaded documents using AI with enhanced features.
    
    **Enhanced Features:**
    - **Tag Filtering**: Search only within documents with specific tags
    - **Metadata Filtering**: Search only within documents matching metadata criteria
    - **Similarity Scores**: See how closely retrieved chunks match your query
    - **Custom Instructions**: Responses follow your configured system instructions
    - **Response Length Control**: Get answers in your preferred length (short/medium/long/detailed)
    - **Chunk Filtering**: Control how many document chunks are used
    
    **How it works:**
    1. Your question is processed by the AI agent
    2. Documents are filtered by tags and/or metadata (if specified)
    3. Relevant document chunks are retrieved based on similarity
    4. Similarity scores show how well chunks match your query
    5. AI generates an answer using your configured instructions
    6. Response length is controlled by your settings
    
    **Filtering Options:**
    - **Tags**: Filter documents by one or more tags (e.g., ["research", "AI"])
    - **Metadata**: Filter documents by metadata key-value pairs (e.g., {"author": "John", "year": 2024})
    - **Combined**: Use both tags and metadata for precise filtering
    
    **Prerequisites:**
    - Documents must be uploaded via `/upload`
    - Agent will be automatically initialized when documents are uploaded
    - Optional: Configure instructions via `/settings/instructions`
    
    **Query Types:**
    - **Factual Questions**: "What is mentioned about X?"
    - **Summarization**: "Summarize the main points"
    - **Analysis**: "What are the key insights?"
    - **Comparison**: "Compare X and Y from the documents"
    - **Extraction**: "List all mentions of Z"
    - **Filtered Queries**: "What did [author] write about [topic]?"
    
    **Response Components:**
    - **Answer**: AI-generated response based on document content
    - **Sources**: List of documents that contributed to the answer
    - **Similarity Scores**: How well each chunk matches your query (if enabled)
    - **Tags & Metadata**: Tags and metadata of retrieved chunks (if show_similarity_scores is enabled)
    - **Processing Time**: Time taken to process the query
    - **Chunks Retrieved**: Number of document chunks used
    - **Settings Used**: Configuration applied to this query
    
    **Example with Filtering:**
    ```json
    {
      "query": "What are the main findings?",
      "model": "gpt-4o-mini",
      "temperature": 0.1,
      "tags": ["research", "AI"],
      "metadata_filter": {"year": 2024, "category": "technical"}
    }
    ```
    
    Args:
        request: Query request containing question, model parameters, and optional filters
        
    Returns:
        EnhancedQueryResponse: Answer with sources, similarity scores, tags, metadata, and filtering info
        
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
        raise HTTPException(status_code=400, detail="Agent not ready. Upload documents first.")
    
    try:
        # Update model settings if different
        rag_system.set_model(request.model, request.temperature)
        
        # Query the system with similarity scores and filters
        result = rag_system.query_with_similarity(
            request.query,
            tags=request.tags,
            metadata_filter=request.metadata_filter
        )
        
        # Calculate processing time
        processing_time = (datetime.now() - start_time).total_seconds()
        
        # Extract sources from memory if available
        sources = []
        if rag_system.agent and hasattr(rag_system.agent, '_extract_sources_from_memory'):
            try:
                sources = rag_system.agent._extract_sources_from_memory()
            except Exception:
                sources = []
        
        return EnhancedQueryResponse(
            success=result["success"],
            answer=result["answer"],
            sources=sources,
            similarity_scores=result.get("similarity_scores"),
            model_used=request.model,
            processing_time=processing_time,
            chunks_retrieved=result.get("chunks_retrieved", 0),
            settings_used=result.get("settings_used"),
            error=result.get("error")
        )
        
    except Exception as e:
        processing_time = (datetime.now() - start_time).total_seconds()
        return EnhancedQueryResponse(
            success=False,
            answer=f"Error processing query: {str(e)}",
            sources=[],
            similarity_scores=None,
            model_used=request.model,
            processing_time=processing_time,
            chunks_retrieved=0,
            settings_used=None,
            error=str(e)
        )

# Document CRUD endpoints
@app.get(
    "/documents",
    response_model=DocumentListResponse,
    tags=["Documents"],
    summary="📋 List All Documents",
    description="Get a list of all uploaded documents with metadata",
    responses={
        200: {
            "description": "Documents retrieved successfully",
            "content": {
                "application/json": {
                    "example": {
                        "success": True,
                        "documents": [
                            {
                                "id": "doc_00000001",
                                "filename": "research_paper.pdf",
                                "file_type": "pdf",
                                "file_size": 1024000,
                                "upload_time": "2025-10-02T14:30:22.123456",
                                "chunk_count": 15,
                                "content_preview": "This research paper discusses..."
                            }
                        ],
                        "total_count": 3
                    }
                }
            }
        },
        500: {"description": "RAG system not initialized"}
    }
)
async def list_documents():
    """📋 Get a list of all uploaded documents with metadata.
    
    Returns detailed information about each document including:
    - **Document ID**: Unique identifier for the document
    - **Filename**: Original filename when uploaded
    - **File Type**: Type of file (pdf, txt, md)
    - **File Size**: Size in bytes (if available)
    - **Upload Time**: Timestamp when document was uploaded
    - **Chunk Count**: Number of text chunks the document was split into
    - **Content Preview**: First 200 characters of the document content
    
    **Use Cases:**
    - View all uploaded documents
    - Get document metadata for management
    - Check upload status and processing results
    - Monitor document collection size
    
    Returns:
        DocumentListResponse: List of documents with metadata and total count
        
    Raises:
        HTTPException: 500 if RAG system not initialized
    """
    global rag_system
    
    if not rag_system:
        raise HTTPException(status_code=500, detail="RAG system not initialized")
    
    documents = rag_system.get_documents()
    
    return DocumentListResponse(
        success=True,
        documents=documents,
        total_count=len(documents)
    )

@app.get(
    "/documents/{doc_id}",
    response_model=DocumentInfo,
    tags=["Documents"],
    summary="📄 Get Document Details",
    description="Get detailed information about a specific document",
    responses={
        200: {
            "description": "Document details retrieved successfully",
            "content": {
                "application/json": {
                    "example": {
                        "id": "doc_00000001",
                        "filename": "research_paper.pdf",
                        "file_type": "pdf",
                        "file_size": 1024000,
                        "upload_time": "2025-10-02T14:30:22.123456",
                        "chunk_count": 15,
                        "content_preview": "This research paper discusses the implementation..."
                    }
                }
            }
        },
        404: {"description": "Document not found"},
        500: {"description": "RAG system not initialized"}
    }
)
async def get_document(doc_id: str):
    """📄 Get detailed information about a specific document.
    
    Retrieve comprehensive metadata for a single document including:
    - **Processing Details**: How the document was chunked and processed
    - **Content Information**: Preview of document content
    - **Upload Metadata**: When and how the document was uploaded
    - **System Integration**: How it fits into the RAG system
    
    **Use Cases:**
    - View detailed document information
    - Verify document processing results
    - Debug document-related issues
    - Get content preview before querying
    
    Args:
        doc_id: Unique document identifier (e.g., "doc_00000001")
        
    Returns:
        DocumentInfo: Complete document metadata and information
        
    Raises:
        HTTPException:
            - 404: Document not found with the specified ID
            - 500: RAG system not initialized
    """
    global rag_system
    
    if not rag_system:
        raise HTTPException(status_code=500, detail="RAG system not initialized")
    
    document = rag_system.get_document(doc_id)
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    return document

@app.delete(
    "/documents/{doc_id}",
    response_model=DocumentDeleteResponse,
    tags=["Documents"],
    summary="🗑️ Delete Document",
    description="Delete a specific document from the system",
    responses={
        200: {
            "description": "Document deleted successfully",
            "content": {
                "application/json": {
                    "example": {
                        "success": True,
                        "message": "Document deleted successfully",
                        "deleted_document_id": "doc_00000001",
                        "remaining_count": 2
                    }
                }
            }
        },
        404: {"description": "Document not found"},
        500: {"description": "RAG system not initialized or deletion failed"}
    }
)
async def delete_document(doc_id: str):
    """🗑️ Delete a specific document from the system.
    
    **This operation will:**
    - Remove the document from the tracking system
    - Clear associated text chunks from memory
    - Update document count and statistics
    - Reset the AI agent if this was the last document
    
    **Important Notes:**
    - The vector embeddings remain in the vector store (limitation of current implementation)
    - If this is the last document, the AI agent will be reset
    - This action cannot be undone
    
    **Use Cases:**
    - Remove outdated or incorrect documents
    - Clean up test uploads
    - Manage document collection size
    - Remove sensitive content
    
    Args:
        doc_id: Unique document identifier to delete
        
    Returns:
        DocumentDeleteResponse: Deletion result with remaining document count
        
    Raises:
        HTTPException:
            - 404: Document not found with the specified ID
            - 500: RAG system not initialized or deletion operation failed
    """
    global rag_system
    
    if not rag_system:
        raise HTTPException(status_code=500, detail="RAG system not initialized")
    
    # Check if document exists
    if not rag_system.get_document(doc_id):
        raise HTTPException(status_code=404, detail="Document not found")
    
    success = rag_system.delete_document(doc_id)
    
    if success:
        # Reset agent if no documents remain
        if rag_system.get_document_count() == 0:
            rag_system.agent = None
        
        return DocumentDeleteResponse(
            success=True,
            message="Document deleted successfully",
            deleted_document_id=doc_id,
            remaining_count=len(rag_system.get_documents())
        )
    else:
        raise HTTPException(status_code=500, detail="Failed to delete document")

@app.delete(
    "/documents",
    tags=["Documents"],
    summary="🗑️ Delete All Documents",
    description="Delete all documents from the system",
    responses={
        200: {
            "description": "All documents deleted successfully",
            "content": {
                "application/json": {
                    "example": {
                        "success": True,
                        "message": "All documents deleted successfully",
                        "deleted_count": 5
                    }
                }
            }
        },
        500: {"description": "RAG system not initialized or deletion failed"}
    }
)
async def delete_all_documents():
    """🗑️ Delete all documents from the system.
    
    **This operation will:**
    - Remove all uploaded documents and their metadata
    - Clear all text chunks from memory
    - Reset the vector store completely
    - Reset the AI agent
    - Clear all system memory and cache
    
    **Warning:** This action cannot be undone. All uploaded documents and their processing results will be permanently lost.
    
    **Use Cases:**
    - Start fresh with a new document collection
    - Clear system for new projects
    - Reset system after errors or issues
    - Development and testing cleanup
    
    **System Impact:**
    - Document count will be reset to 0
    - Agent will need to be reinitialized after new uploads
    - All queries will fail until new documents are uploaded
    
    Returns:
        dict: Success message with count of deleted documents
        
    Raises:
        HTTPException:
            - 500: RAG system not initialized or deletion operation failed
    """
    global rag_system
    
    if not rag_system:
        raise HTTPException(status_code=500, detail="RAG system not initialized")
    
    # Get count before deletion
    deleted_count = rag_system.get_document_count()
    
    success = rag_system.clear_all_documents()
    
    if success:
        return {
            "success": True, 
            "message": "All documents deleted successfully",
            "deleted_count": deleted_count
        }
    else:
        raise HTTPException(status_code=500, detail="Failed to delete all documents")

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

# Instruction Settings endpoints
@app.post(
    "/settings/instructions",
    response_model=InstructionSettingsResponse,
    tags=["System"],
    summary="⚙️ Set AI Instructions",
    description="Configure AI behavior, response length, and similarity settings",
    responses={
        200: {
            "description": "Settings updated successfully",
            "content": {
                "application/json": {
                    "example": {
                        "success": True,
                        "message": "Settings updated successfully",
                        "settings": {
                            "system_instruction": "You are an expert research assistant...",
                            "response_length": "detailed",
                            "show_similarity_scores": True,
                            "max_chunks": 8,
                            "similarity_threshold": 0.1
                        }
                    }
                }
            }
        },
        500: {"description": "Error updating settings"}
    }
)
async def set_instruction_settings(
    settings: InstructionSettings = Body(
        ...,
        examples=[
            {
                "summary": "Research Assistant",
                "description": "Configure as a research assistant with detailed responses",
                "value": {
                    "system_instruction": "You are an expert research assistant. Provide detailed, accurate answers based on the documents. Always cite sources and explain your reasoning step by step.",
                    "response_length": "detailed",
                    "show_similarity_scores": True,
                    "max_chunks": 8,
                    "similarity_threshold": 0.1
                }
            },
            {
                "summary": "Quick Summarizer for Phone Calls",
                "description": "Configure for very short responses (300 characters max) suitable for phone conversations",
                "value": {
                    "system_instruction": "คุณเป็น AI ที่ตอบคำถามแบบสั้นมาก ไม่เกิน 300 ตัวอักษรเด็ดขาด ห้ามใช้รายการ ห้ามใช้หัวข้อ ห้ามใช้ดาว ตอบเป็นประโยคเดียวต่อเนื่อง กระชับ ตรงประเด็น",
                    "response_length": "short",
                    "show_similarity_scores": False,
                    "max_chunks": 2,
                    "similarity_threshold": 0.3
                }
            }
        ]
    )
):
    """⚙️ Configure AI behavior, response length, and similarity settings.
    
    **System Instructions:**
    Set how the AI should behave and respond to queries. This affects:
    - Response tone and style
    - Level of detail and explanation
    - How sources are cited
    - Overall AI personality
    
    **Response Length Options:**
    - **short**: ประโยคสั้น กระชับ 300 ตัวอักษร เหมาะสำหรับการฟังระหว่างโทร
    - **medium**: Balanced response, 2-4 paragraphs
    - **long**: Comprehensive response, 4-6 paragraphs
    - **detailed**: Exhaustive analysis with all relevant information
    
    **Similarity Settings:**
    - **show_similarity_scores**: Display how well chunks match queries
    - **max_chunks**: Maximum document chunks to retrieve (1-20)
    - **similarity_threshold**: Minimum similarity score (0.0-1.0)
    
    **Configuration Persistence:**
    - Settings are saved to `instruction_settings.json`
    - Persists across server restarts
    - Applied to all future queries until changed
    - Automatically reapplied when agent is reinitialized
    
    **Use Cases:**
    - Academic research (detailed, citing sources)
    - Business analysis (professional, action-oriented)
    - Quick Q&A (concise, direct answers)
    - Educational content (explanatory, step-by-step)
    
    Args:
        settings: New instruction settings configuration
        
    Returns:
        InstructionSettingsResponse: Success status and updated settings
        
    Raises:
        HTTPException:
            - 500: Error saving settings or system not initialized
    """
    global rag_system
    
    if not rag_system:
        raise HTTPException(status_code=500, detail="RAG system not initialized")
    
    try:
        success = rag_system.update_settings(settings)
        
        if success:
            return InstructionSettingsResponse(
                success=True,
                message="Settings updated successfully. Changes will apply to future queries.",
                settings=settings
            )
        else:
            raise HTTPException(status_code=500, detail="Failed to save settings")
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating settings: {str(e)}")

@app.get(
    "/settings/instructions",
    response_model=InstructionSettingsResponse,
    tags=["System"],
    summary="👁️ Get AI Instructions",
    description="View current AI behavior and similarity settings",
    responses={
        200: {
            "description": "Settings retrieved successfully",
            "content": {
                "application/json": {
                    "example": {
                        "success": True,
                        "message": "Current settings retrieved",
                        "settings": {
                            "system_instruction": "You are a helpful AI assistant...",
                            "response_length": "medium",
                            "show_similarity_scores": True,
                            "max_chunks": 5,
                            "similarity_threshold": 0.0
                        }
                    }
                }
            }
        },
        500: {"description": "Error retrieving settings"}
    }
)
async def get_instruction_settings():
    """👁️ View current AI behavior and similarity settings.
    
    **Returns Current Configuration:**
    - **System Instruction**: How AI is configured to behave
    - **Response Length**: Length setting for responses
    - **Similarity Display**: Whether similarity scores are shown
    - **Chunk Limits**: Maximum chunks and similarity threshold
    
    **Configuration Sources:**
    - Loaded from `instruction_settings.json` if exists
    - Default values if no custom configuration
    - Real-time settings currently in use
    
    **Use Cases:**
    - Verify current AI configuration
    - Check response length settings
    - Review similarity search parameters
    - Audit system behavior settings
    - Debug query behavior issues
    
    **Response Information:**
    - Current system instruction text
    - Response length preference
    - Similarity score display preference
    - Document retrieval limits
    - Similarity filtering threshold
    
    Returns:
        InstructionSettingsResponse: Current settings and status
        
    Raises:
        HTTPException:
            - 500: Error retrieving settings or system not initialized
    """
    global rag_system
    
    if not rag_system:
        raise HTTPException(status_code=500, detail="RAG system not initialized")
    
    try:
        current_settings = rag_system.get_settings()
        
        return InstructionSettingsResponse(
            success=True,
            message="Current settings retrieved successfully",
            settings=current_settings
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving settings: {str(e)}")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8003)
