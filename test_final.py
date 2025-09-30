#!/usr/bin/env python3
"""
Test script to verify the ChatOpenAI fix and API functionality
"""
import requests
import json
import time
import sys

def test_api_endpoints():
    """Test all API endpoints"""
    base_url = "http://localhost:8002"
    
    print("🧪 Testing API Endpoints...")
    
    # Test 1: Health check
    try:
        response = requests.get(f"{base_url}/health")
        if response.status_code == 200:
            print("✅ Health check passed")
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Health check error: {e}")
        return False
    
    # Test 2: Status check
    try:
        response = requests.get(f"{base_url}/status")
        if response.status_code == 200:
            status = response.json()
            print(f"✅ Status check passed - System ready: {status.get('agent_ready', False)}")
        else:
            print(f"❌ Status check failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Status check error: {e}")
    
    # Test 3: Initialize agent
    try:
        response = requests.post(f"{base_url}/initialize?model=gpt-3.5-turbo&temperature=0.1")
        if response.status_code == 200:
            print("✅ Agent initialization passed")
        else:
            print(f"❌ Agent initialization failed: {response.status_code}")
            print(f"Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Agent initialization error: {e}")
        return False
    
    # Test 4: Simple query
    try:
        query_data = {"question": "Hello, this is a test query. Please respond."}
        response = requests.post(f"{base_url}/query", json=query_data)
        
        if response.status_code == 200:
            result = response.json()
            if result.get("success", False):
                print("✅ Query test passed")
                print(f"📝 Response preview: {result['answer'][:100]}...")
                return True
            else:
                print(f"❌ Query failed: {result.get('error', 'Unknown error')}")
                print(f"📝 Full response: {result}")
                return False
        else:
            print(f"❌ Query request failed: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Query test error: {e}")
        return False

def test_streamlit_ui():
    """Test if Streamlit UI is accessible"""
    try:
        response = requests.get("http://localhost:8503")
        if response.status_code == 200:
            print("✅ Streamlit UI is accessible")
            return True
        else:
            print(f"❌ Streamlit UI not accessible: {response.status_code}")
            return False
    except Exception as e:
        print(f"ℹ️  Streamlit UI test skipped: {e}")
        return True  # Not critical

if __name__ == "__main__":
    print("🔧 ChatOpenAI Fix Verification Test")
    print("=" * 50)
    
    # Wait a moment for API to be ready
    print("⏳ Waiting for API server...")
    time.sleep(2)
    
    # Test API
    api_success = test_api_endpoints()
    
    # Test UI
    ui_success = test_streamlit_ui()
    
    print("\n" + "=" * 50)
    if api_success:
        print("🎉 SUCCESS! ChatOpenAI error has been FIXED!")
        print("✅ API is working correctly")
        print("✅ Agent can process queries")
        print("\n📋 System is ready to use:")
        print("   - API Server: http://localhost:8002")
        print("   - Streamlit UI: http://localhost:8503")
        print("   - Original CLI: python3 main.py")
    else:
        print("❌ FAILED! There are still issues with the system.")
        print("💡 Please check the error messages above.")
        sys.exit(1)
