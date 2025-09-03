#!/usr/bin/env python3
"""
Debug script to test vector store functionality
"""
import os
import sys
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent / "src"))

# Load environment
from dotenv import load_dotenv
load_dotenv()

def test_vector_search():
    """Test vector store search functionality"""
    print("🔍 Testing Vector Store Search...")
    print("-" * 40)
    
    # Check API key
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("❌ OPENAI_API_KEY not found!")
        return False
    
    print(f"✅ API Key loaded: {api_key[:10]}...")
    
    try:
        from src.vector_store import VectorStoreManager
        
        # Initialize vector store
        vm = VectorStoreManager()
        success = vm.load_vectorstore()
        
        if not success:
            print("❌ Vector store not loaded or empty")
            return False
        
        doc_count = vm.get_document_count()
        print(f"✅ Vector store loaded with {doc_count} documents")
        
        # Test searches
        test_queries = [
            "Python programming",
            "Cofive company", 
            "Agentic RAG"
        ]
        
        for query in test_queries:
            print(f"\n🔍 Searching for: '{query}'")
            results = vm.search(query, k=2)
            
            if results:
                for i, doc in enumerate(results, 1):
                    print(f"  {i}. {doc.page_content[:100]}...")
                    print(f"     Source: {doc.metadata.get('source', 'Unknown')}")
            else:
                print("  ❌ No results found")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_document_search_tool():
    """Test the document search tool specifically"""
    print("\n🛠️ Testing Document Search Tool...")
    print("-" * 40)
    
    try:
        from src.vector_store import VectorStoreManager
        from src.tools import DocumentSearchTool
        
        # Setup vector store
        vm = VectorStoreManager()
        vm.load_vectorstore()
        
        # Create tool
        search_tool = DocumentSearchTool(vm)
        
        # Test tool
        result = search_tool._run("Python programming", k=2)
        print("Tool result:")
        print(result[:500] + "..." if len(result) > 500 else result)
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def main():
    print("🧪 Vector Store Debug Session")
    print("=" * 50)
    
    # Test vector search
    success1 = test_vector_search()
    
    # Test document search tool
    success2 = test_document_search_tool()
    
    print("\n" + "=" * 50)
    print("📊 Results:")
    print(f"Vector Search: {'✅ PASS' if success1 else '❌ FAIL'}")
    print(f"Search Tool: {'✅ PASS' if success2 else '❌ FAIL'}")
    
    if success1 and success2:
        print("\n🎉 Vector store is working correctly!")
    else:
        print("\n⚠️ There are issues with vector store functionality")

if __name__ == "__main__":
    main()
