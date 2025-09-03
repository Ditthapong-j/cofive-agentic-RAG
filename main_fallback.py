"""
Main entry point for Agentic RAG system with SQLite fallback support
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

class AgenticRAGSystem:
    """Main class for Agentic RAG system with fallback support"""
    
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
        
        # Initialize components with fallback support
        self._initialize_components()
    
    def _initialize_components(self):
        """Initialize system components with fallback handling"""
        try:
            # Try to import and use fallback vector store first
            from src.vector_store_fallback import VectorStoreFallbackManager
            
            print("🔄 Initializing vector store with fallback support...")
            self.vector_manager = VectorStoreFallbackManager(self.vectorstore_path + "_fallback")
            
        except Exception as e:
            print(f"❌ Fallback vector store failed: {e}")
            
            # Fall back to original vector store
            try:
                from src.vector_store import VectorStoreManager
                print("🔄 Trying original vector store...")
                self.vector_manager = VectorStoreManager(self.vectorstore_path)
            except Exception as e2:
                print(f"❌ Original vector store also failed: {e2}")
                raise RuntimeError("Both vector store implementations failed")
        
        # Initialize other components
        try:
            from src.document_loader import DocumentLoader
            self.document_loader = DocumentLoader()
            print("✅ Document loader initialized")
        except Exception as e:
            print(f"❌ Document loader failed: {e}")
            self.document_loader = None
        
        # Agent will be initialized later
        self.agent = None
        print("✅ System components initialized")
    
    def get_document_count(self) -> int:
        """Get number of documents in vector store"""
        try:
            return self.vector_manager.get_document_count()
        except Exception as e:
            print(f"Error getting document count: {e}")
            return 0
    
    def add_documents_from_sources(self, source_paths) -> bool:
        """Add documents from file sources"""
        if not self.document_loader:
            print("❌ Document loader not available")
            return False
        
        try:
            print(f"📄 Processing {len(source_paths)} source(s)...")
            
            all_documents = []
            for source_path in source_paths:
                print(f"📖 Loading: {source_path}")
                documents = self.document_loader.load_documents([source_path])
                all_documents.extend(documents)
                print(f"✅ Loaded {len(documents)} documents from {source_path}")
            
            if all_documents:
                print(f"💾 Adding {len(all_documents)} documents to vector store...")
                success = self.vector_manager.add_documents(all_documents)
                
                if success:
                    print(f"✅ Successfully added {len(all_documents)} documents")
                    print(f"📊 Total documents in store: {self.get_document_count()}")
                    return True
                else:
                    print("❌ Failed to add documents to vector store")
                    return False
            else:
                print("⚠️ No documents were loaded")
                return False
                
        except Exception as e:
            print(f"❌ Error processing documents: {e}")
            return False
    
    def initialize_agent(self):
        """Initialize the RAG agent"""
        try:
            from src.agentic_rag import AgenticRAG
            
            print("🧠 Initializing Agentic RAG agent...")
            
            # Get retriever from vector manager
            retriever = self.vector_manager.get_retriever()
            if not retriever:
                raise ValueError("No retriever available from vector store")
            
            self.agent = AgenticRAG(retriever)
            print("✅ Agent initialized successfully!")
            
        except Exception as e:
            print(f"❌ Failed to initialize agent: {e}")
            raise
    
    def query(self, question: str) -> dict:
        """Query the system"""
        if not self.agent:
            raise ValueError("Agent not initialized. Call initialize_agent() first.")
        
        try:
            return self.agent.query(question)
        except Exception as e:
            print(f"❌ Query failed: {e}")
            return {
                "answer": f"Sorry, I encountered an error: {str(e)}",
                "source_documents": []
            }
    
    def clear_vectorstore(self) -> bool:
        """Clear all documents from vector store"""
        try:
            success = self.vector_manager.clear_vectorstore()
            if success:
                print("🗑️ Vector store cleared successfully")
                # Re-initialize agent if it exists
                if self.agent:
                    self.agent = None
                    print("🔄 Agent reset - call initialize_agent() to reinitialize")
            return success
        except Exception as e:
            print(f"❌ Error clearing vector store: {e}")
            return False


def main():
    """Main function for testing"""
    try:
        print("🚀 Starting Agentic RAG System...")
        
        # Initialize system
        rag_system = AgenticRAGSystem()
        
        # Check document count
        doc_count = rag_system.get_document_count()
        print(f"📊 Current documents in vector store: {doc_count}")
        
        if doc_count == 0:
            print("⚠️ No documents found. Please add documents first.")
            print("💡 You can add documents using:")
            print("   - The Streamlit interface")
            print("   - rag_system.add_documents_from_sources(['path/to/your/file.pdf'])")
            return
        
        # Initialize agent
        rag_system.initialize_agent()
        
        # Test query
        print("\n💬 Testing with a sample query...")
        result = rag_system.query("What is the main topic of the documents?")
        print(f"🤖 Answer: {result['answer']}")
        
        print("\n✅ System is working correctly!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())
