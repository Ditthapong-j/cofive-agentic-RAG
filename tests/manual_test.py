#!/usr/bin/env python3
"""
Manual API Testing - Simple version
"""

import requests
import json
import time

def test_api_manually():
    base_url = "http://localhost:8003"
    
    print("🚀 Manual API Testing")
    print("=" * 40)
    
    # Start server manually first
    print("\n📌 Make sure API server is running on http://localhost:8003")
    print("📌 Run: python3 api_server.py")
    input("📌 Press Enter when server is ready...")
    
    # Test 1: Health Check
    print("\n1. Testing Health Check...")
    try:
        response = requests.get(f"{base_url}/health", timeout=5)
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.json()}")
    except Exception as e:
        print(f"   Error: {e}")
    
    # Test 2: System Status
    print("\n2. Testing System Status...")
    try:
        response = requests.get(f"{base_url}/status", timeout=5)
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.json()}")
    except Exception as e:
        print(f"   Error: {e}")
    
    # Test 3: Available Models
    print("\n3. Testing Available Models...")
    try:
        response = requests.get(f"{base_url}/models", timeout=5)
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.json()}")
    except Exception as e:
        print(f"   Error: {e}")
    
    # Test 4: Upload Documents
    print("\n4. Testing Document Upload...")
    try:
        # Create a simple test file
        test_content = "This is a test document for API testing. It contains information about testing procedures and API functionality."
        
        files = {
            'files': ('test.txt', test_content, 'text/plain')
        }
        
        response = requests.post(f"{base_url}/upload", files=files, timeout=30)
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.json()}")
    except Exception as e:
        print(f"   Error: {e}")
    
    # Test 5: Initialize Agent
    print("\n5. Testing Agent Initialization...")
    try:
        data = {
            "model": "gpt-3.5-turbo",
            "temperature": 0.1
        }
        response = requests.post(f"{base_url}/initialize", json=data, timeout=30)
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.json()}")
    except Exception as e:
        print(f"   Error: {e}")
    
    # Test 6: Query
    print("\n6. Testing Query...")
    try:
        data = {
            "query": "What is this document about?",
            "model": "gpt-3.5-turbo",
            "temperature": 0.1
        }
        response = requests.post(f"{base_url}/query", json=data, timeout=60)
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.json()}")
    except Exception as e:
        print(f"   Error: {e}")
    
    # Test 7: Reset System
    print("\n7. Testing System Reset...")
    try:
        response = requests.post(f"{base_url}/reset", timeout=10)
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.json()}")
    except Exception as e:
        print(f"   Error: {e}")
    
    print("\n✅ Manual testing completed!")

if __name__ == "__main__":
    test_api_manually()