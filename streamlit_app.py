"""
Streamlit Web Interface for Agentic RAG - Enhanced Version with Model Selection and Custom Prompts
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
    """Initialize the RAG system with model settings"""
    try:
        # Get current settings
        model_name = st.session_state.get('selected_model', 'gpt-3.5-turbo')
        temperature = st.session_state.get('temperature', 0.1)
        custom_prompt = st.session_state.get('custom_prompt', '').strip() or None
        
        # Try FAISS first (recommended)
        try:
            from main_faiss import AgenticRAGSystem
            st.info(f"🔄 Using FAISS vector store with {model_name}...")
            
            # Initialize with settings
            rag_system = AgenticRAGSystem(
                model_name=model_name,
                temperature=temperature,
                custom_prompt=custom_prompt
            )
            
        except ImportError:
            st.error("❌ main_faiss.py not found. Please ensure the file exists.")
            return False
        
        with st.spinner("🚀 Initializing system..."):
            # Store system for file upload only - no automatic data loading
            st.session_state.rag_system = rag_system
            st.info("💡 System initialized! Please upload documents to get started.")
            st.warning("� No automatic document loading. Upload files using the sidebar.")
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
                        # Check if we have enough documents
                        doc_count = st.session_state.rag_system.get_document_count()
                        st.info(f"📊 Total documents in database: {doc_count}")
                        
                        if doc_count > 0:
                            # Try to initialize agent
                            if st.session_state.rag_system.initialize_agent():
                                st.session_state.system_ready = True
                                st.success("✅ System is now ready for questions!")
                                st.balloons()  # Celebration effect
                            else:
                                st.error("❌ Agent initialization failed even with documents present")
                                st.info("💡 Try clicking 'Apply Model Settings' and then 'Initialize System' again")
                        else:
                            st.warning("⚠️ No documents found in database after upload")
                            st.info("💡 Please try uploading the files again")
                            
                    except Exception as e:
                        st.error(f"❌ Agent initialization error: {str(e)}")
                        st.info("🔧 Troubleshooting steps:")
                        st.code("""
