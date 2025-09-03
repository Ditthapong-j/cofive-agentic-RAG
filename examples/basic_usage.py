"""
Basic usage example for Agentic RAG system
"""
import sys
import os
from pathlib import Path

# Add parent directory to path to import modules
sys.path.append(str(Path(__file__).parent.parent))

from src.document_loader import DocumentLoader
from src.vector_store import VectorStoreManager
from src.agentic_rag import AgenticRAG
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


def basic_example():
    """Basic usage example"""
    print("🚀 Starting Basic Agentic RAG Example")
    print("-" * 50)
    
    # 1. Initialize components
    print("1. Initializing components...")
    document_loader = DocumentLoader(chunk_size=1000, chunk_overlap=200)
    vector_store = VectorStoreManager(persist_directory="./example_vectorstore")
    
    # 2. Load documents
    print("2. Loading documents...")
    # You can use various sources:
    sources = [
        "../data",  # Directory with documents
        # "https://example.com/article",  # Web URL
        # "./sample_doc.pdf"  # Individual file
    ]
    
    documents = document_loader.load_multiple_sources(sources)
    if not documents:
        print("❌ No documents loaded. Please add documents to ../data directory")
        return
    
    print(f"   Loaded {len(documents)} document chunks")
    
    # 3. Create/load vector store
    print("3. Setting up vector store...")
    if not vector_store.load_vectorstore():
        vector_store.create_vectorstore(documents)
    else:
        print("   Using existing vector store")
    
    # 4. Initialize agent
    print("4. Initializing Agentic RAG agent...")
    agent = AgenticRAG(
        vector_store_manager=vector_store,
        model_name="gpt-3.5-turbo",
        temperature=0.1,
        verbose=True
    )
    
    # 5. Example queries
    print("\n" + "="*50)
    print("🤖 Agent Ready! Running Example Queries")
    print("="*50)
    
    example_queries = [
        "สรุปเนื้อหาหลักของเอกสารที่มี",
        "มีหัวข้ออะไรบ้างในเอกสาร",
        "คำนวณ 25% ของ 800",
        "อธิบายเกี่ยวกับ Python",
    ]
    
    for i, query in enumerate(example_queries, 1):
        print(f"\n📝 Query {i}: {query}")
        print("-" * 30)
        
        result = agent.query(query)
        print(f"🤖 Answer: {result['answer']}")
        
        # Show sources if available
        sources = agent.get_sources_used(result)
        if sources:
            print(f"📚 Sources: {', '.join(sources)}")
        
        print()
    
    print("✅ Example completed successfully!")


def interactive_example():
    """Interactive chat example"""
    print("🚀 Starting Interactive Agentic RAG Example")
    print("-" * 50)
    
    # Initialize system (same as basic example)
    document_loader = DocumentLoader()
    vector_store = VectorStoreManager(persist_directory="./example_vectorstore")
    
    # Load documents
    sources = ["../data"]
    documents = document_loader.load_multiple_sources(sources)
    
    if not documents:
        print("❌ No documents loaded. Please add documents to ../data directory")
        return
    
    # Setup vector store
    if not vector_store.load_vectorstore():
        vector_store.create_vectorstore(documents)
    
    # Initialize agent
    agent = AgenticRAG(vector_store_manager=vector_store)
    
    print("\n" + "="*50)
    print("💬 Interactive Chat Mode")
    print("="*50)
    print("Type your questions (or 'quit' to exit)")
    print("-" * 50)
    
    while True:
        try:
            user_input = input("\n🙋 You: ").strip()
            
            if user_input.lower() in ['quit', 'exit', 'ออก']:
                print("👋 Goodbye!")
                break
            
            if user_input.lower() == 'clear':
                agent.clear_memory()
                print("🧹 Conversation history cleared.")
                continue
            
            if not user_input:
                continue
            
            print("\n🤖 Agent: Thinking...")
            result = agent.query(user_input)
            
            print(f"\n🤖 Agent: {result['answer']}")
            
            # Show sources
            sources = agent.get_sources_used(result)
            if sources:
                print(f"\n📚 Sources: {', '.join(sources)}")
        
        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"\n❌ Error: {e}")


def main():
    """Main function to choose example type"""
    print("🎯 Agentic RAG Examples")
    print("1. Basic Example (predefined queries)")
    print("2. Interactive Example (chat mode)")
    
    while True:
        choice = input("\nSelect example (1 or 2): ").strip()
        
        if choice == "1":
            basic_example()
            break
        elif choice == "2":
            interactive_example()
            break
        else:
            print("❌ Invalid choice. Please enter 1 or 2.")


if __name__ == "__main__":
    main()
