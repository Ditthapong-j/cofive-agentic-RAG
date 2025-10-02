"""
Streamlit UI for Agentic RAG System
Works both standalone and with API backend
"""
import os
import sys
import tempfile
import requests
from pathlib import Path
from typing import Optional, List

import streamlit as st

# Add src to path
sys.path.append(str(Path(__file__).parent / "src"))

# Try to import the core modules for standalone mode
try:
    from src.document_loader import DocumentLoader
    from src.vector_store import VectorStoreManager
    from src.agentic_rag import AgenticRAG
    STANDALONE_MODE = True
except ImportError:
    STANDALONE_MODE = False

# Page config
st.set_page_config(
    page_title="Agentic RAG System",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Backend client for API mode
class BackendClient:
    """Client for communicating with the FastAPI backend"""
    
    def __init__(self, base_url: str = "http://localhost:8002"):
        self.base_url = base_url
    
    def health_check(self):
        try:
            response = requests.get(f"{self.base_url}/health", timeout=5)
            return response.status_code == 200
        except:
            return False
    
    def get_status(self):
        response = requests.get(f"{self.base_url}/status")
        return response.json()
    
    def upload_files(self, files):
        files_data = []
        for file in files:
            files_data.append(('files', (file.name, file.getvalue(), 'application/octet-stream')))
        
        response = requests.post(f"{self.base_url}/upload", files=files_data)
        return response.json()
    
    def initialize_agent(self, model="gpt-3.5-turbo", temperature=0.1):
        response = requests.post(
            f"{self.base_url}/initialize",
            params={"model": model, "temperature": temperature}
        )
        return response.json()
    
    def query(self, query_text, model="gpt-3.5-turbo", temperature=0.1):
        response = requests.post(
            f"{self.base_url}/query",
            json={"query": query_text, "model": model, "temperature": temperature}
        )
        return response.json()

# Standalone system class
class StandaloneRAGSystem:
    def __init__(self):
        if not STANDALONE_MODE:
            raise ImportError("Standalone mode not available. Missing dependencies.")
        
        self.doc_loader = DocumentLoader()
        self.vector_store_manager = VectorStoreManager()
        self.agent = None
        self.vector_store_manager.load_vectorstore()
    
    def get_status(self):
        return {
            "status": "ready" if self.agent else "needs_documents",
            "document_count": self.vector_store_manager.get_document_count(),
            "agent_ready": bool(self.agent),
            "api_key_configured": bool(os.getenv("OPENAI_API_KEY"))
        }
    
    def upload_files(self, files):
        processed = 0
        total_docs_before = self.vector_store_manager.get_document_count()
        
        for file in files:
            try:
                # Save to temp file
                with tempfile.NamedTemporaryFile(delete=False, suffix=f"_{file.name}") as tmp:
                    tmp.write(file.getvalue())
                    tmp_path = tmp.name
                
                # Load documents
                file_ext = Path(file.name).suffix.lower()
                if file_ext == '.pdf':
                    docs = self.doc_loader.load_pdf(tmp_path)
                elif file_ext in ['.txt', '.md']:
                    docs = self.doc_loader.load_text(tmp_path)
                else:
                    continue
                
                if docs:
                    self.vector_store_manager.add_documents(docs)
                    processed += 1
                
                os.unlink(tmp_path)
            except Exception as e:
                st.error(f"Error processing {file.name}: {e}")
        
        total_docs_after = self.vector_store_manager.get_document_count()
        
        return {
            "success": True,
            "files_processed": processed,
            "total_documents": total_docs_after,
            "message": f"Successfully processed {processed} files"
        }
    
    def initialize_agent(self, model="gpt-3.5-turbo", temperature=0.1):
        try:
            if self.vector_store_manager.get_document_count() == 0:
                return {"success": False, "message": "No documents available"}
            
            self.agent = AgenticRAG(
                vector_store_manager=self.vector_store_manager,
                model_name=model,
                temperature=temperature
            )
            return {
                "success": True,
                "message": "Agent initialized successfully",
                "agent_ready": True,
                "document_count": self.vector_store_manager.get_document_count()
            }
        except Exception as e:
            return {"success": False, "message": f"Error: {e}"}
    
    def query(self, query_text, model="gpt-3.5-turbo", temperature=0.1):
        if not self.agent:
            return {
                "success": False,
                "answer": "Agent not initialized",
                "sources": [],
                "error": "Agent not ready"
            }
        
        try:
            result = self.agent.query(query_text)
            sources = self.agent.get_sources_used(result) if self.agent else []
            
            return {
                "success": result["success"],
                "answer": result["answer"],
                "sources": sources,
                "model_used": model,
                "processing_time": 0
            }
        except Exception as e:
            return {
                "success": False,
                "answer": f"Error: {e}",
                "sources": [],
                "error": str(e)
            }

# Initialize session state
if 'backend_client' not in st.session_state:
    st.session_state.backend_client = None
if 'standalone_system' not in st.session_state:
    st.session_state.standalone_system = None
if 'mode' not in st.session_state:
    st.session_state.mode = None
if 'messages' not in st.session_state:
    st.session_state.messages = []

# Main UI
st.title("🤖 Agentic RAG System")

# Sidebar for mode selection and configuration
with st.sidebar:
    st.header("Configuration")
    
    # Mode selection
    mode = st.radio(
        "Select Mode:",
        options=["API Mode", "Standalone Mode"],
        help="API Mode connects to a FastAPI backend. Standalone Mode runs everything locally."
    )
    
    if mode == "API Mode":
        # API configuration
        backend_url = st.text_input(
            "Backend URL:",
            value=os.getenv("BACKEND_URL", "http://localhost:8000"),
            help="URL of the FastAPI backend"
        )
        
        if st.button("Connect to Backend"):
            try:
                client = BackendClient(backend_url)
                if client.health_check():
                    st.session_state.backend_client = client
                    st.session_state.mode = "api"
                    st.success("✅ Connected to backend!")
                else:
                    st.error("❌ Cannot connect to backend")
            except Exception as e:
                st.error(f"❌ Connection error: {e}")
        
        if st.session_state.backend_client:
            try:
                status = st.session_state.backend_client.get_status()
                st.info(f"📊 Documents: {status['document_count']}")
                st.info(f"🤖 Agent: {'Ready' if status['agent_ready'] else 'Not Ready'}")
            except:
                st.error("❌ Backend connection lost")
                st.session_state.backend_client = None
    
    else:
        # Standalone mode
        if STANDALONE_MODE:
            if st.button("Initialize Standalone System"):
                try:
                    st.session_state.standalone_system = StandaloneRAGSystem()
                    st.session_state.mode = "standalone"
                    st.success("✅ Standalone system initialized!")
                except Exception as e:
                    st.error(f"❌ Initialization error: {e}")
            
            if st.session_state.standalone_system:
                try:
                    status = st.session_state.standalone_system.get_status()
                    st.info(f"📊 Documents: {status['document_count']}")
                    st.info(f"🤖 Agent: {'Ready' if status['agent_ready'] else 'Not Ready'}")
                except Exception as e:
                    st.error(f"❌ Status error: {e}")
        else:
            st.error("❌ Standalone mode not available. Missing dependencies.")
    
    # Model settings
    st.subheader("Model Settings")
    model = st.selectbox(
        "Model:",
        options=["gpt-3.5-turbo", "gpt-4", "gpt-4-turbo", "gpt-4o", "gpt-4o-mini"],
        index=4
    )
    temperature = st.slider("Temperature:", 0.0, 2.0, 0.1, 0.1)

# Main content area
if st.session_state.mode is None:
    st.info("👈 Please select and configure a mode in the sidebar to get started.")

else:
    # Get the active system
    system = (st.session_state.backend_client if st.session_state.mode == "api" 
              else st.session_state.standalone_system)
    
    if not system:
        st.error("❌ System not initialized. Please configure in the sidebar.")
    else:
        # Create tabs
        tab1, tab2, tab3 = st.tabs(["📤 Upload Documents", "🤖 Initialize Agent", "💬 Chat"])
        
        with tab1:
            st.header("Upload Documents")
            
            uploaded_files = st.file_uploader(
                "Choose files",
                accept_multiple_files=True,
                type=['pdf', 'txt', 'md'],
                help="Upload PDF, TXT, or MD files to add to the knowledge base"
            )
            
            if uploaded_files and st.button("Upload Files"):
                with st.spinner("Processing files..."):
                    try:
                        result = system.upload_files(uploaded_files)
                        if result.get("success"):
                            st.success(f"✅ {result['message']}")
                            st.info(f"📊 Total documents: {result['total_documents']}")
                        else:
                            st.error("❌ Upload failed")
                    except Exception as e:
                        st.error(f"❌ Upload error: {e}")
        
        with tab2:
            st.header("Initialize Agent")
            
            if st.button("Initialize Agent"):
                with st.spinner("Initializing agent..."):
                    try:
                        result = system.initialize_agent(model, temperature)
                        if result.get("success"):
                            st.success(f"✅ {result['message']}")
                        else:
                            st.error(f"❌ {result.get('message', 'Initialization failed')}")
                    except Exception as e:
                        st.error(f"❌ Initialization error: {e}")
        
        with tab3:
            st.header("Chat with Your Documents")
            
            # Display chat messages
            for message in st.session_state.messages:
                with st.chat_message(message["role"]):
                    st.markdown(message["content"])
                    if "sources" in message and message["sources"]:
                        with st.expander("Sources"):
                            for source in message["sources"]:
                                st.text(source)
            
            # Chat input
            if prompt := st.chat_input("Ask a question about your documents..."):
                # Add user message
                st.session_state.messages.append({"role": "user", "content": prompt})
                with st.chat_message("user"):
                    st.markdown(prompt)
                
                # Get AI response
                with st.chat_message("assistant"):
                    with st.spinner("Thinking..."):
                        try:
                            result = system.query(prompt, model, temperature)
                            
                            if result.get("success"):
                                st.markdown(result["answer"])
                                
                                # Add to session
                                st.session_state.messages.append({
                                    "role": "assistant",
                                    "content": result["answer"],
                                    "sources": result.get("sources", [])
                                })
                                
                                # Show sources
                                if result.get("sources"):
                                    with st.expander("Sources"):
                                        for source in result["sources"]:
                                            st.text(source)
                            else:
                                error_msg = result.get("answer", "Query failed")
                                st.error(f"❌ {error_msg}")
                                st.session_state.messages.append({
                                    "role": "assistant", 
                                    "content": error_msg
                                })
                        
                        except Exception as e:
                            error_msg = f"Error: {e}"
                            st.error(f"❌ {error_msg}")
                            st.session_state.messages.append({
                                "role": "assistant",
                                "content": error_msg
                            })
            
            # Clear chat button
            if st.button("Clear Chat History"):
                st.session_state.messages = []
                st.rerun()

# Footer
st.sidebar.markdown("---")
st.sidebar.markdown("🤖 **Agentic RAG System**")
st.sidebar.markdown(f"Mode: {st.session_state.mode or 'Not configured'}")
