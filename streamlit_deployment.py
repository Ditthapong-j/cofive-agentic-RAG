"""
Streamlit Web Interface for Agentic RAG - Deployment Version
"""
import sys
import os
import streamlit as st
from pathlib import Path
import tempfile

# Add src to path
current_dir = Path(__file__).parent
src_path = current_dir / "src"
sys.path.insert(0, str(src_path))

# Import with error handling
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# Environment variables handling
def get_env_var(key, default=None):
    """Get environment variable with fallback to Streamlit secrets"""
    # Try environment variable first
    value = os.getenv(key, default)
    # Try Streamlit secrets if env var not found
    if value is None and hasattr(st, 'secrets') and key in st.secrets:
        value = st.secrets[key]
    return value

# Check for OpenAI API key
openai_api_key = get_env_var("OPENAI_API_KEY")
if not openai_api_key:
    st.error("⚠️ OPENAI_API_KEY not found!")
    st.info("""
    Please set your OpenAI API key in one of these ways:
    - Environment variable: OPENAI_API_KEY
    - Streamlit secrets: Add to .streamlit/secrets.toml
    - For Streamlit Cloud: Add in App settings > Secrets
    """)
    st.stop()

# Set environment variable for OpenAI
os.environ["OPENAI_API_KEY"] = openai_api_key

# Import modules with fallback
try:
    from main import AgenticRAGSystem
except ImportError:
    try:
        # Fallback imports
        from vector_store import VectorStoreManager
        from document_loader import DocumentLoader
        from agentic_rag import AgenticRAG
        
        # Simple AgenticRAGSystem class for compatibility
        class AgenticRAGSystem:
            def __init__(self):
                self.vector_manager = VectorStoreManager()
                self.doc_loader = DocumentLoader()
                self.agent = None
                
            def get_document_count(self):
                return self.vector_manager.get_document_count() if self.vector_manager.vectorstore else 0
                
            def initialize_agent(self):
                if self.get_document_count() > 0:
                    self.agent = AgenticRAG(
                        vector_store_manager=self.vector_manager,
                        temperature=0.1,
                        verbose=True
                    )
                    return True
                return False
                
            def query(self, question):
                if self.agent:
                    result = self.agent.query(question)
                    return result.get('output', result.get('answer', str(result)))
                return "Agent not initialized. Please add documents first."
                
            def add_documents_from_sources(self, sources):
                try:
                    documents = []
                    for source in sources:
                        if os.path.isfile(source):
                            docs = self.doc_loader.load_documents(source)
                            documents.extend(docs)
                        elif os.path.isdir(source):
                            docs = self.doc_loader.load_documents(source)
                            documents.extend(docs)
                    
                    if documents:
                        if self.vector_manager.vectorstore is None:
                            self.vector_manager.create_vectorstore(documents)
                        else:
                            self.vector_manager.add_documents(documents)
                        return True
                    return False
                except Exception as e:
                    print(f"Error adding documents: {e}")
                    return False
                    
            def clear_vectorstore(self):
                if self.vector_manager:
                    self.vector_manager.clear_vectorstore()
                    self.agent = None
    except ImportError as e:
        st.error(f"Failed to import required modules: {e}")
        st.info("Please ensure all required files are present in the src directory.")
        st.stop()

