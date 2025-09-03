"""
Streamlit Web Interface for Agentic RAG - Production Deployment Version
"""
import streamlit as st
import os
im        except ImportError:
            # Fallback to main system
            try:
                from main import AgenticRAGSystem
                st.info("🔄 Using main system...")
                rag_system = AgenticRAGSystem()sys
from pathlib import Path
import tempfile

# Set page config first
st.set_page_config(
    page_title="🤖 Agentic RAG System",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Add src to Python path
current_dir = Path(__file__).parent
src_path = current_dir / "src"
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

# Import with error handling
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# Custom CSS for enhanced UI
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
</style>
""", unsafe_allow_html=True)

def get_env_var(key, default=None):
    """Get environment variable with fallback to Streamlit secrets"""
    # Try environment variable first
    value = os.getenv(key, default)
    # Try Streamlit secrets if env var not found
    if value is None:
        try:
            if hasattr(st, 'secrets') and key in st.secrets:
                value = st.secrets[key]
        except Exception:
            pass
    return value

def check_environment():
    """Check and setup environment variables with enhanced error handling"""
    required_vars = ["OPENAI_API_KEY"]
    missing_vars = []
    
    for var in required_vars:
        value = get_env_var(var)
        
        if value:
            # Set environment variable for the system
            os.environ[var] = value
        else:
            missing_vars.append(var)
    
    return missing_vars

def initialize_system():
    """Initialize the RAG system with proper fallback handling"""
    try:
        # Try FAISS first (recommended)
        try:
            from main_faiss import AgenticRAGSystem
            st.info("🔄 Using FAISS vector store (SQLite-free)...")
            
            # Get current settings
            model_name = st.session_state.get('selected_model', 'gpt-3.5-turbo')
            temperature = st.session_state.get('temperature', 0.1)
            custom_prompt = st.session_state.get('custom_prompt', '').strip() or None
            
            # Initialize with settings
            rag_system = AgenticRAGSystem(
                model_name=model_name,
                temperature=temperature,
                custom_prompt=custom_prompt
            )
        except ImportError:
            # Fallback to main system
            try:
                from main import AgenticRAGSystem
                st.info("� Using main system...")
            except ImportError:
                # Final fallback - build system manually
                from vector_store_faiss import FAISSVectorStore
                from document_loader import DocumentLoader
                from agentic_rag import AgenticRAG
                
                class AgenticRAGSystem:
                    def __init__(self):
                        self.vector_manager = FAISSVectorStore()
                        self.doc_loader = DocumentLoader()
                        self.agent = None
                        
                    def get_document_count(self):
                        return len(self.vector_manager.documents) if hasattr(self.vector_manager, 'documents') else 0
                        
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
                            return {"answer": result.get('output', result.get('answer', str(result)))}
                        return {"answer": "Agent not initialized. Please add documents first."}
                        
                    def add_documents_from_sources(self, sources):
                        try:
                            documents = self.doc_loader.load_documents(sources)
                            if documents:
                                self.vector_manager.add_documents(documents)
                                return True
                            return False
                        except Exception as e:
                            st.error(f"Error adding documents: {e}")
                            return False
                
                st.info("🔄 Using fallback system...")
        
        with st.spinner("🚀 Initializing system..."):
            rag_system = AgenticRAGSystem()
            
            # Check for existing documents
            data_path = current_dir / "data"
            if data_path.exists() and any(data_path.iterdir()):
                try:
                    rag_system.add_documents_from_sources([str(data_path)])
                    doc_count = rag_system.get_document_count()
                    if doc_count > 0:
                        st.success(f"✅ Loaded {doc_count} documents from data folder")
                        rag_system.initialize_agent()
                        st.session_state.rag_system = rag_system
                        st.session_state.system_ready = True
                        return True
                except Exception as e:
                    st.warning(f"⚠️ Could not load existing documents: {e}")
            
            # Store system for file upload
            st.session_state.rag_system = rag_system
            st.warning("⚠️ No documents found. Please upload documents first.")
            return False
                
    except Exception as e:
        st.error(f"❌ System initialization error: {e}")
        st.info("🔧 Try installing missing dependencies:")
        st.code("pip install faiss-cpu langchain-openai")
        return False

def process_uploaded_files(uploaded_files):
    """Process uploaded files with enhanced error handling"""
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
                        if st.session_state.rag_system.initialize_agent():
                            st.session_state.system_ready = True
                            st.success("✅ System is now ready for questions!")
                        else:
                            st.warning("⚠️ Files uploaded but agent initialization failed")
                    except Exception as e:
                        st.warning(f"⚠️ Files uploaded but agent init failed: {e}")
                return True
            else:
                st.error("❌ Failed to process files")
                return False
                
    except Exception as e:
        st.error(f"❌ Error processing files: {e}")
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
    """Main application with enhanced UI and settings"""
    
    # Header with styling
    st.markdown('<h1 class="main-header">🤖 Agentic RAG System</h1>', unsafe_allow_html=True)
    st.markdown("### AI-Powered Document Question Answering with Advanced Settings")
    
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
            1. Create a `.env` file or `.streamlit/secrets.toml`
            2. Add: `OPENAI_API_KEY = "your_api_key_here"`
            
            **Alternative: Environment Variable**
            ```bash
            export OPENAI_API_KEY="your_api_key_here"
            ```
            """)
        st.stop()
    
    # Initialize session state
    session_defaults = {
        'messages': [],
        'system_ready': False,
        'response_style': 'balanced',
        'output_language': 'auto',
        'response_length': 'medium',
        'include_sources': True,
        'include_examples': False,
        'step_by_step': False,
        'selected_model': 'gpt-3.5-turbo',
        'custom_prompt': '',
        'temperature': 0.1
    }
    
    for key, default_value in session_defaults.items():
        if key not in st.session_state:
            st.session_state[key] = default_value
    
    # Sidebar with enhanced controls
    with st.sidebar:
        st.header("⚙️ System Control")
        
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
        
        st.divider()
        
        # File upload section
        st.header("📄 Upload Documents")
        uploaded_files = st.file_uploader(
            "Choose files to upload",
            type=['pdf', 'txt', 'md', 'docx'],
            accept_multiple_files=True,
            help="Upload PDF, TXT, MD, or DOCX files"
        )
        
        if uploaded_files and st.button("📤 Process Files"):
            # Initialize system if needed
            if not hasattr(st.session_state, 'rag_system'):
                initialize_system()
            
            if hasattr(st.session_state, 'rag_system'):
                process_uploaded_files(uploaded_files)
        
        st.divider()
        
        # Model and AI Settings
        st.header("🤖 Model Settings")
        
        # Model selection
        available_models = [
            'gpt-3.5-turbo',
            'gpt-4',
            'gpt-4-turbo-preview',
            'gpt-4o',
            'gpt-4o-mini'
        ]
        
        st.session_state.selected_model = st.selectbox(
            "Select Model",
            options=available_models,
            index=available_models.index(st.session_state.selected_model) if st.session_state.selected_model in available_models else 0,
            help="Choose the AI model to use"
        )
        
        # Temperature setting
        st.session_state.temperature = st.slider(
            "Temperature",
            min_value=0.0,
            max_value=2.0,
            value=st.session_state.temperature,
            step=0.1,
            help="Controls randomness: 0.0 = deterministic, 2.0 = very creative"
        )
        
        # Custom prompt
        st.session_state.custom_prompt = st.text_area(
            "Custom System Prompt",
            value=st.session_state.custom_prompt,
            height=150,
            help="Override the default system prompt with your own instructions",
            placeholder="Enter custom instructions for the AI assistant..."
        )
        
        # Reinitialize system if settings changed
        if st.button("🔄 Apply Model Settings"):
            if hasattr(st.session_state, 'rag_system'):
                del st.session_state.rag_system
            st.session_state.system_ready = False
            st.success("Settings updated! Please initialize system again.")
        
        st.divider()
        
        # Response customization settings
        st.header("🎨 Response Settings")
        
        st.session_state.response_style = st.selectbox(
            "Response Style",
            options=['balanced', 'technical', 'casual', 'academic', 'concise', 'detailed'],
            index=['balanced', 'technical', 'casual', 'academic', 'concise', 'detailed'].index(st.session_state.response_style),
            help="Choose the tone and style of responses"
        )
        
        st.session_state.output_language = st.selectbox(
            "Output Language",
            options=['auto', 'thai', 'english', 'mixed'],
            index=['auto', 'thai', 'english', 'mixed'].index(st.session_state.output_language),
            help="Control the language of responses"
        )
        
        st.session_state.response_length = st.selectbox(
            "Response Length",
            options=['short', 'medium', 'long', 'comprehensive'],
            index=['short', 'medium', 'long', 'comprehensive'].index(st.session_state.response_length),
            help="Control how detailed responses should be"
        )
        
        st.divider()
        
        # Enhancement options
        st.header("✨ Enhancement Options")
        st.session_state.include_sources = st.checkbox(
            "Include Sources", 
            value=st.session_state.include_sources,
            help="Show source references in responses"
        )
        st.session_state.include_examples = st.checkbox(
            "Include Examples", 
            value=st.session_state.include_examples,
            help="Add practical examples when relevant"
        )
        st.session_state.step_by_step = st.checkbox(
            "Step-by-Step Explanations", 
            value=st.session_state.step_by_step,
            help="Break down complex topics into steps"
        )
        
        st.divider()
        
        # System management
        st.header("🛠️ System Management")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("🗑️ Clear Chat"):
                st.session_state.messages = []
                st.success("Chat cleared!")
                st.rerun()
        
        with col2:
            if st.button("🔄 Reset System"):
                # Clear session state
                for key in list(st.session_state.keys()):
                    del st.session_state[key]
                st.success("System reset!")
                st.rerun()
        
        # Example questions
        st.header("💡 Example Questions")
        examples = [
            "สรุปเนื้อหาหลักของเอกสาร",
            "What are the main topics?",
            "Explain the key concepts",
            "Calculate 15% of 1000"
        ]
        
        for example in examples:
            if st.button(f"💭 {example}", key=f"example_{example}"):
                # Add to messages and process
                st.session_state.messages.append({"role": "user", "content": example})
                st.rerun()
        
        # About section
        with st.expander("ℹ️ About System"):
            st.markdown("""
            **Enhanced Agentic RAG System** features:
            - 📚 Multi-format document processing
            - 🔍 Intelligent semantic search
            - 🤖 AI-powered question answering
            - 🎨 Customizable response styles
            - 🌐 Multi-language support
            - 📝 Source citations
            - 🧮 Built-in calculator
            - 🔧 FAISS vector database (SQLite-free)
            """)
    
    # Main chat interface
    st.header("💬 Enhanced Chat Interface")
    
    # Display chat messages with enhanced styling
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            
            # Show sources if available
            if message["role"] == "assistant" and "sources" in message:
                with st.expander("📚 Sources Used"):
                    for i, source in enumerate(message["sources"], 1):
                        st.text(f"{i}. {source}")
    
    # Chat input with enhanced processing
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
                        # Create enhanced prompt based on settings
                        settings = {
                            'response_style': st.session_state.response_style,
                            'output_language': st.session_state.output_language,
                            'response_length': st.session_state.response_length,
                            'include_sources': st.session_state.include_sources,
                            'include_examples': st.session_state.include_examples,
                            'step_by_step': st.session_state.step_by_step
                        }
                        
                        enhanced_query = create_enhanced_prompt(prompt, settings)
                        
                        # Query the system
                        result = st.session_state.rag_system.query(enhanced_query)
                        response = result.get("answer", "I couldn't generate a response.")
                        
                        st.markdown(response)
                        
                        # Try to get sources
                        sources = []
                        try:
                            if hasattr(st.session_state.rag_system, 'agent') and hasattr(st.session_state.rag_system.agent, 'get_sources_used'):
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
                
                I'm here to help analyze your documents with customizable response styles and languages.
                """
                st.markdown(fallback_msg)
                st.session_state.messages.append({"role": "assistant", "content": fallback_msg})
    
    # Welcome message for new users
    if not st.session_state.messages:
        st.info("""
        👋 **Welcome to the Enhanced Agentic RAG System!**
        
        **🚀 Quick Start:**
        1. 📤 **Upload Documents**: Use the sidebar to upload PDF, TXT, MD, or DOCX files
        2. 🚀 **Initialize System**: Click the "Initialize System" button
        3. 🎨 **Customize Settings**: Choose your preferred response style, language, and length
        4. 💬 **Start Chatting**: Ask questions about your documents!
        
        **✨ Enhanced Features:**
        - 🎨 **Customizable Response Styles**: Technical, casual, academic, and more
        - 🌐 **Multi-language Support**: Auto-detect, Thai, English, or mixed
        - 📏 **Response Length Control**: Short, medium, long, or comprehensive
        - 📚 **Source Citations**: Track where information comes from
        - 🧮 **Built-in Calculator**: Perform calculations when needed
        - 🔧 **SQLite-free**: Uses FAISS for better compatibility
        
        **💡 Try Example Questions:**
        - Click the example buttons in the sidebar
        - Or ask: *"What are the main topics in my documents?"*
        - Try: *"Summarize the key points in Thai"*
        """)

if __name__ == "__main__":
    main()
