"""
Streamlit Web Interface for Agentic RAG - Clean Production Version
"""
import streamlit as st
import os
import sys
from pathlib import Path
import tempfile

# Set page config first
st.set_page_config(
    page_title="🤖 Agentic RAG System",
    page_icon="🤖",
    layout="wide"
)

# Add src to Python path
current_dir = Path(__file__).parent
src_path = current_dir / "src"
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

def check_environment():
    """Check and setup environment variables"""
    required_vars = ["OPENAI_API_KEY"]
    missing_vars = []
    
    for var in required_vars:
        value = os.getenv(var)
        
        # Check Streamlit secrets if env var not found
        if not value and hasattr(st, 'secrets') and var in st.secrets:
            value = st.secrets[var]
            os.environ[var] = value
        
        if not value:
            missing_vars.append(var)
    
    return missing_vars

def initialize_system():
    """Initialize the RAG system"""
    try:
        # Import main system
        from main import AgenticRAGSystem
        
        with st.spinner("🚀 Initializing system..."):
            rag_system = AgenticRAGSystem()
            
            # Check if we have documents
            doc_count = rag_system.get_document_count()
            
            if doc_count > 0:
                # Initialize agent
                rag_system.initialize_agent()
                st.session_state.rag_system = rag_system
                st.session_state.system_ready = True
                st.success(f"✅ System ready! Found {doc_count} documents.")
                return True
            else:
                # Store system for file upload
                st.session_state.rag_system = rag_system
                st.warning("⚠️ No documents found. Please upload documents first.")
                return False
                
    except ImportError as e:
        st.error(f"❌ Import error: {e}")
        st.info("Some modules may not be available. Please check requirements.")
        return False
    except Exception as e:
        st.error(f"❌ System error: {e}")
        return False

def process_uploaded_files(uploaded_files):
    """Process uploaded files"""
    if not uploaded_files:
        return False
    
    try:
        with st.spinner("📤 Processing files..."):
            # Create temporary directory
            temp_dir = tempfile.mkdtemp()
            file_paths = []
            
            # Save uploaded files
            for uploaded_file in uploaded_files:
                temp_path = os.path.join(temp_dir, uploaded_file.name)
                with open(temp_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())
                file_paths.append(temp_path)
            
            # Process with RAG system
            success = st.session_state.rag_system.add_documents_from_sources(file_paths)
            
            # Cleanup
            for file_path in file_paths:
                try:
                    os.remove(file_path)
                except:
                    pass
            try:
                os.rmdir(temp_dir)
            except:
                pass
            
            if success:
                st.success(f"✅ Successfully processed {len(uploaded_files)} file(s)!")
                
                # Try to initialize agent if not ready
                if not st.session_state.get('system_ready', False):
                    try:
                        st.session_state.rag_system.initialize_agent()
                        st.session_state.system_ready = True
                        st.success("✅ System is now ready for questions!")
                    except Exception as e:
                        st.warning(f"⚠️ Files uploaded but agent init failed: {e}")
                return True
            else:
                st.error("❌ Failed to process files")
                return False
                
    except Exception as e:
        st.error(f"❌ Error processing files: {e}")
        return False

