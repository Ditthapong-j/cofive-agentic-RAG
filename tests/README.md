# API Testing Guide

This directory contains comprehensive testing tools and documentation for the Agentic RAG API.

## 📁 Contents

### Test Files (`test_files/`)
- `sample_document.txt` - General information about the RAG system
- `ai_guide.md` - AI and machine learning concepts  
- `python_guide.txt` - Python programming guide

### Testing Scripts
- `test_api.py` - Comprehensive automated API testing
- `manual_test.py` - Interactive manual testing script

### Test Collections
- `Agentic_RAG_API.postman_collection.json` - Postman collection for API testing

## 🚀 Quick Start

### 1. Start the API Server
```bash
cd /Users/ditthapong/Desktop/cofive-agentic-RAG
python3 api_server.py
```

### 2. Run Automated Tests
```bash
cd tests
python3 test_api.py --save
```

### 3. Run Manual Tests
```bash
cd tests
python3 manual_test.py
```

## 📋 Test Coverage

### Endpoints Tested
- ✅ `GET /health` - Health check
- ✅ `GET /status` - System status  
- ✅ `GET /models` - Available models
- ✅ `POST /upload` - Document upload
- ✅ `POST /initialize` - Agent initialization
- ✅ `POST /query` - Document querying
- ✅ `POST /reset` - System reset

### Test Scenarios
- ✅ Success cases
- ✅ Error handling
- ✅ Validation errors
- ✅ Invalid endpoints
- ✅ File upload (various formats)
- ✅ Model configuration
- ✅ Temperature validation

## 🧪 Test Types

### Automated Testing (`test_api.py`)

**Features:**
- Complete endpoint coverage
- Error case testing
- Response validation
- Performance timing
- JSON result export
- Detailed logging

**Usage:**
```bash
# Basic testing
python3 test_api.py

# Save results to JSON
python3 test_api.py --save

# Custom API URL
python3 test_api.py --url http://localhost:8003

# Custom output file
python3 test_api.py --save --output my_results.json
```

**Output:**
```
🚀 Starting Agentic RAG API Tests
==================================================

📡 Testing Basic Connectivity
✅ PASS Health Check
✅ PASS System Status
✅ PASS Available Models

📁 Testing Document Upload
✅ PASS Upload - No Files
✅ PASS Upload - Valid Files
✅ PASS Upload - Invalid File Type

🤖 Testing Agent Initialization
✅ PASS Initialize - No Documents
✅ PASS Initialize - Normal
✅ PASS Initialize - Different Model

💬 Testing Query Processing
✅ PASS Query - 'What is the Agentic RAG system?...'
✅ PASS Query - 'What file formats are supported?...'

📊 TEST SUMMARY
Total Tests: 25
Passed: 25
Failed: 0
Success Rate: 100.0%
Total Time: 45.23s
```

### Manual Testing (`manual_test.py`)

**Features:**
- Interactive testing
- Step-by-step guidance
- Human verification
- Educational walkthrough

**Usage:**
```bash
python3 manual_test.py
```

### Postman Collection

**Features:**
- Visual testing interface
- Pre-built requests
- Automated test assertions
- Environment variables
- Collection runner support

**Usage:**
1. Import `Agentic_RAG_API.postman_collection.json` into Postman
2. Set environment variable `base_url` to `http://localhost:8003`
3. Run collection or individual requests

## 📊 Test Results

### Sample Test Report
```json
{
  "test": "Health Check",
  "success": true,
  "details": "Status: healthy",
  "timestamp": "2025-09-14 17:00:00",
  "response_data": {
    "status": "healthy",
    "timestamp": "2025-09-14T17:00:00.000000",
    "version": "1.0.0"
  }
}
```

## 🔧 Configuration

### Environment Variables
- `OPENAI_API_KEY` - Required for API functionality

### Test Configuration
- **Base URL**: `http://localhost:8003`
- **Timeout**: 30s for uploads, 60s for queries
- **Test Files**: Located in `test_files/` directory

## 📝 Adding New Tests

### Automated Tests
Add new test methods to `AgenticRAGAPITester` class:

```python
def test_new_endpoint(self):
    """Test new endpoint"""
    try:
        response = self.session.get(f"{self.base_url}/new-endpoint")
        if response.status_code == 200:
            self.log_test("New Endpoint", True, "Success")
        else:
            self.log_test("New Endpoint", False, f"HTTP {response.status_code}")
    except Exception as e:
        self.log_test("New Endpoint", False, f"Exception: {str(e)}")
```

### Postman Tests
Add new requests to the collection with test scripts:

```javascript
pm.test("Status code is 200", function () {
    pm.response.to.have.status(200);
});

pm.test("Response has required field", function () {
    var jsonData = pm.response.json();
    pm.expect(jsonData).to.have.property('field_name');
});
```

## 🐛 Troubleshooting

### Common Issues

1. **Connection Refused**
   ```
   Error: Connection refused
   ```
   **Solution**: Ensure API server is running on port 8003

2. **OpenAI API Key Missing**
   ```
   Error: OPENAI_API_KEY not found
   ```
   **Solution**: Set environment variable
   ```bash
   export OPENAI_API_KEY="your_key_here"
   ```

3. **File Upload Fails**
   ```
   Error: No files processed
   ```
   **Solution**: Check file paths and formats (PDF, TXT, MD only)

4. **Agent Not Ready**
   ```
   Error: Agent not ready
   ```
   **Solution**: Upload documents first, then initialize

### Debug Mode

Enable verbose logging for troubleshooting:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## 📈 Performance Benchmarks

### Expected Response Times
- Health check: < 100ms
- Status check: < 200ms
- Document upload: 1-10s (depending on size)
- Agent initialization: 2-5s
- Query processing: 1-5s

### Load Testing
For load testing, use tools like:
- Apache Bench (ab)
- wrk
- Postman Collection Runner

## 🔍 Validation

### Response Validation
All tests validate:
- HTTP status codes
- Response structure
- Required fields
- Data types
- Business logic

### Error Handling
Tests cover:
- Invalid inputs
- Missing parameters
- Server errors
- Network issues
- Timeout scenarios

## 📚 Documentation

- **API Documentation**: `/API_DOCUMENTATION.md`
- **OpenAPI/Swagger**: `http://localhost:8003/docs`
- **ReDoc**: `http://localhost:8003/redoc`

## 🎯 Test Strategy

### Test Pyramid
1. **Unit Tests**: Individual component testing
2. **Integration Tests**: API endpoint testing (this directory)
3. **E2E Tests**: Full workflow testing
4. **Performance Tests**: Load and stress testing

### Testing Philosophy
- Test early and often
- Cover happy paths and edge cases
- Validate both success and failure scenarios
- Maintain test documentation
- Automate where possible

---

**Last Updated**: September 14, 2025  
**Version**: 1.0.0