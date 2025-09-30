# Agentic RAG API Documentation

## Overview

The Agentic RAG (Retrieval-Augmented Generation) API is a FastAPI-based web service that provides intelligent document question-answering capabilities. The system combines vector search with large language models to create a conversational AI agent that can answer questions based on uploaded documents.

## Features

- 📁 **Document Upload**: Support for PDF, TXT, and MD files
- 🔍 **Vector Search**: Efficient semantic search using ChromaDB
- 🤖 **AI Agent**: LangChain-powered conversational agent
- 🌐 **REST API**: Complete RESTful web service
- 🔧 **Model Configuration**: Support for multiple OpenAI models
- 🛡️ **Error Handling**: Comprehensive error handling and validation

## Quick Start

### Prerequisites

1. Python 3.8+
2. OpenAI API key
3. Required dependencies (see requirements.txt)

### Installation

```bash
# Clone the repository
git clone <repository_url>
cd cofive-agentic-RAG

# Install dependencies
pip install -r requirements.txt

# Set environment variable
export OPENAI_API_KEY="your_openai_api_key_here"

# Start the server
python3 api_server.py
```

### Basic Usage

1. **Start the server** - Run `python3 api_server.py`
2. **Upload documents** - POST to `/upload` with your documents
3. **Initialize agent** - POST to `/initialize` to prepare the AI agent
4. **Ask questions** - POST to `/query` with your questions

## API Endpoints

### Base URL
```
http://localhost:8003
```

---

### 1. Health Check

**GET** `/health`

Check if the API is running and healthy.

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2025-09-14T17:00:00.000000",
  "version": "1.0.0"
}
```

**Example:**
```bash
curl -X GET "http://localhost:8003/health"
```

---

### 2. System Status

**GET** `/status`

Get the current system status and configuration.

**Response:**
```json
{
  "status": "ready",
  "document_count": 5,
  "agent_ready": true,
  "api_key_configured": true,
  "version": "1.0.0"
}
```

**Fields:**
- `status`: System status (`"needs_documents"` or `"ready"`)
- `document_count`: Number of documents in the vector store
- `agent_ready`: Whether the AI agent is initialized
- `api_key_configured`: Whether OpenAI API key is set

**Example:**
```bash
curl -X GET "http://localhost:8003/status"
```

---

### 3. Available Models

**GET** `/models`

Get list of available AI models.

**Response:**
```json
{
  "models": [
    "gpt-3.5-turbo",
    "gpt-4",
    "gpt-4-turbo",
    "gpt-4o",
    "gpt-4o-mini"
  ],
  "default": "gpt-3.5-turbo"
}
```

**Example:**
```bash
curl -X GET "http://localhost:8003/models"
```

---

### 4. Upload Documents

**POST** `/upload`

Upload documents to the system for processing.

**Request:**
- **Content-Type**: `multipart/form-data`
- **Body**: One or more files with field name `files`

**Supported File Types:**
- `.pdf` - PDF documents
- `.txt` - Plain text files
- `.md` - Markdown files

**Response:**
```json
{
  "success": true,
  "message": "Successfully processed 3 files",
  "files_processed": 3,
  "total_documents": 15
}
```

**Example:**
```bash
curl -X POST "http://localhost:8003/upload" \
  -F "files=@document1.pdf" \
  -F "files=@document2.txt" \
  -F "files=@guide.md"
```

**Python Example:**
```python
import requests

files = [
    ('files', ('doc1.txt', open('doc1.txt', 'rb'), 'text/plain')),
    ('files', ('doc2.pdf', open('doc2.pdf', 'rb'), 'application/pdf'))
]

response = requests.post('http://localhost:8003/upload', files=files)
print(response.json())
```

---

### 5. Initialize Agent

**POST** `/initialize`

Initialize the AI agent with uploaded documents.

**Request Body:**
```json
{
  "model": "gpt-3.5-turbo",
  "temperature": 0.1
}
```

**Parameters:**
- `model` (optional): AI model to use (default: "gpt-3.5-turbo")
- `temperature` (optional): Model temperature 0.0-2.0 (default: 0.1)

**Response:**
```json
{
  "success": true,
  "message": "Agent initialized successfully",
  "agent_ready": true,
  "document_count": 5
}
```

**Example:**
```bash
curl -X POST "http://localhost:8003/initialize" \
  -H "Content-Type: application/json" \
  -d '{"model": "gpt-4", "temperature": 0.2}'
```

**Error Response (No Documents):**
```json
{
  "detail": "No documents available. Upload documents first."
}
```

---

### 6. Query Documents

**POST** `/query`

Ask questions about the uploaded documents.

**Request Body:**
```json
{
  "query": "What is the main topic of the documents?",
  "model": "gpt-3.5-turbo",
  "temperature": 0.1
}
```

**Parameters:**
- `query`: The question to ask (required)
- `model` (optional): AI model to use (default: "gpt-3.5-turbo")
- `temperature` (optional): Model temperature 0.0-2.0 (default: 0.1)

**Response:**
```json
{
  "success": true,
  "answer": "Based on the uploaded documents, the main topics include...",
  "sources": [
    "document1.pdf",
    "guide.md"
  ],
  "model_used": "gpt-3.5-turbo",
  "processing_time": 2.34,
  "error": null
}
```

**Example:**
```bash
curl -X POST "http://localhost:8003/query" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What are the key features mentioned?",
    "model": "gpt-3.5-turbo",
    "temperature": 0.1
  }'
