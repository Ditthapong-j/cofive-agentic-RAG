#!/usr/bin/env python3
"""
Test CRUD Operations for Document Management
Tests all document CRUD endpoints including upload, list, get, delete operations
"""

import os
import sys
import requests
import json
import time
from pathlib import Path

# API Configuration
API_BASE_URL = "http://localhost:8003"
TEST_FILES_DIR = Path(__file__).parent / "test_files"

def create_test_files():
    """Create test files for upload testing"""
    TEST_FILES_DIR.mkdir(exist_ok=True)
    
    # Create a test text file
    with open(TEST_FILES_DIR / "test_document.txt", "w", encoding="utf-8") as f:
        f.write("""Test Document for CRUD Operations

This is a test document created for testing the CRUD operations of the Agentic RAG API.

Key Information:
- Document Type: Text file
- Purpose: Testing CRUD functionality
- Content: Sample text for processing
- Author: Test System
- Date: 2025-10-02

Features being tested:
1. Document upload
2. Document listing
3. Document retrieval
4. Document deletion
5. Bulk operations

This document contains various information that can be queried through the RAG system.
""")
    
    # Create another test file
    with open(TEST_FILES_DIR / "research_notes.md", "w", encoding="utf-8") as f:
        f.write("""# Research Notes

## Overview
These are sample research notes for testing the document management system.

## Key Findings
- CRUD operations are essential for document management
- Vector stores provide efficient similarity search
- AI agents can process multiple document types

## Methodology
1. Upload documents to the system
2. Process and chunk the content
3. Store embeddings in vector database
4. Enable querying through AI interface

## Conclusions
The system successfully handles multiple document formats and provides
comprehensive CRUD operations for effective document management.

## Future Work
- Implement selective vector store updates
- Add document versioning
- Enhance metadata management
""")

def test_health_check():
    """Test API health check"""
    print("🏥 Testing Health Check...")
    try:
        response = requests.get(f"{API_BASE_URL}/health")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Health check passed: {data['status']}")
            return True
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Health check error: {e}")
        return False

def test_system_status():
    """Test system status endpoint"""
    print("📊 Testing System Status...")
    try:
        response = requests.get(f"{API_BASE_URL}/status")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ System status: {data['status']}")
            print(f"   Documents: {data['document_count']}")
            print(f"   Agent ready: {data['agent_ready']}")
            print(f"   API key configured: {data['api_key_configured']}")
            return data
        else:
            print(f"❌ System status failed: {response.status_code}")
            return None
    except requests.exceptions.RequestException as e:
        print(f"❌ System status error: {e}")
        return None

def test_upload_documents():
    """Test document upload"""
    print("📤 Testing Document Upload...")
    
    create_test_files()
    
    uploaded_files = []
    test_files = [
        TEST_FILES_DIR / "test_document.txt",
        TEST_FILES_DIR / "research_notes.md"
    ]
    
    for file_path in test_files:
        if file_path.exists():
            try:
                with open(file_path, 'rb') as f:
                    files = {'files': (file_path.name, f, 'text/plain')}
                    response = requests.post(f"{API_BASE_URL}/upload", files=files)
                
                if response.status_code == 200:
                    data = response.json()
                    print(f"✅ Uploaded {file_path.name}")
                    print(f"   Files processed: {data['files_processed']}")
                    print(f"   Total documents: {data['total_documents']}")
                    uploaded_files.append(file_path.name)
                else:
                    print(f"❌ Upload failed for {file_path.name}: {response.status_code}")
                    print(f"   Response: {response.text}")
            except Exception as e:
                print(f"❌ Upload error for {file_path.name}: {e}")
    
    return uploaded_files

def test_list_documents():
    """Test listing all documents"""
    print("📋 Testing Document Listing...")
    try:
        response = requests.get(f"{API_BASE_URL}/documents")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Documents listed successfully")
            print(f"   Total count: {data['total_count']}")
            
            for i, doc in enumerate(data['documents'], 1):
                print(f"   {i}. {doc['filename']} (ID: {doc['id']})")
                print(f"      Type: {doc['file_type']}, Chunks: {doc['chunk_count']}")
                print(f"      Upload time: {doc['upload_time']}")
                if doc['content_preview']:
                    preview = doc['content_preview'][:100] + "..." if len(doc['content_preview']) > 100 else doc['content_preview']
                    print(f"      Preview: {preview}")
                print()
            
            return data['documents']
        else:
            print(f"❌ Document listing failed: {response.status_code}")
            return []
    except requests.exceptions.RequestException as e:
        print(f"❌ Document listing error: {e}")
        return []