def main():
    """Main application"""
    
    # Header
    st.title("🤖 Agentic RAG System")
    st.markdown("### AI-Powered Document Question Answering")
    
    # Environment check
    missing_vars = check_environment()
    if missing_vars:
        st.error(f"❌ Missing environment variables: {', '.join(missing_vars)}")
        
        with st.expander("📋 Setup Instructions"):
            st.markdown("""
            **For Streamlit Cloud:**
            1. Go to your app settings
            2. Click on "Secrets"
            3. Add your API key:
            ```
            OPENAI_API_KEY = "your_api_key_here"
            ```
            
            **For local development:**
            1. Create a `.env` file
            2. Add: `OPENAI_API_KEY=your_api_key_here`
            """)
        st.stop()
    
    # Initialize session state
    if 'messages' not in st.session_state:
        st.session_state.messages = []
    if 'system_ready' not in st.session_state:
        st.session_state.system_ready = False
    
    # Sidebar
    with st.sidebar:
        st.header("📋 System Control")
        
        # System status and initialization
        if not st.session_state.system_ready:
            if st.button("🚀 Initialize System", type="primary"):
                initialize_system()
        else:
            st.success("✅ System Ready")
            
            # Show document count
            if hasattr(st.session_state, 'rag_system'):
                try:
                    doc_count = st.session_state.rag_system.get_document_count()
                    st.metric("Documents in Database", doc_count)
                except:
                    st.metric("Documents", "Unknown")
        
        # File upload section
        st.header("📄 Upload Documents")
        uploaded_files = st.file_uploader(
            "Choose files to upload",
            type=['pdf', 'txt', 'md'],
            accept_multiple_files=True,
            help="Upload PDF, TXT, or MD files"
        )
        
        if uploaded_files and st.button("📤 Process Files"):
            # Initialize system if needed
            if not hasattr(st.session_state, 'rag_system'):
                try:
                    from main import AgenticRAGSystem
                    st.session_state.rag_system = AgenticRAGSystem()
                except Exception as e:
                    st.error(f"❌ Cannot initialize system: {e}")
                    st.stop()
            
            process_uploaded_files(uploaded_files)
        
        # System management
        st.header("🛠️ System Management")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("🗑️ Clear Chat"):
                st.session_state.messages = []
                if hasattr(st.session_state, 'rag_system') and hasattr(st.session_state.rag_system, 'agent'):
                    try:
                        st.session_state.rag_system.agent.clear_memory()
                    except:
                        pass
                st.success("Chat cleared!")
        
        with col2:
            if st.button("🔄 Reset System"):
                # Clear session state
                for key in list(st.session_state.keys()):
                    if key != 'messages':  # Keep messages
                        del st.session_state[key]
                st.success("System reset!")
                st.rerun()
        
        # About section
        with st.expander("ℹ️ About"):
            st.markdown("""
            **Agentic RAG System** features:
            - 📚 Document upload and processing
            - 🔍 Intelligent search and retrieval
            - 🤖 AI-powered question answering
            - 📝 Source citations
            - 🧮 Built-in calculator
            """)
    
    # Main chat interface
    st.header("💬 Chat Interface")
    
    # Display chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            
            # Show sources if available
            if message["role"] == "assistant" and "sources" in message:
                with st.expander("📚 Sources Used"):
                    for i, source in enumerate(message["sources"], 1):
                        st.text(f"{i}. {source}")
    
    # Chat input
    if prompt := st.chat_input("Ask me anything about your documents..."):
        # Add user message
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Generate assistant response
        with st.chat_message("assistant"):
            if st.session_state.system_ready and hasattr(st.session_state, 'rag_system'):
                try:
                    with st.spinner("🤔 Thinking..."):
                        # Query the system
                        result = st.session_state.rag_system.query(prompt)
                        response = result.get("answer", "I couldn't generate a response.")
                        
                        st.markdown(response)
                        
                        # Try to get sources
                        sources = []
                        try:
                            if hasattr(st.session_state.rag_system, 'agent'):
                                sources = st.session_state.rag_system.agent.get_sources_used(result)
                        except:
                            pass
                        
                        # Add to message history
                        message_data = {"role": "assistant", "content": response}
                        if sources:
                            message_data["sources"] = sources
                            with st.expander("📚 Sources Used"):
                                for i, source in enumerate(sources, 1):
                                    st.text(f"{i}. {source}")
                        
                        st.session_state.messages.append(message_data)
                        
                except Exception as e:
                    error_msg = f"❌ Error processing your question: {str(e)}"
                    st.markdown(error_msg)
                    st.session_state.messages.append({"role": "assistant", "content": error_msg})
            else:
                # System not ready
                fallback_msg = """
                🤖 **System not fully ready yet!**
                
                Please:
                1. 📤 Upload some documents using the sidebar
                2. 🚀 Click "Initialize System" 
                3. 💬 Then ask your questions!
                
                I'm here to help analyze your documents and answer questions about them.
                """
                st.markdown(fallback_msg)
                st.session_state.messages.append({"role": "assistant", "content": fallback_msg})
    
    # Welcome message for new users
    if not st.session_state.messages:
        st.info("""
        👋 **Welcome to the Agentic RAG System!**
        
        **Quick Start:**
        1. 📤 **Upload Documents**: Use the sidebar to upload PDF, TXT, or MD files
        2. 🚀 **Initialize System**: Click the "Initialize System" button
        3. 💬 **Start Chatting**: Ask questions about your documents!
        
        **What I can do:**
        - Answer questions about your uploaded documents
        - Provide citations and sources for my answers
        - Perform calculations and web searches when needed
        - Remember our conversation context
        
        Try asking: *"What are the main topics in my documents?"* or *"Summarize the key points"*
        """)

if __name__ == "__main__":
    main()
