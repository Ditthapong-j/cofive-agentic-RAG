"""
Main entry point for Agentic RAG system
"""
import os
import sys
from pathlib import Path

# Try to import dotenv, handle if not available
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    print("⚠️ python-dotenv not found. Please install with: pip install python-dotenv")
    print("📝 Or set environment variables manually")
    load_dotenv = lambda: None

# Add src to path
sys.path.append(str(Path(__file__).parent / "src"))

try:
    from src.document_loader import DocumentLoader
    from src.vector_store import VectorStoreManager
    from src.agentic_rag import AgenticRAG
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("📦 Please install required packages: pip install -r requirements.txt")
    sys.exit(1)


class AgenticRAGSystem:
    """Main class for Agentic RAG system"""
    
    def __init__(self, vectorstore_path: str = "./vectorstore"):
        # Try to load environment variables
        try:
            from dotenv import load_dotenv
            load_dotenv()
        except ImportError:
            print("⚠️ python-dotenv not installed. Using system environment variables.")
        
        # Check for OpenAI API key
        if not os.getenv("OPENAI_API_KEY"):
            print("❌ OPENAI_API_KEY not found in environment variables.")
            print("💡 Please set it either:")
            print("   1. In .env file: OPENAI_API_KEY=your_key_here")
            print("   2. Export in terminal: export OPENAI_API_KEY=your_key_here")
            print("   3. Set in your system environment variables")
            raise ValueError("OPENAI_API_KEY is required to run the system.")
        
        self.vectorstore_path = vectorstore_path
        
        try:
            self.document_loader = DocumentLoader()
            self.vector_store_manager = VectorStoreManager(persist_directory=vectorstore_path)
            self.agent = None
        except Exception as e:
            print(f"❌ Error initializing components: {e}")
            print("📦 Please ensure all required packages are installed:")
            print("   pip install -r requirements.txt")
            raise
        
        # Try to load existing vector store
        if not self.vector_store_manager.load_vectorstore():
            print("📝 No existing vector store found. You'll need to add documents first.")
    
    def add_documents_from_sources(self, sources: list):
        """
        Add documents from various sources (files, directories, URLs)
        
        Args:
            sources: List of file paths, directory paths, or URLs
        """
        print("Loading documents from sources...")
        documents = self.document_loader.load_multiple_sources(sources)
        
        if not documents:
            print("No documents were loaded successfully.")
            return False
        
        print(f"Loaded {len(documents)} document chunks.")
        
        # Add to vector store
        self.vector_store_manager.add_documents(documents)
        print("Documents added to vector store successfully!")
        return True
    
    def initialize_agent(self, model_name: str = "gpt-3.5-turbo", temperature: float = 0.1):
        """Initialize the agentic RAG agent"""
        if self.vector_store_manager.get_document_count() == 0:
            raise ValueError("No documents in vector store. Add documents first.")
        
        print("Initializing Agentic RAG agent...")
        self.agent = AgenticRAG(
            vector_store_manager=self.vector_store_manager,
            model_name=model_name,
            temperature=temperature
        )
        print("Agent initialized successfully!")
    
    def query(self, question: str):
        """Query the agentic RAG system"""
        if not self.agent:
            raise ValueError("Agent not initialized. Call initialize_agent() first.")
        
        return self.agent.query(question)
    
    def chat(self, message: str):
        """Simple chat interface"""
        if not self.agent:
            raise ValueError("Agent not initialized. Call initialize_agent() first.")
        
        return self.agent.chat(message)
    
    def get_document_count(self):
        """Get the number of documents in the vector store"""
        return self.vector_store_manager.get_document_count()
    
    def clear_vectorstore(self):
        """Clear the vector store"""
        self.vector_store_manager.delete_collection()
        print("Vector store cleared.")


def main():
    """Example usage of the Agentic RAG system"""
    
    # Create system instance
    rag_system = AgenticRAGSystem()
    
    # Example: Add documents from data directory
    data_sources = [
        "./data",  # Add all files from data directory
        # "https://example.com",  # Add web page
        # "./path/to/specific/file.pdf"  # Add specific file
    ]
    
    # Check if we have documents
    if rag_system.get_document_count() == 0:
        print("No documents found in vector store.")
        print("Add some documents to the './data' directory and run again.")
        print("Supported formats: PDF, TXT, MD files")
        
        # Create a sample document if data directory is empty
        os.makedirs("./data", exist_ok=True)
        sample_content = """
        Welcome to the Agentic RAG System!
        
        This is a sample document to demonstrate the capabilities of the system.
        
        The Agentic RAG (Retrieval-Augmented Generation) system combines:
        1. Document retrieval from a vector database
        2. Agent-based reasoning with tools
        3. Large language model generation
        
        Key features:
        - Multi-source document loading (PDF, text, web pages)
        - Intelligent document search and retrieval
        - Agent with multiple tools (search, calculate, summarize)
        - Conversation memory
        - Source citation
        
        You can ask questions about the documents, perform calculations, 
        get summaries, and the agent will use the appropriate tools to help you.
        """
        
        with open("./data/sample.txt", "w", encoding="utf-8") as f:
            f.write(sample_content)
        
        print("Created sample document. Adding to vector store...")
        rag_system.add_documents_from_sources(data_sources)
    
    # Initialize agent
    rag_system.initialize_agent()
    
    # Interactive chat loop
    print("\n" + "="*50)
    print("Agentic RAG System Ready!")
    print("="*50)
    print("You can now ask questions about your documents.")
    print("Type 'quit' or 'exit' to end the session.")
    print("Type 'clear' to clear conversation history.")
    print("-"*50)
    
    while True:
        try:
            user_input = input("\nYou: ").strip()
            
            if user_input.lower() in ['quit', 'exit']:
                print("Goodbye!")
                break
            
            if user_input.lower() == 'clear':
                rag_system.agent.clear_memory()
                print("Conversation history cleared.")
                continue
            
            if not user_input:
                continue
            
            print("\nAgent: Thinking...")
            result = rag_system.query(user_input)
            
            print(f"\nAgent: {result['answer']}")
            
            # Show sources if available
            sources = rag_system.agent.get_sources_used(result)
            if sources:
                print(f"\nSources: {', '.join(sources)}")
        
        except KeyboardInterrupt:
            print("\n\nGoodbye!")
            break
        except Exception as e:
            print(f"\nError: {e}")


if __name__ == "__main__":
    main()
