"""
Streamlit Web Interface for Agentic RAG
"""
import streamlit as st
import os
import sys
from pathlib import Path
import tempfile
from dotenv import load_dotenv

# Add src to path
sys.path.append(str(Path(__file__).parent / "src"))

from main import AgenticRAGSystem
from src.prompt_manager import get_prompt_manager

# Load environment variables
load_dotenv()

# Page configuration
st.set_page_config(
    page_title="Agentic RAG System",
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
    }
    .chat-message {
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
    }
    .user-message {
        background-color: #e3f2fd;
        border-left: 4px solid #2196f3;
    }
    .agent-message {
        background-color: #f1f8e9;
        border-left: 4px solid #4caf50;
    }
    .sidebar-section {
        margin-bottom: 2rem;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'rag_system' not in st.session_state:
    st.session_state.rag_system = None
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []
if 'system_initialized' not in st.session_state:
    st.session_state.system_initialized = False
if 'custom_prompt' not in st.session_state:
    st.session_state.custom_prompt = ""
if 'response_style' not in st.session_state:
    st.session_state.response_style = "balanced"
if 'output_language' not in st.session_state:
    st.session_state.output_language = "auto"
if 'response_length' not in st.session_state:
    st.session_state.response_length = "medium"
if 'prompt_template' not in st.session_state:
    st.session_state.prompt_template = "default_rag"
if 'enhancement_options' not in st.session_state:
    st.session_state.enhancement_options = {
        'include_examples': True,
        'include_citations': True,
        'include_confidence': False,
        'step_by_step': False,
        'formality': 5,
        'enthusiasm': 5,
        'content_focus': [],
        'exclude_content': []
    }

def initialize_system():
    """Initialize the RAG system"""
    try:
        if not os.getenv("OPENAI_API_KEY"):
            st.error("❌ OPENAI_API_KEY not found. Please set it in your environment variables or .env file.")
            return False
        
        st.session_state.rag_system = AgenticRAGSystem()
        
        # Check if we have documents
        doc_count = st.session_state.rag_system.get_document_count()
        if doc_count == 0:
            st.warning("⚠️ No documents found in vector store. Please upload documents first.")
            return False
        
        # Initialize agent
        st.session_state.rag_system.initialize_agent()
        st.session_state.system_initialized = True
        st.success(f"✅ System initialized successfully! Found {doc_count} documents in vector store.")
        return True
        
    except Exception as e:
        st.error(f"❌ Error initializing system: {str(e)}")
        return False

def create_enhanced_prompt(base_prompt, custom_settings):
    """Create enhanced prompt based on user settings"""
    
    # Response style templates
    style_templates = {
        "balanced": "Provide balanced, clear responses with practical information.",
        "technical": "Use technical terminology and provide detailed technical explanations with code examples when relevant.",
        "casual": "Use conversational tone and simple language. Make it easy to understand.",
        "academic": "Provide scholarly, well-researched responses with proper citations and formal language.",
        "concise": "Be brief and to the point. Provide only essential information.",
        "detailed": "Provide comprehensive, thorough explanations with examples and context."
    }
    
    # Language preferences
    language_instructions = {
        "auto": "Respond in the same language as the question, or Thai if uncertain.",
        "thai": "Always respond in Thai language.",
        "english": "Always respond in English language.",
        "mixed": "Use both Thai and English as appropriate for technical terms."
    }
    
    # Length preferences
    length_instructions = {
        "short": "Keep responses under 100 words. Be concise.",
        "medium": "Provide moderate-length responses (100-300 words).",
        "long": "Provide detailed responses (300-500 words).",
        "comprehensive": "Provide thorough, comprehensive responses (500+ words) with examples."
    }
    
    # Build enhanced prompt
    enhanced_prompt = base_prompt + "\n\nADDITIONAL INSTRUCTIONS:\n"
    enhanced_prompt += f"- STYLE: {style_templates[custom_settings['response_style']]}\n"
    enhanced_prompt += f"- LANGUAGE: {language_instructions[custom_settings['output_language']]}\n"
    enhanced_prompt += f"- LENGTH: {length_instructions[custom_settings['response_length']]}\n"
    
    if custom_settings['custom_prompt']:
        enhanced_prompt += f"- CUSTOM: {custom_settings['custom_prompt']}\n"
    
    return enhanced_prompt

def process_uploaded_files(uploaded_files):
    """Process uploaded files and add to vector store"""
    if not uploaded_files:
        return False
    
    try:
        with st.spinner("Processing uploaded files..."):
            # Create temporary directory for uploaded files
            temp_dir = tempfile.mkdtemp()
            file_paths = []
            
            for uploaded_file in uploaded_files:
                # Save uploaded file to temporary directory
                temp_path = os.path.join(temp_dir, uploaded_file.name)
                with open(temp_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())
                file_paths.append(temp_path)
            
            # Add documents to vector store
            success = st.session_state.rag_system.add_documents_from_sources(file_paths)
            
            # Clean up temporary files
            for file_path in file_paths:
                os.remove(file_path)
            os.rmdir(temp_dir)
            
            if success:
                st.success(f"✅ Successfully processed {len(uploaded_files)} file(s)!")
                return True
            else:
                st.error("❌ Failed to process files.")
                return False
                
    except Exception as e:
        st.error(f"❌ Error processing files: {str(e)}")
        return False

def main():
    """Main Streamlit application"""
    
    # Header
    st.markdown('<h1 class="main-header">🤖 Agentic RAG System</h1>', unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.markdown('<div class="sidebar-section">', unsafe_allow_html=True)
        st.header("📋 System Control")
        
        # System initialization
        if st.button("🚀 Initialize System", type="primary"):
            initialize_system()
        
        # Prompt Customization Section
        st.subheader("🎨 Prompt Customization")
        
        # Prompt Template Selection
        prompt_manager = get_prompt_manager()
        available_templates = prompt_manager.list_templates()
        
        template_descriptions = {
            "default_rag": "Standard RAG system",
            "teacher": "Educational explanations",
            "business_consultant": "Business-focused advice"
        }
        
        selected_template = st.selectbox(
            "📋 Prompt Template",
            available_templates,
            index=available_templates.index(st.session_state.prompt_template) if st.session_state.prompt_template in available_templates else 0,
            format_func=lambda x: f"{x} - {template_descriptions.get(x, 'Custom template')}",
            help="Choose the type of assistant behavior"
        )
        st.session_state.prompt_template = selected_template
        
        # Response Style Selection
        response_style = st.selectbox(
            "🎭 Response Style",
            ["balanced", "technical", "casual", "academic", "concise", "detailed"],
            index=["balanced", "technical", "casual", "academic", "concise", "detailed"].index(st.session_state.response_style),
            help="Choose how the AI should respond"
        )
        st.session_state.response_style = response_style
        
        # Output Language
        output_language = st.selectbox(
            "🌍 Output Language",
            ["auto", "thai", "english", "mixed"],
            index=["auto", "thai", "english", "mixed"].index(st.session_state.output_language),
            help="Preferred language for responses"
        )
        st.session_state.output_language = output_language
        
        # Response Length
        response_length = st.selectbox(
            "📏 Response Length",
            ["short", "medium", "long", "comprehensive"],
            index=["short", "medium", "long", "comprehensive"].index(st.session_state.response_length),
            help="How detailed should the responses be"
        )
        st.session_state.response_length = response_length
        
        # Custom System Prompt
        with st.expander("✏️ Custom System Prompt"):
            custom_prompt = st.text_area(
                "Add custom instructions for the AI",
                value=st.session_state.custom_prompt,
                height=100,
                placeholder="e.g., Always provide examples, Focus on practical applications, Use simple language..."
            )
            st.session_state.custom_prompt = custom_prompt
            
            # Preset prompts
            preset_prompts = {
                "Teacher Mode": "Explain concepts step-by-step like teaching a student. Use examples and analogies.",
                "Expert Mode": "Provide detailed technical information with advanced concepts and industry best practices.",
                "Beginner Mode": "Use simple language and explain technical terms. Provide basic examples.",
                "Business Mode": "Focus on practical applications and business value. Be concise and actionable.",
                "Creative Mode": "Think outside the box. Provide innovative solutions and creative approaches."
            }
            
            selected_preset = st.selectbox("📋 Preset Prompts", ["Custom"] + list(preset_prompts.keys()))
            if selected_preset != "Custom":
                if st.button(f"Apply {selected_preset}"):
                    st.session_state.custom_prompt = preset_prompts[selected_preset]
                    st.rerun()
        
        # Template Management
        with st.expander("💾 Template Management"):
            st.markdown("**Save Current Settings as Template:**")
            
            col1, col2 = st.columns(2)
            with col1:
                new_template_name = st.text_input("Template Name", placeholder="my_custom_template")
            with col2:
                new_template_desc = st.text_input("Description", placeholder="My custom prompt template")
            
            if st.button("💾 Save Template") and new_template_name:
                try:
                    from src.prompt_manager import PromptTemplate
                    
                    # Create new template from current settings
                    new_template = PromptTemplate(
                        name=new_template_name,
                        description=new_template_desc,
                        system_prompt=st.session_state.custom_prompt,
                        style_instructions={
                            "custom": f"Use {st.session_state.response_style} style"
                        },
                        language_instructions={
                            "custom": f"Respond in {st.session_state.output_language}"
                        },
                        length_instructions={
                            "custom": f"Make responses {st.session_state.response_length}"
                        },
                        tags=["custom", "user_created"],
                        examples=[]
                    )
                    
                    prompt_manager = get_prompt_manager()
                    prompt_manager.save_template(new_template)
                    st.success(f"✅ Template '{new_template_name}' saved successfully!")
                except Exception as e:
                    st.error(f"❌ Error saving template: {e}")
            
            st.markdown("**Load Saved Templates:**")
            if st.button("🔄 Refresh Templates"):
                st.rerun()
        
        # Document upload
        st.subheader("📄 Upload Documents")
        uploaded_files = st.file_uploader(
            "Upload documents",
            type=['pdf', 'txt', 'md'],
            accept_multiple_files=True,
            help="Upload PDF, TXT, or MD files to add to the knowledge base"
        )
        
        if uploaded_files and st.button("📤 Process Files"):
            if st.session_state.rag_system is None:
                st.session_state.rag_system = AgenticRAGSystem()
            process_uploaded_files(uploaded_files)
        
        # System status
        st.subheader("📊 System Status")
        if st.session_state.rag_system:
            doc_count = st.session_state.rag_system.get_document_count()
            st.metric("Documents in Vector Store", doc_count)
            
            if st.session_state.system_initialized:
                st.success("✅ Agent Ready")
            else:
                st.warning("⚠️ Agent Not Initialized")
        else:
            st.info("ℹ️ System Not Loaded")
        
        # Clear options
        st.subheader("🧹 Clear Options")
        if st.button("🗑️ Clear Chat History"):
            st.session_state.chat_history = []
            if st.session_state.rag_system and st.session_state.rag_system.agent:
                st.session_state.rag_system.agent.clear_memory()
            st.success("Chat history cleared!")
        
        if st.button("💥 Clear Vector Store", type="secondary"):
            if st.session_state.rag_system:
                st.session_state.rag_system.clear_vectorstore()
                st.session_state.system_initialized = False
                st.success("Vector store cleared!")
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # About section
        with st.expander("ℹ️ About"):
            st.markdown("""
            **Agentic RAG System** combines:
            - 📚 Document retrieval from vector database
            - 🧠 Agent-based reasoning with tools
            - 🤖 Large language model generation
            
            **Features:**
            - Multi-source document loading
            - Intelligent search and retrieval
            - Calculator and web search tools
            - Conversation memory
            - Source citation
            """)
    
    # Main content area
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("💬 Chat Interface")
        
        # Display chat history
        chat_container = st.container()
        with chat_container:
            for message in st.session_state.chat_history:
                if message["role"] == "user":
                    st.markdown(f"""
                    <div class="chat-message user-message">
                        <strong>👤 You:</strong> {message["content"]}
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown(f"""
                    <div class="chat-message agent-message">
                        <strong>🤖 Agent:</strong> {message["content"]}
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Show sources if available
                    if "sources" in message and message["sources"]:
                        with st.expander("📚 Sources"):
                            for source in message["sources"]:
                                st.text(f"• {source}")
        
        # Chat input
        if st.session_state.system_initialized:
            user_input = st.chat_input("Ask me anything about your documents...")
            
            if user_input:
                # Add user message to history
                st.session_state.chat_history.append({
                    "role": "user",
                    "content": user_input
                })
                
                # Get agent response
                with st.spinner("🤔 Agent is thinking..."):
                    try:
                        # Use advanced prompt management
                        prompt_manager = get_prompt_manager()
                        
                        # Collect enhancement options
                        enhancement_options = st.session_state.enhancement_options.copy()
                        
                        # Create enhanced query using prompt manager
                        enhanced_query = prompt_manager.create_query_with_prompt(
                            user_query=user_input,
                            template_name=st.session_state.prompt_template,
                            style=st.session_state.response_style,
                            language=st.session_state.output_language,
                            length=st.session_state.response_length,
                            custom_instructions=st.session_state.custom_prompt,
                            enhancement_options=enhancement_options
                        )
                        
                        result = st.session_state.rag_system.query(enhanced_query)
                        
                        # Add agent response to history
                        agent_message = {
                            "role": "agent",
                            "content": result["answer"]
                        }
                        
                        # Extract sources
                        sources = st.session_state.rag_system.agent.get_sources_used(result)
                        if sources:
                            agent_message["sources"] = sources
                        
                        st.session_state.chat_history.append(agent_message)
                        
                        # Rerun to update the interface
                        st.rerun()
                        
                    except Exception as e:
                        st.error(f"❌ Error: {str(e)}")
        else:
            st.info("ℹ️ Please initialize the system and upload documents to start chatting.")
    
    with col2:
        st.subheader("🔧 Advanced Settings")
        
        # Model settings
        with st.expander("🎛️ Model Configuration"):
            model_name = st.selectbox(
                "Model",
                ["gpt-3.5-turbo", "gpt-4", "gpt-4-turbo"],
                index=0
            )
            
            temperature = st.slider(
                "Temperature",
                min_value=0.0,
                max_value=1.0,
                value=0.1,
                step=0.1,
                help="Controls randomness in responses"
            )
        
        # Response Enhancement
        with st.expander("✨ Response Enhancement"):
            st.markdown("**Enhanced Features:**")
            
            include_examples = st.checkbox("📚 Include Examples", value=st.session_state.enhancement_options['include_examples'])
            include_citations = st.checkbox("📝 Include Citations", value=st.session_state.enhancement_options['include_citations'])
            include_confidence = st.checkbox("📊 Show Confidence Score", value=st.session_state.enhancement_options['include_confidence'])
            step_by_step = st.checkbox("🔢 Step-by-step Explanations", value=st.session_state.enhancement_options['step_by_step'])
            
            # Update session state
            st.session_state.enhancement_options.update({
                'include_examples': include_examples,
                'include_citations': include_citations,
                'include_confidence': include_confidence,
                'step_by_step': step_by_step
            })
            
            # Tone adjustments
            st.markdown("**Tone Adjustments:**")
            formality = st.slider("Formality Level", 0, 10, st.session_state.enhancement_options['formality'], help="0=Very Casual, 10=Very Formal")
            enthusiasm = st.slider("Enthusiasm Level", 0, 10, st.session_state.enhancement_options['enthusiasm'], help="0=Neutral, 10=Very Enthusiastic")
            
            # Update session state
            st.session_state.enhancement_options.update({
                'formality': formality,
                'enthusiasm': enthusiasm
            })
        
        # Content Filtering
        with st.expander("🎯 Content Focus"):
            content_focus = st.multiselect(
                "Focus on specific content types:",
                ["Technical Details", "Business Applications", "Examples", "Best Practices", "Troubleshooting", "Background Theory"],
                default=st.session_state.enhancement_options['content_focus']
            )
            
            exclude_content = st.multiselect(
                "Exclude content types:",
                ["Overly Technical", "Basic Explanations", "Lengthy Background", "Deprecated Information"],
                default=st.session_state.enhancement_options['exclude_content']
            )
            
            # Update session state
            st.session_state.enhancement_options.update({
                'content_focus': content_focus,
                'exclude_content': exclude_content
            })
        
        # Quick actions
        st.subheader("⚡ Quick Actions")
        
        if st.button("📊 Get Document Summary"):
            if st.session_state.system_initialized:
                with st.spinner("Generating summary..."):
                    result = st.session_state.rag_system.query("Provide a comprehensive summary of all the documents in the knowledge base.")
                    st.text_area("Summary", result["answer"], height=200)
            else:
                st.warning("Please initialize the system first.")
        
        if st.button("🔍 Show Available Topics"):
            if st.session_state.system_initialized:
                with st.spinner("Analyzing topics..."):
                    result = st.session_state.rag_system.query("What are the main topics covered in the documents?")
                    st.text_area("Topics", result["answer"], height=150)
            else:
                st.warning("Please initialize the system first.")
        
        # Example queries
        st.subheader("💡 Example Queries")
        example_queries = [
            "What is the main topic of the documents?",
            "Summarize the key points",
            "Calculate 15% of 1000",
            "What are the latest developments mentioned?",
            "Find information about [specific topic]"
        ]
        
        for query in example_queries:
            if st.button(f"💬 {query}", key=f"example_{query}"):
                if st.session_state.system_initialized:
                    # Add to chat
                    st.session_state.chat_history.append({
                        "role": "user",
                        "content": query
                    })
                    
                    with st.spinner("Processing..."):
                        result = st.session_state.rag_system.query(query)
                        agent_message = {
                            "role": "agent",
                            "content": result["answer"]
                        }
                        
                        sources = st.session_state.rag_system.agent.get_sources_used(result)
                        if sources:
                            agent_message["sources"] = sources
                        
                        st.session_state.chat_history.append(agent_message)
                        st.rerun()
                else:
                    st.warning("Please initialize the system first.")

if __name__ == "__main__":
    main()
