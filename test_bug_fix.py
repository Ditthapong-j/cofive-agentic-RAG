"""
Test script to verify bug fix for get_document_count error
"""
import requests
import json

BASE_URL = "http://localhost:8003"

def test_query_without_filter():
    """Test query without any filters - this was causing the error"""
    print("\n" + "="*60)
    print("🧪 Test 1: Query WITHOUT filters (Bug was here)")
    print("="*60)
    
    url = f"{BASE_URL}/query"
    data = {
        "query": "What documents do we have?",
        "model": "gpt-4o-mini",
        "temperature": 0.1
    }
    
    try:
        response = requests.post(url, json=data)
        result = response.json()
        
        if result.get('success'):
            print("✅ SUCCESS: Query processed without error!")
            print(f"   Answer: {result['answer'][:100]}...")
            print(f"   Chunks: {result.get('chunks_retrieved', 0)}")
        else:
            print(f"❌ FAILED: {result.get('error', 'Unknown error')}")
            
    except Exception as e:
        print(f"❌ ERROR: {e}")

def test_query_with_tags():
    """Test query with tags filter"""
    print("\n" + "="*60)
    print("🧪 Test 2: Query WITH tag filter")
    print("="*60)
    
    url = f"{BASE_URL}/query"
    data = {
        "query": "What are the research findings?",
        "model": "gpt-4o-mini",
        "temperature": 0.1,
        "tags": ["research"]
    }
    
    try:
        response = requests.post(url, json=data)
        result = response.json()
        
        if result.get('success'):
            print("✅ SUCCESS: Query with tags works!")
            print(f"   Answer: {result['answer'][:100]}...")
            print(f"   Chunks: {result.get('chunks_retrieved', 0)}")
        else:
            print(f"⚠️  No results: {result.get('error', 'No error')}")
            
    except Exception as e:
        print(f"❌ ERROR: {e}")

def test_query_with_metadata():
    """Test query with metadata filter"""
    print("\n" + "="*60)
    print("🧪 Test 3: Query WITH metadata filter")
    print("="*60)
    
    url = f"{BASE_URL}/query"
    data = {
        "query": "What did we find in 2024?",
        "model": "gpt-4o-mini",
        "temperature": 0.1,
        "metadata_filter": {"year": 2024}
    }
    
    try:
        response = requests.post(url, json=data)
        result = response.json()
        
        if result.get('success'):
            print("✅ SUCCESS: Query with metadata works!")
            print(f"   Answer: {result['answer'][:100]}...")
            print(f"   Chunks: {result.get('chunks_retrieved', 0)}")
        else:
            print(f"⚠️  No results: {result.get('error', 'No error')}")
            
    except Exception as e:
        print(f"❌ ERROR: {e}")

def test_simple_queries():
    """Test various simple queries"""
    print("\n" + "="*60)
    print("🧪 Test 4: Multiple simple queries")
    print("="*60)
    
    queries = [
        "What is the main topic?",
        "Summarize the key points",
        "What are the conclusions?",
        "Tell me about the research"
    ]
    
    url = f"{BASE_URL}/query"
    
    success_count = 0
    for query in queries:
        try:
            data = {
                "query": query,
                "model": "gpt-4o-mini",
                "temperature": 0.1
            }
            
            response = requests.post(url, json=data)
            result = response.json()
            
            if result.get('success'):
                success_count += 1
                print(f"✅ '{query}' - OK")
            else:
                print(f"❌ '{query}' - Failed: {result.get('error', '')}")
                
        except Exception as e:
            print(f"❌ '{query}' - Error: {e}")
    
    print(f"\n📊 Results: {success_count}/{len(queries)} queries successful")

def main():
    print("\n" + "🔧"*30)
    print("  BUG FIX VERIFICATION TEST")
    print("  Testing: get_document_count() error fix")
    print("🔧"*30)
    
    try:
        # Test 1: The main bug - query without filters
        test_query_without_filter()
        
        # Test 2: Query with filters (should still work)
        test_query_with_tags()
        
        # Test 3: Query with metadata
        test_query_with_metadata()
        
        # Test 4: Multiple simple queries
        test_simple_queries()
        
        print("\n" + "="*60)
        print("✅ ALL TESTS COMPLETED")
        print("="*60)
        print("\nIf Test 1 passed, the bug is fixed! 🎉")
        print("The error 'get_document_count() takes 0 positional arguments'")
        print("should no longer occur.")
        
    except requests.exceptions.ConnectionError:
        print("\n❌ ERROR: Cannot connect to API server")
        print("Make sure the server is running: python api_server.py")
    except Exception as e:
        print(f"\n❌ ERROR: {e}")

if __name__ == "__main__":
    main()
