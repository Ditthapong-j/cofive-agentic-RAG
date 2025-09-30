#!/usr/bin/env python3
"""
Comprehensive API Testing Script for Agentic RAG System
Tests all endpoints with various scenarios including success and error cases
"""

import requests
import json
import time
import os
import sys
from pathlib import Path
from typing import Dict, Any
import argparse

class AgenticRAGAPITester:
    def __init__(self, base_url: str = "http://localhost:8003"):
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
        self.test_results = []
        
    def log_test(self, test_name: str, success: bool, details: str = "", response_data: Any = None):
        """Log test results"""
        result = {
            "test": test_name,
            "success": success,
            "details": details,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "response_data": response_data
        }
        self.test_results.append(result)
        
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}")
        if details:
            print(f"    {details}")
        if not success and response_data:
            print(f"    Response: {response_data}")
        print()
    
    def test_health_endpoint(self):
        """Test /health endpoint"""
        try:
            response = self.session.get(f"{self.base_url}/health")
            if response.status_code == 200:
                data = response.json()
                if "status" in data and data["status"] == "healthy":
                    self.log_test("Health Check", True, f"Status: {data['status']}")
                else:
                    self.log_test("Health Check", False, "Invalid response format", data)
            else:
                self.log_test("Health Check", False, f"HTTP {response.status_code}", response.text)
        except Exception as e:
            self.log_test("Health Check", False, f"Exception: {str(e)}")
    
    def test_status_endpoint(self):
        """Test /status endpoint"""
        try:
            response = self.session.get(f"{self.base_url}/status")
            if response.status_code == 200:
                data = response.json()
                required_fields = ["status", "document_count", "agent_ready", "api_key_configured"]
                if all(field in data for field in required_fields):
                    self.log_test("System Status", True, 
                                f"Status: {data['status']}, Docs: {data['document_count']}, "
                                f"Agent Ready: {data['agent_ready']}, API Key: {data['api_key_configured']}")
                else:
                    self.log_test("System Status", False, "Missing required fields", data)
            else:
                self.log_test("System Status", False, f"HTTP {response.status_code}", response.text)
        except Exception as e:
            self.log_test("System Status", False, f"Exception: {str(e)}")
    
    def test_models_endpoint(self):
        """Test /models endpoint"""
        try:
            response = self.session.get(f"{self.base_url}/models")
            if response.status_code == 200:
                data = response.json()
                if "models" in data and "default" in data and isinstance(data["models"], list):
                    self.log_test("Available Models", True, 
                                f"Models: {len(data['models'])}, Default: {data['default']}")
                else:
                    self.log_test("Available Models", False, "Invalid response format", data)
            else:
                self.log_test("Available Models", False, f"HTTP {response.status_code}", response.text)
        except Exception as e:
            self.log_test("Available Models", False, f"Exception: {str(e)}")
    
    def test_upload_endpoint(self):
        """Test /upload endpoint with various file types"""
        test_files_dir = Path(__file__).parent / "test_files"
        
        # Test with no files
        try:
            response = self.session.post(f"{self.base_url}/upload", files={})
            if response.status_code == 422:  # FastAPI validation error for missing files
                self.log_test("Upload - No Files", True, "Correctly rejected empty upload")
            else:
                self.log_test("Upload - No Files", False, f"Expected 422, got {response.status_code}")
        except Exception as e:
            self.log_test("Upload - No Files", False, f"Exception: {str(e)}")
        
        # Test with valid files
        if test_files_dir.exists():
            files_to_upload = []
            for file_path in test_files_dir.glob("*"):
                if file_path.is_file() and file_path.suffix.lower() in ['.txt', '.md', '.pdf']:
                    files_to_upload.append(('files', (file_path.name, open(file_path, 'rb'), 'text/plain')))
            
            if files_to_upload:
                try:
                    response = self.session.post(f"{self.base_url}/upload", files=files_to_upload)
                    
                    # Close file handles
                    for _, (_, file_handle, _) in files_to_upload:
                        file_handle.close()
                    
                    if response.status_code == 200:
                        data = response.json()
                        if data.get("success"):
                            self.log_test("Upload - Valid Files", True, 
                                        f"Processed: {data['files_processed']}, Total docs: {data['total_documents']}")
                        else:
                            self.log_test("Upload - Valid Files", False, "Upload not successful", data)
                    else:
                        self.log_test("Upload - Valid Files", False, f"HTTP {response.status_code}", response.text)
                except Exception as e:
                    self.log_test("Upload - Valid Files", False, f"Exception: {str(e)}")
            else:
                self.log_test("Upload - Valid Files", False, "No test files found")
        else:
            self.log_test("Upload - Valid Files", False, "Test files directory not found")
        
        # Test with invalid file type
        try:
            invalid_file = ('files', ('test.xyz', b'invalid content', 'application/octet-stream'))
            response = self.session.post(f"{self.base_url}/upload", files=[invalid_file])
            if response.status_code == 200:
                data = response.json()
                if data.get("files_processed", 0) == 0:
                    self.log_test("Upload - Invalid File Type", True, "Correctly ignored invalid file type")
                else:
                    self.log_test("Upload - Invalid File Type", False, "Should not process invalid file type", data)
            else:
                self.log_test("Upload - Invalid File Type", False, f"HTTP {response.status_code}", response.text)
        except Exception as e:
            self.log_test("Upload - Invalid File Type", False, f"Exception: {str(e)}")
    
    def test_initialize_endpoint(self):
        """Test /initialize endpoint"""
        # Test initialization without documents
        try:
            response = self.session.post(f"{self.base_url}/reset")
            response = self.session.post(f"{self.base_url}/initialize")
            if response.status_code == 400:
                self.log_test("Initialize - No Documents", True, "Correctly rejected initialization without documents")
            else:
                self.log_test("Initialize - No Documents", False, f"Expected 400, got {response.status_code}")
        except Exception as e:
            self.log_test("Initialize - No Documents", False, f"Exception: {str(e)}")
        
        # Upload documents first, then test initialization
        self.test_upload_endpoint()
        
        # Test normal initialization
        try:
            response = self.session.post(f"{self.base_url}/initialize", 
                                       json={"model": "gpt-3.5-turbo", "temperature": 0.1})
            if response.status_code == 200:
                data = response.json()
                if data.get("success") and data.get("agent_ready"):
                    self.log_test("Initialize - Normal", True, f"Agent ready: {data['agent_ready']}")
                else:
                    self.log_test("Initialize - Normal", False, "Initialization failed", data)
            else:
                self.log_test("Initialize - Normal", False, f"HTTP {response.status_code}", response.text)
        except Exception as e:
            self.log_test("Initialize - Normal", False, f"Exception: {str(e)}")
        
        # Test with different model
        try:
            response = self.session.post(f"{self.base_url}/initialize", 
                                       json={"model": "gpt-4", "temperature": 0.5})
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    self.log_test("Initialize - Different Model", True, "Successfully initialized with different model")
                else:
                    self.log_test("Initialize - Different Model", False, "Failed with different model", data)
            else:
                self.log_test("Initialize - Different Model", False, f"HTTP {response.status_code}", response.text)
        except Exception as e:
            self.log_test("Initialize - Different Model", False, f"Exception: {str(e)}")
    
    def test_query_endpoint(self):
        """Test /query endpoint"""
        # Test query without agent initialization
        try:
            response = self.session.post(f"{self.base_url}/reset")
            query_data = {"query": "What is the Agentic RAG system?"}
            response = self.session.post(f"{self.base_url}/query", json=query_data)
            if response.status_code == 400:
                self.log_test("Query - No Agent", True, "Correctly rejected query without agent")
            else:
                self.log_test("Query - No Agent", False, f"Expected 400, got {response.status_code}")
        except Exception as e:
            self.log_test("Query - No Agent", False, f"Exception: {str(e)}")
        
        # Setup system for queries
        self.test_upload_endpoint()
        self.test_initialize_endpoint()
        
        # Test valid query
        test_queries = [
            "What is the Agentic RAG system?",
            "What file formats are supported?",
            "How does Python work?",
            "What are the key features of machine learning?",
            "Explain vector databases"
        ]
        
        for query in test_queries:
            try:
                query_data = {
                    "query": query,
                    "model": "gpt-3.5-turbo",
                    "temperature": 0.1
                }
                response = self.session.post(f"{self.base_url}/query", json=query_data)
                if response.status_code == 200:
                    data = response.json()
                    if data.get("success") and data.get("answer"):
                        self.log_test(f"Query - '{query[:30]}...'", True, 
                                    f"Response time: {data.get('processing_time', 0):.2f}s")
                    else:
                        self.log_test(f"Query - '{query[:30]}...'", False, "No answer received", data)
                else:
                    self.log_test(f"Query - '{query[:30]}...'", False, f"HTTP {response.status_code}", response.text)
            except Exception as e:
                self.log_test(f"Query - '{query[:30]}...'", False, f"Exception: {str(e)}")
        
        # Test query with invalid parameters
        try:
            invalid_query = {"query": ""}  # Empty query
            response = self.session.post(f"{self.base_url}/query", json=invalid_query)
            if response.status_code == 422:  # Validation error
                self.log_test("Query - Empty Query", True, "Correctly rejected empty query")
            else:
                self.log_test("Query - Empty Query", False, f"Expected 422, got {response.status_code}")
        except Exception as e:
            self.log_test("Query - Empty Query", False, f"Exception: {str(e)}")
        
        # Test query with invalid temperature
        try:
            invalid_query = {"query": "test", "temperature": 5.0}  # Invalid temperature
            response = self.session.post(f"{self.base_url}/query", json=invalid_query)
            if response.status_code == 422:  # Validation error
                self.log_test("Query - Invalid Temperature", True, "Correctly rejected invalid temperature")
            else:
                self.log_test("Query - Invalid Temperature", False, f"Expected 422, got {response.status_code}")
        except Exception as e:
            self.log_test("Query - Invalid Temperature", False, f"Exception: {str(e)}")
    
    def test_reset_endpoint(self):
        """Test /reset endpoint"""
        try:
            response = self.session.post(f"{self.base_url}/reset")
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    self.log_test("System Reset", True, data.get("message", "Reset successful"))
                else:
                    self.log_test("System Reset", False, "Reset failed", data)
            else:
                self.log_test("System Reset", False, f"HTTP {response.status_code}", response.text)
        except Exception as e:
            self.log_test("System Reset", False, f"Exception: {str(e)}")
    
    def test_invalid_endpoints(self):
        """Test invalid endpoints"""
        invalid_endpoints = [
            "/nonexistent",
            "/upload/invalid",
            "/query/test"
        ]
        
        for endpoint in invalid_endpoints:
            try:
                response = self.session.get(f"{self.base_url}{endpoint}")
                if response.status_code == 404:
                    self.log_test(f"Invalid Endpoint - {endpoint}", True, "Correctly returned 404")
                else:
                    self.log_test(f"Invalid Endpoint - {endpoint}", False, f"Expected 404, got {response.status_code}")
            except Exception as e:
                self.log_test(f"Invalid Endpoint - {endpoint}", False, f"Exception: {str(e)}")
    
    def run_all_tests(self):
        """Run all API tests"""
        print("🚀 Starting Agentic RAG API Tests")
        print("=" * 50)
        
        start_time = time.time()
        
        # Basic connectivity tests
        print("\n📡 Testing Basic Connectivity")
        self.test_health_endpoint()
        self.test_status_endpoint()
        self.test_models_endpoint()
        
        # Core functionality tests
        print("\n📁 Testing Document Upload")
        self.test_upload_endpoint()
        
        print("\n🤖 Testing Agent Initialization")
        self.test_initialize_endpoint()
        
        print("\n💬 Testing Query Processing")
        self.test_query_endpoint()
        
        print("\n🔄 Testing System Reset")
        self.test_reset_endpoint()
        
        print("\n🚫 Testing Invalid Endpoints")
        self.test_invalid_endpoints()
        
        # Summary
        total_time = time.time() - start_time
        passed = sum(1 for result in self.test_results if result["success"])
        total = len(self.test_results)
        
        print("\n" + "=" * 50)
        print(f"📊 TEST SUMMARY")
        print(f"Total Tests: {total}")
        print(f"Passed: {passed}")
        print(f"Failed: {total - passed}")
        print(f"Success Rate: {(passed/total*100):.1f}%")
        print(f"Total Time: {total_time:.2f}s")
        
        if total - passed > 0:
            print("\n❌ FAILED TESTS:")
            for result in self.test_results:
                if not result["success"]:
                    print(f"  - {result['test']}: {result['details']}")
        
        return self.test_results
    
    def save_results(self, filename: str = None):
        """Save test results to JSON file"""
        if filename is None:
            filename = f"api_test_results_{int(time.time())}.json"
        
        with open(filename, 'w') as f:
            json.dump(self.test_results, f, indent=2)
        
        print(f"\n💾 Test results saved to: {filename}")

def main():
    parser = argparse.ArgumentParser(description="Test Agentic RAG API")
    parser.add_argument("--url", default="http://localhost:8003", help="API base URL")
    parser.add_argument("--save", action="store_true", help="Save results to JSON file")
    parser.add_argument("--output", help="Output filename for results")
    
    args = parser.parse_args()
    
    tester = AgenticRAGAPITester(args.url)
    
    try:
        results = tester.run_all_tests()
        
        if args.save:
            tester.save_results(args.output)
        
        # Exit with error code if any tests failed
        failed_tests = sum(1 for result in results if not result["success"])
        sys.exit(failed_tests)
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Tests interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n💥 Test runner error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()