1. Check if OPENAI_API_KEY is set correctly
2. Try clicking 'Apply Model Settings' 
3. Click 'Initialize System' again
4. If still failing, try 'Reset System' and start over
                        """)
                        
                        # Show detailed error for debugging
                        with st.expander("🐛 Technical Details"):
                            st.text(f"Error type: {type(e).__name__}")
                            st.text(f"Error message: {str(e)}")
                            
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
    st.markdown('<h1 class="main-header">🤖 Enhanced Agentic RAG System</h1>', unsafe_allow_html=True)
    st.markdown("### AI-Powered Document Q&A with Custom Models & Prompts")
    
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
        'selected_model': 'gpt-4o-mini',
        'custom_prompt': '',
        'temperature': 0.1
    }
    
    for key, default_value in session_defaults.items():
        if key not in st.session_state:
            st.session_state[key] = default_value
    
    # Sidebar with enhanced controls
    with st.sidebar:
        st.header("⚙️ System Control")
        
        # System status display
        with st.container():
            st.subheader("📊 System Status")
            
            # Check system components
            has_system = hasattr(st.session_state, 'rag_system')
            is_ready = st.session_state.get('system_ready', False)
            
            if has_system:
                st.success("✅ RAG System: Loaded")
                try:
                    doc_count = st.session_state.rag_system.get_document_count()
                    if doc_count > 0:
                        st.success(f"✅ Documents: {doc_count} loaded")
                    else:
                        st.warning("⚠️ Documents: None loaded")
                except:
                    st.error("❌ Documents: Error checking count")
            else:
                st.error("❌ RAG System: Not loaded")
            
            if is_ready:
                st.success("✅ Agent: Ready")
            else:
                st.error("❌ Agent: Not initialized")
            
            # API Key status
            api_key = get_env_var("OPENAI_API_KEY")
            if api_key:
                st.success("✅ API Key: Configured")
            else:
                st.error("❌ API Key: Missing")
        
        st.divider()
        
        # System status and initialization
        if not st.session_state.system_ready:
            if st.button("🚀 Initialize System", type="primary"):
                initialize_system()
                
            # Show manual agent initialization if system exists but agent not ready
            if hasattr(st.session_state, 'rag_system') and not st.session_state.system_ready:
                st.warning("⚠️ System exists but agent not ready")
                
                # Check if agent is actually ready but session state is wrong
                if hasattr(st.session_state.rag_system, 'is_agent_ready') and st.session_state.rag_system.is_agent_ready():
                    st.session_state.system_ready = True
                    st.success("✅ Agent was already ready! Status updated.")
                    st.rerun()
                
                if st.button("🤖 Try Initialize Agent Only"):
                    try:
                        doc_count = st.session_state.rag_system.get_document_count()
                        st.info(f"📊 Documents available: {doc_count}")
                        
                        if doc_count > 0:
                            with st.spinner("🤖 Initializing agent..."):
                                if st.session_state.rag_system.initialize_agent():
                                    st.session_state.system_ready = True
                                    st.success("✅ Agent initialized successfully!")
                                    st.rerun()
                                else:
                                    st.error("❌ Agent initialization returned False")
                        else:
                            st.error("❌ No documents found. Please upload documents first.")
                    except Exception as e:
                        st.error(f"❌ Agent initialization failed: {e}")
                        with st.expander("🔧 Debug Info"):
                            st.text(f"Model: {st.session_state.get('selected_model', 'Unknown')}")
                            st.text(f"Temperature: {st.session_state.get('temperature', 'Unknown')}")
                            st.text(f"Custom prompt: {'Yes' if st.session_state.get('custom_prompt', '').strip() else 'No'}")
                            st.text(f"Error type: {type(e).__name__}")
                            st.text(f"Error details: {str(e)}")
        else:
            st.success("✅ System Ready")
            
            # Show document count and model info
            if hasattr(st.session_state, 'rag_system'):
                try:
                    doc_count = st.session_state.rag_system.get_document_count()
                    model_name = st.session_state.get('selected_model', 'Unknown')
                    st.metric("Documents in Database", doc_count)
                    st.info(f"🤖 Using: {model_name}")
                except:
                    st.metric("Documents", "Unknown")
        
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
        with st.expander("ℹ️ About Enhanced System"):
            st.markdown(f"""
            **Enhanced Agentic RAG System** features:
            - 🤖 **Model Selection**: Choose from GPT-3.5 to GPT-4o
            - 🎨 **Custom Prompts**: Override system instructions
            - 🌡️ **Temperature Control**: Adjust creativity level
            - 📚 **Multi-format Documents**: PDF, TXT, MD, DOCX
            - 🔍 **FAISS Vector Search**: SQLite-free, faster search
            - 🌐 **Multi-language Support**: Thai, English, Mixed
            - 📝 **Response Customization**: Style, length, format
            - 📊 **Source Citations**: Track information sources
            
            **Current Model**: {st.session_state.get('selected_model', 'Not selected')}
            **Temperature**: {st.session_state.get('temperature', 0.1)}
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
                        
                        # Use custom prompt enhancement if no custom system prompt is set
                        if not st.session_state.get('custom_prompt', '').strip():
                            enhanced_query = create_enhanced_prompt(prompt, settings)
                        else:
                            enhanced_query = prompt  # Let the custom system prompt handle formatting
                        
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
                3. 🤖 Select your preferred model and settings
                4. 💬 Then ask your questions!
                
                I'm here to help analyze your documents with customizable AI models and response styles.
                """
                st.markdown(fallback_msg)
                st.session_state.messages.append({"role": "assistant", "content": fallback_msg})
    
    # Welcome message for new users
    if not st.session_state.messages:
        st.info("""
        👋 **Welcome to the Enhanced Agentic RAG System!**
        
        **🚀 Quick Start:**
        1. 🤖 **Choose Model**: Select from GPT-3.5-turbo to GPT-4o in the sidebar
        2. 🌡️ **Adjust Temperature**: Control creativity level (0.0 = precise, 2.0 = creative)
        3. 📝 **Custom Prompt**: Override system instructions with your own
        4. 📤 **Upload Documents**: Add PDF, TXT, MD, or DOCX files
        5. 🚀 **Initialize System**: Start the AI with your settings
        6. 💬 **Start Chatting**: Ask questions about your documents!
        
        **✨ Enhanced Features:**
        - 🤖 **Multiple AI Models**: Choose the best model for your needs
        - 📝 **Custom System Prompts**: Define exactly how the AI should behave
        - 🌡️ **Temperature Control**: Fine-tune response creativity
        - 🎨 **Response Customization**: Style, language, length control
        - 📚 **Advanced Document Processing**: Multi-format support
        - 🔍 **FAISS Vector Search**: Fast, SQLite-free search
        - 📊 **Source Tracking**: See where answers come from
        
        **💡 Pro Tips:**
        - Try different models for different tasks (GPT-4 for complex analysis, GPT-3.5 for quick questions)
        - Use custom prompts to create specialized assistants
        - Adjust temperature based on your needs (low for facts, high for creativity)
        """)

if __name__ == "__main__":
    main()
