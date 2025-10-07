# 📄 Document CRUD Operations Guide

## 🎯 Overview
This guide explains the comprehensive CRUD (Create, Read, Update, Delete) operations for document management in the Agentic RAG API.

## 🔧 Available Operations

### 📤 CREATE - Upload Documents
Upload and process documents into the system.

**Endpoint:** `POST /upload`

**Features:**
- Multiple file upload support
- Supported formats: PDF, TXT, MD
- Automatic content extraction and chunking
- Metadata tracking and storage
- File size and type validation

**Example:**
```bash
curl -X POST "http://localhost:8003/upload" \
  -F "files=@document.pdf" \
  -F "files=@notes.txt"
```

**Response:**
```json
{
  "success": true,
  "message": "Successfully processed 2 files",
  "files_processed": 2,
  "total_documents": 5
}
```

### 📋 READ - List All Documents
Get a comprehensive list of all uploaded documents.

**Endpoint:** `GET /documents`

**Features:**
- Complete document metadata
- Upload timestamps
- Content previews
- Processing statistics
- File information

**Example:**
```bash
curl -X GET "http://localhost:8003/documents"
```

**Response:**
```json
{
  "success": true,
  "documents": [
    {
      "id": "doc_00000001",
      "filename": "research_paper.pdf",
      "file_type": "pdf",
      "file_size": 1024000,
      "upload_time": "2025-10-02T14:30:22.123456",
      "chunk_count": 15,
      "content_preview": "This research paper discusses..."
    }
  ],
  "total_count": 3
}
```

### 📄 READ - Get Document Details
Retrieve detailed information about a specific document.

**Endpoint:** `GET /documents/{doc_id}`

**Features:**
- Complete document metadata
- Processing details
- Content preview
- System integration info

**Example:**
```bash
curl -X GET "http://localhost:8003/documents/doc_00000001"
```

**Response:**
```json
{
  "id": "doc_00000001",
  "filename": "research_paper.pdf",
  "file_type": "pdf",
  "file_size": 1024000,
  "upload_time": "2025-10-02T14:30:22.123456",
  "chunk_count": 15,
  "content_preview": "This research paper discusses the implementation..."
}
```

### 🗑️ DELETE - Remove Specific Document
Delete a single document from the system.

**Endpoint:** `DELETE /documents/{doc_id}`

**Features:**
- Safe document removal
- Metadata cleanup
- Agent reset if last document
- Remaining count tracking

**Example:**
```bash
curl -X DELETE "http://localhost:8003/documents/doc_00000001"
```

**Response:**
```json
{
  "success": true,
  "message": "Document deleted successfully",
  "deleted_document_id": "doc_00000001",
  "remaining_count": 2
}
```

### 🗑️ DELETE - Remove All Documents
Clear all documents from the system.

**Endpoint:** `DELETE /documents`

**Features:**
- Complete system reset
- Vector store cleanup
- Agent reinitialization
- Memory clearing

**Example:**
```bash
curl -X DELETE "http://localhost:8003/documents"
```

**Response:**
```json
{
  "success": true,
  "message": "All documents deleted successfully",
  "deleted_count": 5
}
```

## 🔄 Complete Workflow Example

### 1. Check System Status
```bash
curl -X GET "http://localhost:8003/status"
```

### 2. Upload Documents
```bash
# Upload a PDF
curl -X POST "http://localhost:8003/upload" \
  -F "files=@research.pdf"

# Upload multiple files
curl -X POST "http://localhost:8003/upload" \
  -F "files=@doc1.txt" \
  -F "files=@doc2.md"
```

### 3. List All Documents
```bash
curl -X GET "http://localhost:8003/documents"
```

### 4. Get Specific Document
```bash
curl -X GET "http://localhost:8003/documents/doc_00000001"
```

### 5. Initialize Agent
```bash
curl -X POST "http://localhost:8003/initialize?model=gpt-4o-mini&temperature=0.1"
```

### 6. Query Documents
```bash
curl -X POST "http://localhost:8003/query" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What are the main topics?",
    "model": "gpt-4o-mini",
    "temperature": 0.1
  }'
```

### 7. Delete Specific Document
```bash
curl -X DELETE "http://localhost:8003/documents/doc_00000001"
```

### 8. Delete All Documents (Reset)
```bash
curl -X DELETE "http://localhost:8003/documents"
```

## 📊 Document Metadata

Each document includes the following metadata:

| Field | Type | Description |
|-------|------|-------------|
| `id` | string | Unique document identifier |
| `filename` | string | Original filename |
| `file_type` | string | File extension (pdf, txt, md) |
| `file_size` | integer | File size in bytes |
| `upload_time` | string | ISO timestamp of upload |
| `chunk_count` | integer | Number of text chunks |
| `content_preview` | string | First 200 characters |

## 🧪 Testing with Python

Use the provided test script:

```bash
cd /Users/ditthapong/Desktop/cofive-agentic-RAG
python3 tests/test_crud_operations.py
```

## 🔧 Advanced Features

### Document Tracking
- Unique ID generation for each document
- Metadata persistence across sessions
- Relationship tracking between documents and chunks

### Content Processing
- Automatic text extraction from PDFs
- Smart text chunking for optimal retrieval
- Content preview generation

### System Integration
- Vector store management
- Agent state synchronization
- Memory and cache management

## ⚠️ Important Notes

### Limitations
- Vector embeddings persist after document deletion (current limitation)
- Large files may take time to process
- Memory usage scales with document count

### Best Practices
- Upload documents before initializing agent
- Use descriptive filenames
- Monitor system status regularly
- Clean up test uploads

### Error Handling
- 404: Document not found
- 400: Invalid file type or missing files
- 500: System errors or initialization issues

## 🚀 Quick Start

1. **Start API Server:**
   ```bash
   python3 api_server.py
   ```

2. **Access Swagger UI:**
   - Open `http://localhost:8003/docs`
   - Test all CRUD operations interactively

3. **Run Test Suite:**
   ```bash
   python3 tests/test_crud_operations.py
   ```

## 📈 Performance Considerations

### Upload Performance
- Multiple small files vs. few large files
- PDF processing is slower than text files
- Network bandwidth affects upload speed

### Query Performance
- More documents = more comprehensive answers
- Chunk count affects retrieval quality
- Model choice impacts response time

### Memory Usage
- Document metadata stored in memory
- Text chunks cached for performance
- Vector embeddings stored persistently

## 🔮 Future Enhancements

### Planned Features
- Document versioning and updates
- Selective vector store updates
- Advanced search and filtering
- Bulk operations with progress tracking
- Document content modification
- Metadata editing capabilities

### API Extensions
- Pagination for large document lists
- Advanced filtering and sorting
- Document tagging and categorization
- Usage analytics and statistics

This comprehensive CRUD system provides full control over document management while maintaining system performance and data integrity.