# Page configuration
st.set_page_config(
    page_title="🤖 Agentic RAG System",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
        font-weight: bold;
    }
    .chat-message {
        padding: 1rem;
        border-radius: 0.8rem;
        margin-bottom: 1rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .user-message {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        margin-left: 10%;
    }
    .agent-message {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        color: white;
        margin-right: 10%;
    }
    .stButton > button {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 20px;
        padding: 0.5rem 1rem;
        font-weight: bold;
    }
    .sidebar-section {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 10px;
        margin-bottom: 1rem;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
def initialize_session_state():
    """Initialize all session state variables"""
    defaults = {
        'rag_system': None,
        'chat_history': [],
        'system_initialized': False,
        'response_style': 'balanced',
        'output_language': 'auto',
        'response_length': 'medium',
        'include_sources': True,
        'include_examples': False,
        'step_by_step': False
    }
    
    for key, default_value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = default_value

def initialize_system():
    """Initialize the RAG system"""
    try:
        with st.spinner("🔄 Initializing RAG system..."):
            # Initialize RAG system
            st.session_state.rag_system = AgenticRAGSystem()
            
            # Load default documents if available
            data_path = current_dir / "data"
            if data_path.exists() and any(data_path.iterdir()):
                st.session_state.rag_system.add_documents_from_sources([str(data_path)])
                doc_count = st.session_state.rag_system.get_document_count()
                if doc_count > 0:
                    st.success(f"✅ Loaded {doc_count} documents")
                    # Initialize agent
                    if st.session_state.rag_system.initialize_agent():
                        st.session_state.system_initialized = True
                        st.success("🤖 Agent initialized successfully!")
                        return True
                    else:
                        st.warning("⚠️ Failed to initialize agent")
                else:
                    st.warning("⚠️ No documents loaded")
            else:
                st.info("📁 No documents found. Please upload documents to start.")
                st.session_state.rag_system = AgenticRAGSystem()
                return True
            
    except Exception as e:
        st.error(f"❌ Failed to initialize system: {str(e)}")
        return False

def process_uploaded_files(uploaded_files):
    """Process uploaded files"""
    if not uploaded_files:
        return False
    
    try:
        with st.spinner("📤 Processing uploaded files..."):
            # Create temporary directory
            temp_dir = tempfile.mkdtemp()
            file_paths = []
            
            for uploaded_file in uploaded_files:
                # Save uploaded file
                temp_path = os.path.join(temp_dir, uploaded_file.name)
                with open(temp_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())
                file_paths.append(temp_path)
            
            # Add documents to system
            if st.session_state.rag_system is None:
                st.session_state.rag_system = AgenticRAGSystem()
            
            success = st.session_state.rag_system.add_documents_from_sources(file_paths)
            
            # Clean up
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
                # Try to initialize agent
                if st.session_state.rag_system.initialize_agent():
                    st.session_state.system_initialized = True
                return True
            else:
                st.error("❌ Failed to process files")
                return False
                
    except Exception as e:
        st.error(f"❌ Error processing files: {str(e)}")
        return False

def create_enhanced_prompt(query, settings):
    """Create enhanced prompt based on user settings"""
    
    style_prompts = {
        'balanced': "Provide balanced, informative responses.",
        'technical': "Use technical language and include code examples when relevant.",
        'casual': "Use conversational, easy-to-understand language.",
        'academic': "Provide scholarly responses with proper citations.",
        'concise': "Be brief and to the point.",
        'detailed': "Provide comprehensive, thorough explanations."
    }
    
    language_prompts = {
        'auto': "Respond in the same language as the question.",
        'thai': "Always respond in Thai.",
        'english': "Always respond in English.",
        'mixed': "Use Thai for explanations and English for technical terms."
    }
    
    length_prompts = {
        'short': "Keep response under 100 words.",
        'medium': "Provide moderate-length response (100-300 words).",
        'long': "Provide detailed response (300-500 words).",
        'comprehensive': "Provide thorough response (500+ words)."
    }
    
    # Build enhanced prompt
    enhanced = f"INSTRUCTIONS:\n"
    enhanced += f"- Style: {style_prompts[settings['response_style']]}\n"
    enhanced += f"- Language: {language_prompts[settings['output_language']]}\n"
    enhanced += f"- Length: {length_prompts[settings['response_length']]}\n"
    
    if settings['include_sources']:
        enhanced += "- Always include source references when using document information.\n"
    
    if settings['include_examples']:
        enhanced += "- Include practical examples when relevant.\n"
    
    if settings['step_by_step']:
        enhanced += "- Break down complex topics into step-by-step explanations.\n"
    
    enhanced += f"\nQUERY: {query}"
    
    return enhanced

def main():
    """Main application"""
    initialize_session_state()
    
    # Header
    st.markdown('<h1 class="main-header">🤖 Agentic RAG System</h1>', unsafe_allow_html=True)
    
    # Sidebar for settings
    with st.sidebar:
        st.header("⚙️ System Control")
        
        # System status
        with st.container():
            st.subheader("🔋 System Status")
            if st.session_state.system_initialized:
                st.success("✅ System Ready")
                if st.session_state.rag_system:
                    doc_count = st.session_state.rag_system.get_document_count()
                    st.metric("Documents", doc_count)
            else:
                st.warning("⚠️ System not initialized")
                if st.button("🚀 Initialize System"):
                    initialize_system()
        
        st.divider()
        
        # File upload
        st.subheader("📤 Upload Documents")
        uploaded_files = st.file_uploader(
            "Choose files",
            type=['pdf', 'txt', 'md', 'docx'],
            accept_multiple_files=True,
            help="Upload PDF, TXT, MD, or DOCX files"
        )
        
        if uploaded_files and st.button("📥 Process Files"):
            process_uploaded_files(uploaded_files)
        
        st.divider()
        
        # Response settings
        st.subheader("🎨 Response Settings")
        
        st.session_state.response_style = st.selectbox(
            "Response Style",
            options=['balanced', 'technical', 'casual', 'academic', 'concise', 'detailed'],
            index=['balanced', 'technical', 'casual', 'academic', 'concise', 'detailed'].index(st.session_state.response_style)
        )
        
        st.session_state.output_language = st.selectbox(
            "Output Language",
            options=['auto', 'thai', 'english', 'mixed'],
            index=['auto', 'thai', 'english', 'mixed'].index(st.session_state.output_language)
        )
        
        st.session_state.response_length = st.selectbox(
            "Response Length",
            options=['short', 'medium', 'long', 'comprehensive'],
            index=['short', 'medium', 'long', 'comprehensive'].index(st.session_state.response_length)
        )
        
        st.divider()
        
        # Enhancement options
        st.subheader("✨ Enhancements")
        st.session_state.include_sources = st.checkbox("Include Sources", value=st.session_state.include_sources)
        st.session_state.include_examples = st.checkbox("Include Examples", value=st.session_state.include_examples)
        st.session_state.step_by_step = st.checkbox("Step-by-step", value=st.session_state.step_by_step)
        
        st.divider()
        
        # Clear options
        st.subheader("🧹 Clear Options")
        if st.button("🗑️ Clear Chat"):
            st.session_state.chat_history = []
            st.rerun()
        
        if st.button("💥 Reset System"):
            if st.session_state.rag_system:
                st.session_state.rag_system.clear_vectorstore()
            st.session_state.system_initialized = False
            st.session_state.rag_system = None
            st.session_state.chat_history = []
            st.success("System reset!")
            st.rerun()
    
    # Main chat interface
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.subheader("💬 Chat Interface")
        
        # Display chat history
        chat_container = st.container()
        with chat_container:
            for i, (query, response) in enumerate(st.session_state.chat_history):
                st.markdown(f'<div class="chat-message user-message"><strong>👤 You:</strong> {query}</div>', 
                           unsafe_allow_html=True)
                st.markdown(f'<div class="chat-message agent-message"><strong>🤖 Agent:</strong> {response}</div>', 
                           unsafe_allow_html=True)
        
        # Query input
        query = st.text_input("💬 Ask your question:", placeholder="Type your question here...")
        
        col_send, col_clear = st.columns([1, 4])
        with col_send:
            send_button = st.button("Send", type="primary")
        
        if send_button and query:
            if not st.session_state.system_initialized:
                st.error("❌ Please initialize the system first!")
            elif not st.session_state.rag_system:
                st.error("❌ System not available!")
            else:
                try:
                    with st.spinner("🤔 Thinking..."):
                        # Create enhanced prompt
                        settings = {
                            'response_style': st.session_state.response_style,
                            'output_language': st.session_state.output_language,
                            'response_length': st.session_state.response_length,
                            'include_sources': st.session_state.include_sources,
                            'include_examples': st.session_state.include_examples,
                            'step_by_step': st.session_state.step_by_step
                        }
                        
                        enhanced_query = create_enhanced_prompt(query, settings)
                        response = st.session_state.rag_system.query(enhanced_query)
                        
                        # Add to chat history
                        st.session_state.chat_history.append((query, response))
                        st.rerun()
                        
                except Exception as e:
                    st.error(f"❌ Error processing query: {str(e)}")
    
    with col2:
        st.subheader("📊 System Info")
        
        # API key status
        if openai_api_key:
            st.success("🔑 API Key: ✅")
        else:
            st.error("🔑 API Key: ❌")
        
        st.subheader("💡 Tips")
        st.info("""
        **For better results:**
        - Be specific in your questions
        - Ask about content in the documents
        - Use clear, direct language
        - Try different response styles
        """)
        
        st.subheader("🎯 Example Questions")
        examples = [
            "สรุปเนื้อหาหลักของเอกสาร",
            "Python คืออะไร?",
            "อธิบายเกี่ยวกับ Machine Learning",
            "คำนวณ 15% ของ 1000"
        ]
        
        for example in examples:
            if st.button(f"💭 {example}", key=f"example_{example}"):
                if st.session_state.system_initialized:
                    settings = {
                        'response_style': st.session_state.response_style,
                        'output_language': st.session_state.output_language,
                        'response_length': st.session_state.response_length,
                        'include_sources': st.session_state.include_sources,
                        'include_examples': st.session_state.include_examples,
                        'step_by_step': st.session_state.step_by_step
                    }
                    enhanced_query = create_enhanced_prompt(example, settings)
                    try:
                        response = st.session_state.rag_system.query(enhanced_query)
                        st.session_state.chat_history.append((example, response))
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error: {e}")
                else:
                    st.warning("Please initialize the system first!")

if __name__ == "__main__":
    main()
