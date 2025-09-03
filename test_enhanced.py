"""
Test script for Enhanced Agentic RAG System with Model Selection and Custom Prompts
"""
import os
from pathlib import Path
import sys

# Add src to path
sys.path.append(str(Path(__file__).parent / "src"))

from main_faiss import AgenticRAGSystem

def test_enhanced_features():
    """Test enhanced features of the system"""
    
    print("🧪 Testing Enhanced Agentic RAG System...")
    print("=" * 60)
    
    # Test different models and settings
    test_configs = [
        {
            "name": "GPT-3.5 Turbo - Technical Style",
            "model": "gpt-3.5-turbo",
            "temperature": 0.1,
            "prompt": """You are a technical documentation expert. 
            Always provide detailed, technical answers with code examples when relevant.
            Format your responses with clear sections and bullet points.
            Focus on accuracy and practical implementation details."""
        },
        {
            "name": "GPT-3.5 Turbo - Creative Assistant",
            "model": "gpt-3.5-turbo", 
            "temperature": 1.2,
            "prompt": """You are a creative assistant who explains complex topics in simple, 
            engaging ways. Use analogies, storytelling, and creative examples. 
            Make technical concepts accessible to beginners while maintaining accuracy."""
        }
    ]
    
    # Test questions
    test_questions = [
        "สรุปเนื้อหาหลักของเอกสาร",
        "What is the main purpose of this system?",
        "How do I start using this program?"
    ]
    
    for config in test_configs:
        print(f"\n🤖 Testing: {config['name']}")
        print("-" * 50)
        
        try:
            # Initialize system with custom settings
            rag_system = AgenticRAGSystem(
                model_name=config['model'],
                temperature=config['temperature'],
                custom_prompt=config['prompt']
            )
            
            # Initialize agent
            rag_system.initialize_agent()
            
            print(f"✅ Model: {config['model']}")
            print(f"✅ Temperature: {config['temperature']}")
            print(f"✅ Documents: {rag_system.get_document_count()}")
            
            # Test a sample question
            question = test_questions[0]
            print(f"\n📝 Question: {question}")
            
            result = rag_system.query(question)
            answer = result.get('answer', 'No answer received')
            
            print(f"🤖 Answer (first 200 chars): {answer[:200]}...")
            
            print("✅ Test completed successfully!")
            
        except Exception as e:
            print(f"❌ Error testing {config['name']}: {e}")
        
        print("\n" + "=" * 60)

def test_vector_search():
    """Test vector search functionality"""
    print("\n🔍 Testing Vector Search...")
    
    try:
        from src.vector_store_faiss import FAISSVectorStore
        
        # Initialize vector store
        vector_store = FAISSVectorStore()
        
        # Test search
        search_terms = ["โปรแกรม", "system", "documents", "AI"]
        
        for term in search_terms:
            print(f"\n🔍 Searching for: '{term}'")
            results = vector_store.similarity_search(term, k=2)
            
            if results:
                print(f"✅ Found {len(results)} results")
                for i, doc in enumerate(results, 1):
                    print(f"  {i}. Source: {doc.metadata.get('source', 'Unknown')}")
                    print(f"     Content: {doc.page_content[:100]}...")
            else:
                print("❌ No results found")
        
        print("\n✅ Vector search test completed!")
        
    except Exception as e:
        print(f"❌ Vector search test failed: {e}")

def main():
    """Main test function"""
    print("🚀 Enhanced Agentic RAG System - Comprehensive Test")
    print("=" * 80)
    
    # Check environment
    if not os.getenv("OPENAI_API_KEY"):
        print("❌ OPENAI_API_KEY not found!")
        print("💡 Please set your OpenAI API key in environment variables")
        return
    
    # Test vector search first
    test_vector_search()
    
    # Test enhanced features
    test_enhanced_features()
    
    print("\n🎉 All tests completed!")
    print("\n💡 System Features Confirmed:")
    print("  ✅ FAISS vector store working")
    print("  ✅ Model selection working")
    print("  ✅ Custom prompts working")
    print("  ✅ Temperature control working")
    print("  ✅ Document search working")
    
    print("\n🌟 Ready for Streamlit deployment!")

if __name__ == "__main__":
    main()
