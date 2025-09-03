"""
Main entry point for Streamlit deployment
"""
import sys
import streamlit as st
from pathlib import Path

# Set page config first
st.set_page_config(
    page_title="🤖 Agentic RAG System",
    page_icon="🤖",
    layout="wide"
)

try:
    # Try to import the simple version
    import streamlit_simple
    st.success("✅ Application loaded successfully!")
    
except ImportError as e:
    st.error(f"❌ Import Error: {e}")
    st.info("Some dependencies might be missing. The system will run in basic mode.")
    
    # Fallback interface
    st.title("🤖 Agentic RAG System")
    st.warning("⚠️ Running in basic mode due to missing dependencies")
    
    # Basic chat interface
    if 'messages' not in st.session_state:
        st.session_state.messages = []
    
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    if prompt := st.chat_input("Ask me anything..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        
        with st.chat_message("assistant"):
            response = f"You asked: '{prompt}'. I'm running in basic mode. Please check the deployment logs for dependency issues."
            st.markdown(response)
            st.session_state.messages.append({"role": "assistant", "content": response})

except Exception as e:
    st.error(f"❌ Application Error: {e}")
    st.info("There was an error loading the application. Please check the logs.")
    
    # Ultra-basic fallback
    st.title("🤖 Agentic RAG System - Debug Mode")
    st.text_area("System Information", f"Error: {e}\nPython Path: {sys.path}", height=200)