def test_get_document_details(documents):
    """Test getting specific document details"""
    print("📄 Testing Document Details...")
    
    if not documents:
        print("❌ No documents available for detail testing")
        return
    
    # Test getting details for the first document
    doc_id = documents[0]['id']
    try:
        response = requests.get(f"{API_BASE_URL}/documents/{doc_id}")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Document details retrieved for {doc_id}")
            print(f"   Filename: {data['filename']}")
            print(f"   File type: {data['file_type']}")
            print(f"   File size: {data.get('file_size', 'Unknown')} bytes")
            print(f"   Chunk count: {data['chunk_count']}")
            print(f"   Upload time: {data['upload_time']}")
            if data['content_preview']:
                print(f"   Content preview: {data['content_preview'][:150]}...")
        else:
            print(f"❌ Document details failed: {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"❌ Document details error: {e}")

def test_initialize_agent():
    """Test agent initialization"""
    print("🤖 Testing Agent Initialization...")
    try:
        response = requests.post(f"{API_BASE_URL}/initialize", params={
            "model": "gpt-4o-mini",
            "temperature": 0.1
        })
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Agent initialized: {data['message']}")
            print(f"   Agent ready: {data['agent_ready']}")
            print(f"   Document count: {data['document_count']}")
            return True
        else:
            print(f"❌ Agent initialization failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Agent initialization error: {e}")
        return False

def test_query_documents():
    """Test querying documents"""
    print("💬 Testing Document Querying...")
    
    query_data = {
        "query": "What is the purpose of these test documents?",
        "model": "gpt-4o-mini",
        "temperature": 0.1
    }
    
    try:
        response = requests.post(
            f"{API_BASE_URL}/query",
            json=query_data,
            headers={"Content-Type": "application/json"}
        )
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Query successful")
            print(f"   Model used: {data['model_used']}")
            print(f"   Processing time: {data['processing_time']:.2f}s")
            print(f"   Answer: {data['answer'][:200]}...")
            if data['sources']:
                print(f"   Sources: {', '.join(data['sources'])}")
            return True
        else:
            print(f"❌ Query failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Query error: {e}")
        return False

def test_delete_document(documents):
    """Test deleting a specific document"""
    print("🗑️ Testing Document Deletion...")
    
    if not documents:
        print("❌ No documents available for deletion testing")
        return
    
    # Delete the first document
    doc_id = documents[0]['id']
    filename = documents[0]['filename']
    
    try:
        response = requests.delete(f"{API_BASE_URL}/documents/{doc_id}")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Document deleted successfully")
            print(f"   Deleted: {filename} (ID: {data['deleted_document_id']})")
            print(f"   Remaining documents: {data['remaining_count']}")
            return True
        else:
            print(f"❌ Document deletion failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Document deletion error: {e}")
        return False

def test_delete_all_documents():
    """Test deleting all documents"""
    print("🗑️ Testing Delete All Documents...")
    
    try:
        response = requests.delete(f"{API_BASE_URL}/documents")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ All documents deleted successfully")
            print(f"   Deleted count: {data.get('deleted_count', 'Unknown')}")
            return True
        else:
            print(f"❌ Delete all failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Delete all error: {e}")
        return False

def test_get_available_models():
    """Test getting available models"""
    print("🧠 Testing Available Models...")
    try:
        response = requests.get(f"{API_BASE_URL}/models")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Available models retrieved")
            print(f"   Default model: {data['default']}")
            print(f"   Available models: {', '.join(data['models'])}")
            if 'descriptions' in data:
                print("   Model descriptions:")
                for model, desc in data['descriptions'].items():
                    print(f"     {model}: {desc}")
            return True
        else:
            print(f"❌ Get models failed: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Get models error: {e}")
        return False

def cleanup_test_files():
    """Clean up test files"""
    if TEST_FILES_DIR.exists():
        for file_path in TEST_FILES_DIR.glob("*"):
            file_path.unlink()
        TEST_FILES_DIR.rmdir()
        print("🧹 Test files cleaned up")

def main():
    """Run comprehensive CRUD tests"""
    print("🚀 Starting Agentic RAG API CRUD Tests")
    print("=" * 50)
    
    # Health checks
    if not test_health_check():
        print("❌ API not available. Please start the server first.")
        return
    
    initial_status = test_system_status()
    print()
    
    # Document operations
    print("📄 Document CRUD Operations")
    print("-" * 30)
    
    # Upload documents
    uploaded_files = test_upload_documents()
    print()
    
    # List documents
    documents = test_list_documents()
    print()
    
    # Get document details
    if documents:
        test_get_document_details(documents)
        print()
    
    # Agent operations
    print("🤖 Agent Operations")
    print("-" * 20)
    
    # Initialize agent
    agent_ready = test_initialize_agent()
    print()
    
    # Query documents
    if agent_ready:
        test_query_documents()
        print()
    
    # System operations
    print("⚙️ System Operations")
    print("-" * 20)
    
    # Get available models
    test_get_available_models()
    print()
    
    # Deletion operations
    print("🗑️ Deletion Operations")
    print("-" * 22)
    
    # Delete specific document
    if documents:
        test_delete_document(documents)
        print()
        
        # List documents after deletion
        remaining_docs = test_list_documents()
        print()
    
    # Delete all documents
    test_delete_all_documents()
    print()
    
    # Verify all documents deleted
    final_docs = test_list_documents()
    final_status = test_system_status()
    print()
    
    # Cleanup
    cleanup_test_files()
    
    print("🎉 CRUD Tests Completed!")
    print("=" * 50)
    
    # Summary
    print("📊 Test Summary:")
    print(f"   Initial documents: {initial_status['document_count'] if initial_status else 'Unknown'}")
    print(f"   Files uploaded: {len(uploaded_files)}")
    print(f"   Final documents: {final_status['document_count'] if final_status else 'Unknown'}")
    print(f"   System status: {final_status['status'] if final_status else 'Unknown'}")

if __name__ == "__main__":
    main()