```

**Error Response (Agent Not Ready):**
```json
{
  "detail": "Agent not ready. Upload documents and initialize first."
}
```

---

### 7. Reset System

**POST** `/reset`

Reset the system and clear all documents.

**Response:**
```json
{
  "success": true,
  "message": "System reset successfully"
}
```

**Example:**
```bash
curl -X POST "http://localhost:8003/reset"
```

---

## Error Handling

The API uses standard HTTP status codes and returns detailed error messages:

### Common Status Codes

- `200` - Success
- `400` - Bad Request (invalid parameters, agent not ready)
- `422` - Validation Error (invalid request body)
- `500` - Internal Server Error

### Error Response Format

```json
{
  "detail": "Error description"
}
```

### Common Errors

1. **Agent Not Ready**
   ```json
   {
     "detail": "Agent not ready. Upload documents and initialize first."
   }
   ```

2. **No Documents**
   ```json
   {
     "detail": "No documents available. Upload documents first."
   }
   ```

3. **Invalid Temperature**
   ```json
   {
     "detail": "Temperature must be between 0.0 and 2.0"
   }
   ```

---

## Usage Workflow

### Complete Workflow Example

```python
import requests
import json

base_url = "http://localhost:8003"

# 1. Check system status
status = requests.get(f"{base_url}/status").json()
print("Status:", status)

# 2. Upload documents
files = [
    ('files', ('doc.txt', "Sample document content", 'text/plain'))
]
upload_result = requests.post(f"{base_url}/upload", files=files).json()
print("Upload:", upload_result)

# 3. Initialize agent
init_data = {"model": "gpt-3.5-turbo", "temperature": 0.1}
init_result = requests.post(f"{base_url}/initialize", json=init_data).json()
print("Initialize:", init_result)

# 4. Query documents
query_data = {
    "query": "What is this document about?",
    "model": "gpt-3.5-turbo",
    "temperature": 0.1
}
query_result = requests.post(f"{base_url}/query", json=query_data).json()
print("Answer:", query_result["answer"])
```

---

## Testing

### Manual Testing

Use the provided test script:

```bash
cd tests
python3 manual_test.py
```

### Automated Testing

Run comprehensive API tests:

```bash
cd tests
python3 test_api.py --save
```

### Test Files

The `/tests/test_files/` directory contains sample documents for testing:
- `sample_document.txt` - General information about the RAG system
- `ai_guide.md` - AI and machine learning concepts
- `python_guide.txt` - Python programming guide

---

## Configuration

### Environment Variables

- `OPENAI_API_KEY` - Your OpenAI API key (required)

### Server Configuration

- **Host**: `0.0.0.0` (all interfaces)
- **Port**: `8003`
- **CORS**: Enabled for all origins

### Model Configuration

Default settings:
- **Model**: `gpt-3.5-turbo`
- **Temperature**: `0.1`
- **Vector Store**: ChromaDB (with FAISS fallback)

---

## Performance

### Response Times

- Health check: < 100ms
- Document upload: 1-10s (depending on file size)
- Agent initialization: 2-5s
- Query processing: 1-5s (depending on complexity)

### Limitations

- Maximum file size: Limited by available memory
- Concurrent requests: Single-threaded (suitable for development)
- Vector store: Local storage (ChromaDB)

---

## Troubleshooting

### Common Issues

1. **"OPENAI_API_KEY not found"**
   - Set the environment variable: `export OPENAI_API_KEY="your_key"`

2. **"Agent not ready"**
   - Upload documents first, then initialize the agent

3. **"No documents available"**
   - Use `/upload` endpoint to upload PDF, TXT, or MD files

4. **Connection refused**
   - Ensure the server is running: `python3 api_server.py`

### Logs

The server outputs detailed logs to the console:
- Startup messages
- Request processing
- Error details

---

## Development

### Adding New File Types

To support additional file formats, modify the `DocumentLoader` class in `src/document_loader.py`.

### Custom Models

Add new models to the `/models` endpoint response in `api_server.py`.

### Advanced Features

- Authentication
- Rate limiting
- Database persistence
- Distributed deployment

---

## API Schema

The API provides OpenAPI/Swagger documentation at:
- **Swagger UI**: `http://localhost:8003/docs`
- **ReDoc**: `http://localhost:8003/redoc`
- **OpenAPI JSON**: `http://localhost:8003/openapi.json`

---

## Support

For issues and questions:
1. Check the logs for detailed error messages
2. Verify your OpenAI API key is valid
3. Ensure all dependencies are installed
4. Review this documentation for usage examples

## Version

Current API version: **1.0.0**

Last updated: September 14, 2025