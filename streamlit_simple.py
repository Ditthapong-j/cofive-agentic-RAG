"""
Simple Streamlit App for Agentic RAG - Deployment Ready
"""
import streamlit as st
import os
import sys
from pathlib import Path
import tempfile

# Basic setup
st.set_page_config(
    page_title="🤖 Agentic RAG System",
    page_icon="🤖",
    layout="wide"
)

# Header
st.title("🤖 Agentic RAG System")
st.markdown("### AI-Powered Document Question Answering")

# Environment check
def check_environment():
    """Check if all required environment variables are set"""
    required_vars = ["OPENAI_API_KEY"]
    missing_vars = []
    
    for var in required_vars:
        value = os.getenv(var)
        if not value and hasattr(st, 'secrets') and var in st.secrets:
            value = st.secrets[var]
            os.environ[var] = value
        
        if not value:
            missing_vars.append(var)
    
    return missing_vars

# Check environment
missing_vars = check_environment()
if missing_vars:
    st.error(f"❌ Missing required environment variables: {', '.join(missing_vars)}")
    st.info("Please set these in your environment or Streamlit secrets.")
    
    with st.expander("📋 How to set environment variables"):
        st.markdown("""
        **For local development:**
        1. Create a `.env` file in your project root
        2. Add: `OPENAI_API_KEY=your_api_key_here`
        
        **For Streamlit Cloud:**
        1. Go to your app settings
        2. Add secrets in the format:
        ```
        OPENAI_API_KEY = "your_api_key_here"
        ```
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
    
    # Simple system status
    if not st.session_state.system_ready:
        if st.button("🚀 Initialize System", type="primary"):
            try:
                # Add src to path if not already there
                current_dir = Path(__file__).parent
                src_path = current_dir / "src"
                if str(src_path) not in sys.path:
                    sys.path.insert(0, str(src_path))
                
                # Try to import and initialize
                from main import AgenticRAGSystem
                
                with st.spinner("Initializing system..."):
                    rag_system = AgenticRAGSystem()
                    
                    # Check document count
                    doc_count = rag_system.get_document_count()
                    if doc_count > 0:
                        rag_system.initialize_agent()
                        st.session_state.rag_system = rag_system
                        st.session_state.system_ready = True
                        st.success(f"✅ System ready! Found {doc_count} documents.")
                    else:
                        st.warning("⚠️ No documents found. Please upload documents first.")
                        st.session_state.rag_system = rag_system
                        
            except ImportError as e:
                st.error(f"❌ Import error: {e}")
                st.info("Some modules may not be available. Please check your requirements.txt")
            except Exception as e:
                st.error(f"❌ Error: {e}")
    else:
        st.success("✅ System Ready")
        
        # Document count
        if hasattr(st.session_state, 'rag_system'):
            try:
                doc_count = st.session_state.rag_system.get_document_count()
                st.metric("Documents", doc_count)
            except:
                st.metric("Documents", "Unknown")
    
    # File upload
    st.header("📄 Upload Documents")
    uploaded_files = st.file_uploader(
        "Choose files",
        type=['pdf', 'txt', 'md'],
        accept_multiple_files=True
    )
    
    if uploaded_files and st.button("📤 Process Files"):
        if not hasattr(st.session_state, 'rag_system'):
            try:
                from main import AgenticRAGSystem
                st.session_state.rag_system = AgenticRAGSystem()
            except:
                st.error("❌ Cannot initialize system for file upload")
                st.stop()
        
        try:
            with st.spinner("Processing files..."):
                # Create temp directory
                temp_dir = tempfile.mkdtemp()
                file_paths = []
                
                # Save uploaded files
                for uploaded_file in uploaded_files:
                    temp_path = os.path.join(temp_dir, uploaded_file.name)
                    with open(temp_path, "wb") as f:
                        f.write(uploaded_file.getbuffer())
                    file_paths.append(temp_path)
                
                # Process files
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
                    st.success(f"✅ Processed {len(uploaded_files)} files!")
                    # Try to initialize agent if not ready
                    if not st.session_state.system_ready:
                        try:
                            st.session_state.rag_system.initialize_agent()
                            st.session_state.system_ready = True
                            st.success("✅ System is now ready!")
                        except Exception as e:
                            st.warning(f"⚠️ Files uploaded but agent initialization failed: {e}")
                else:
                    st.error("❌ Failed to process files")
                    
        except Exception as e:
            st.error(f"❌ Error processing files: {e}")
    
    # Clear options
    st.header("🧹 Clear")
    if st.button("🗑️ Clear Chat"):
        st.session_state.messages = []
        st.success("Chat cleared!")
    
    if st.button("💥 Reset System"):
        # Clear all session state
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.success("System reset!")
        st.rerun()

# Main chat interface
st.header("💬 Chat Interface")

# Display chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        
        # Show sources if available
        if message["role"] == "assistant" and "sources" in message:
            with st.expander("📚 Sources"):
                for source in message["sources"]:
                    st.text(f"• {source}")

# Chat input
if prompt := st.chat_input("Ask me anything about your documents..."):
    # Add user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Generate response
    with st.chat_message("assistant"):
        if st.session_state.system_ready and hasattr(st.session_state, 'rag_system'):
            try:
                with st.spinner("Thinking..."):
                    result = st.session_state.rag_system.query(prompt)
                    response = result["answer"]
                    
                    st.markdown(response)
                    
                    # Get sources
                    sources = []
                    try:
                        sources = st.session_state.rag_system.agent.get_sources_used(result)
                    except:
                        pass
                    
                    # Add to messages
                    message_data = {"role": "assistant", "content": response}
                    if sources:
                        message_data["sources"] = sources
                        with st.expander("📚 Sources"):
                            for source in sources:
                                st.text(f"• {source}")
                    
                    st.session_state.messages.append(message_data)
                    
            except Exception as e:
                error_msg = f"❌ Error: {str(e)}"
                st.markdown(error_msg)
                st.session_state.messages.append({"role": "assistant", "content": error_msg})
        else:
            fallback_msg = "🤖 I'm not fully initialized yet. Please upload some documents and initialize the system first, or I can provide general assistance with your question."
            st.markdown(fallback_msg)
            st.session_state.messages.append({"role": "assistant", "content": fallback_msg})

# Instructions
if not st.session_state.messages:
    st.info("""
    👋 **Welcome to the Agentic RAG System!**
    
    **To get started:**
    1. 📤 Upload some documents (PDF, TXT, or MD files) using the sidebar
    2. 🚀 Click "Initialize System" to prepare the AI
    3. 💬 Start asking questions about your documents!
    
    **Features:**
    - 📚 Intelligent document search and retrieval
    - 🧠 AI-powered question answering
    - 🔍 Source citations for transparency
    - 🧮 Built-in calculator for numerical questions
    """)

# Footer
st.markdown("---")
st.markdown("🤖 **Agentic RAG System** - AI-powered document analysis and question answering")
