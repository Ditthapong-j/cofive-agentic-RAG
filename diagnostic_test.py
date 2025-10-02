#!/usr/bin/env python3
"""
Simple test to check ChatOpenAI initialization
"""
import os
import sys

# Add src to path
sys.path.append('src')

def test_chatopenai():
    """Test ChatOpenAI initialization with different approaches"""
    print("🧪 Testing ChatOpenAI initialization...")
    
    # Test 1: Import and create without actual API call
    try:
        from langchain.chat_models import ChatOpenAI
        print("✅ Successfully imported ChatOpenAI")
        
        # Test with model_name (current approach)
        try:
            llm = ChatOpenAI(model_name="gpt-4o-mini", temperature=0.7)
            print("✅ ChatOpenAI created with model_name parameter")
            return True
        except Exception as e:
            print(f"❌ ChatOpenAI with model_name failed: {e}")
            
            # Test with model parameter
            try:
                llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.7) 
                print("✅ ChatOpenAI created with model parameter")
                return True
            except Exception as e2:
                print(f"❌ ChatOpenAI with model failed: {e2}")
                
    except ImportError as e:
        print(f"❌ Import failed: {e}")
        
    return False

def test_agentic_rag():
    """Test AgenticRAG initialization"""
    try:
        from src.vector_store import VectorStoreManager
        from src.agentic_rag import AgenticRAG
        
        print("🧪 Testing AgenticRAG...")
        
        # Create vector store manager
        vm = VectorStoreManager()
        print("✅ VectorStoreManager created")
        
        # Try to create AgenticRAG (will fail without API key but shouldn't have field errors)
        try:
            rag = AgenticRAG(vm)
            print("✅ AgenticRAG created successfully")
            return True
        except Exception as e:
            if "model" in str(e) and "field" in str(e):
                print(f"❌ Still has model field error: {e}")
                return False
            else:
                print(f"✅ No model field error (other error expected): {type(e).__name__}")
                return True
                
    except Exception as e:
        print(f"❌ AgenticRAG test failed: {e}")
        return False

if __name__ == "__main__":
    print("🔧 ChatOpenAI Error Diagnostic Test")
    print("=" * 50)
    
    test1 = test_chatopenai()
    test2 = test_agentic_rag()
    
    print("\n" + "=" * 50)
    if test1 and test2:
        print("🎉 ALL TESTS PASSED!")
        print("✅ ChatOpenAI error should be fixed")
    else:
        print("❌ Some tests failed")
        print("💡 Need further investigation")
