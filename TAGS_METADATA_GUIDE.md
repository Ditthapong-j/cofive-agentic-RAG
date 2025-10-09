# Tags and Metadata Filtering Guide

## Overview
ระบบ Agentic RAG ได้รับการอัพเกรดให้รองรับการกรองข้อมูลด้วย **Tags** และ **Metadata** เพื่อให้สามารถค้นหาและจัดระเบียบเอกสารได้ดียิ่งขึ่น

## Features

### 1. Tags (ป้ายกำกับ)
- ใช้สำหรับจัดหมวดหมู่เอกสารแบบง่าย
- รองรับหลาย tags ต่อเอกสาร
- เหมาะสำหรับการจัดกลุ่มตามหัวข้อหลัก

**ตัวอย่าง tags:**
- `research`, `AI`, `machine-learning`
- `technical`, `business`, `marketing`
- `2024`, `Q1`, `annual-report`

### 2. Metadata (ข้อมูลเพิ่มเติม)
- เก็บข้อมูลรายละเอียดเพิ่มเติมเป็นคู่ key-value
- ใช้สำหรับข้อมูลที่ต้องการความแม่นยำในการกรอง
- รองรับหลายประเภทข้อมูล (string, number, date, etc.)

**ตัวอย่าง metadata:**
```json
{
  "author": "John Doe",
  "year": 2024,
  "department": "R&D",
  "category": "technical",
  "project": "AI-Assistant",
  "priority": "high"
}
```

## API Endpoints

### 1. Upload Documents with Tags and Metadata

#### Using cURL
```bash
# Upload with tags only
curl -X POST "http://localhost:8003/upload?tags=research,AI,machine-learning" \
     -F "files=@research_paper.pdf"

# Upload with metadata only
curl -X POST "http://localhost:8003/upload?metadata={\"author\":\"John\",\"year\":2024,\"category\":\"technical\"}" \
     -F "files=@technical_doc.pdf"

# Upload with both tags and metadata
curl -X POST "http://localhost:8003/upload?tags=research,AI&metadata={\"author\":\"Jane\",\"year\":2024,\"department\":\"R&D\"}" \
     -F "files=@ai_research.pdf" \
     -F "files=@ml_paper.pdf"
```

#### Using Python
```python
import requests

# Upload with tags and metadata
url = "http://localhost:8003/upload"
files = [
    ('files', open('research_paper.pdf', 'rb')),
    ('files', open('technical_doc.pdf', 'rb'))
]
params = {
    'tags': 'research,AI,technical',
    'metadata': '{"author":"John Doe","year":2024,"department":"R&D","priority":"high"}'
}

response = requests.post(url, files=files, params=params)
print(response.json())
```

#### Using JavaScript/Fetch
```javascript
const formData = new FormData();
formData.append('files', file1);
formData.append('files', file2);

const tags = 'research,AI,technical';
const metadata = JSON.stringify({
  author: 'John Doe',
  year: 2024,
  department: 'R&D',
  priority: 'high'
});

fetch(`http://localhost:8003/upload?tags=${tags}&metadata=${encodeURIComponent(metadata)}`, {
  method: 'POST',
  body: formData
})
.then(response => response.json())
.then(data => console.log(data));
```

### 2. Query Documents with Filtering

#### Filter by Tags Only
```bash
curl -X POST "http://localhost:8003/query" \
     -H "Content-Type: application/json" \
     -d '{
       "query": "What are the key findings in AI research?",
       "model": "gpt-4o-mini",
       "temperature": 0.1,
       "tags": ["research", "AI"]
     }'
```

#### Filter by Metadata Only
```bash
curl -X POST "http://localhost:8003/query" \
     -H "Content-Type: application/json" \
     -d '{
       "query": "What did John write about?",
       "model": "gpt-4o-mini",
       "temperature": 0.1,
       "metadata_filter": {
         "author": "John Doe",
         "year": 2024
       }
     }'
```

#### Filter by Both Tags and Metadata
```bash
curl -X POST "http://localhost:8003/query" \
     -H "Content-Type: application/json" \
     -d '{
       "query": "Summarize technical documents from R&D department",
       "model": "gpt-4o-mini",
       "temperature": 0.1,
       "tags": ["technical"],
       "metadata_filter": {
         "department": "R&D",
         "year": 2024
       }
     }'
```

#### Using Python
```python
import requests

url = "http://localhost:8003/query"
data = {
    "query": "What are the main findings?",
    "model": "gpt-4o-mini",
    "temperature": 0.1,
    "tags": ["research", "AI"],
    "metadata_filter": {
        "author": "John Doe",
        "year": 2024,
        "department": "R&D"
    }
}

response = requests.post(url, json=data)
result = response.json()

print("Answer:", result['answer'])
print("Chunks retrieved:", result['chunks_retrieved'])

# View similarity scores with tags and metadata
if result.get('similarity_scores'):
    for score_info in result['similarity_scores']:
        print(f"\nSource: {score_info['source']}")
        print(f"Score: {score_info['score']}")
        print(f"Tags: {score_info.get('tags', [])}")
        print(f"Metadata: {score_info.get('metadata', {})}")
```

## Use Cases

### 1. Research Papers Management
```python
# Upload research papers with detailed metadata
metadata = {
    "author": "Dr. Smith",
    "year": 2024,
    "journal": "Nature AI",
    "field": "Machine Learning",
    "citations": 150,
    "impact_factor": 8.5
}
tags = ["research", "peer-reviewed", "machine-learning"]

# Query specific papers
query_data = {
    "query": "What are the latest breakthroughs in neural networks?",
    "tags": ["research", "machine-learning"],
    "metadata_filter": {"year": 2024, "field": "Machine Learning"}
}
```

### 2. Business Documents
```python
# Upload business documents
metadata = {
    "department": "Marketing",
    "quarter": "Q4",
    "year": 2024,
    "document_type": "report",
    "status": "approved"
}
tags = ["business", "marketing", "quarterly"]

# Query specific departments
query_data = {
    "query": "What were the marketing results in Q4?",
    "tags": ["business", "marketing"],
    "metadata_filter": {"quarter": "Q4", "year": 2024}
}
```

### 3. Multi-Language Documentation
```python
# Upload documents with language metadata
metadata = {
    "language": "Thai",
    "version": "1.0",
    "last_updated": "2024-10-01",
    "translator": "AI Assistant"
}
tags = ["documentation", "thai", "user-guide"]

# Query Thai documents only
query_data = {
    "query": "คู่มือการใช้งานระบบ AI",
    "tags": ["documentation", "thai"],
    "metadata_filter": {"language": "Thai"}
}
```

### 4. Project-Based Organization
```python
# Upload project documents
metadata = {
    "project": "AI-Assistant-2024",
    "phase": "development",
    "team": "Backend",
    "priority": "high",
    "deadline": "2024-12-31"
}
tags = ["project", "development", "backend"]

# Query by project and phase
query_data = {
    "query": "What are the current development tasks?",
    "tags": ["project", "development"],
    "metadata_filter": {
        "project": "AI-Assistant-2024",
        "phase": "development",
        "priority": "high"
    }
}
```

## Response Format

When you query with filtering enabled, the response includes tags and metadata in similarity scores:

```json
{
  "success": true,
  "answer": "Based on the R&D technical documents from 2024...",
  "sources": ["technical_doc.pdf", "research_paper.pdf"],
  "similarity_scores": [
    {
      "source": "technical_doc.pdf",
      "content": "This section discusses the implementation...",
      "score": 0.89,
      "tags": ["research", "AI", "technical"],
      "metadata": {
        "author": "John Doe",
        "year": 2024,
        "department": "R&D",
        "priority": "high"
      }
    },
    {
      "source": "research_paper.pdf",
      "content": "The main findings indicate...",
      "score": 0.85,
      "tags": ["research", "AI"],
      "metadata": {
        "author": "Jane Smith",
        "year": 2024,
        "department": "R&D"
      }
    }
  ],
  "model_used": "gpt-4o-mini",
  "processing_time": 2.34,
  "chunks_retrieved": 2,
  "settings_used": {
    "response_length": "medium",
    "max_chunks": 5
  }
}
```

## Best Practices

### 1. Tag Naming
- ใช้ lowercase และ hyphen แทน space
- ✅ Good: `machine-learning`, `ai-research`, `q4-2024`
- ❌ Bad: `Machine Learning`, `AI Research`, `Q4 2024`

### 2. Metadata Keys
- ใช้ชื่อที่สื่อความหมาย
- รักษา consistency ของ key names
- ✅ Good: `author`, `year`, `department`
- ❌ Bad: `a`, `yr`, `dept`

### 3. Filtering Strategy
- ใช้ tags สำหรับหมวดหมู่กว้างๆ
- ใช้ metadata สำหรับเงื่อนไขเฉพาะเจาะจง
- รวม tags + metadata เพื่อความแม่นยำสูงสุด

### 4. Performance Tips
- ใช้ tags แทน metadata เมื่อเป็นไปได้ (faster)
- จำกัดจำนวน metadata fields ให้เหมาะสม
- ใช้ถ้อยคำที่ consistent กับเอกสาร

## Migration Guide

### Existing Documents (No Tags/Metadata)
Documents uploaded before this update will:
- Work normally without any tags or metadata
- Can be queried without filters
- Won't appear in filtered queries

### Adding Metadata to Existing Documents
Currently, you need to:
1. Delete the old document using `/documents/{doc_id}` DELETE endpoint
2. Re-upload with tags and metadata

## Testing Examples

### Test Script
```python
import requests
import json

BASE_URL = "http://localhost:8003"

def test_upload_with_tags_metadata():
    """Test uploading documents with tags and metadata"""
    url = f"{BASE_URL}/upload"
    
    # Prepare test document
    files = [('files', ('test.txt', 'This is a test document about AI', 'text/plain'))]
    
    params = {
        'tags': 'test,AI,research',
        'metadata': json.dumps({
            'author': 'Test User',
            'year': 2024,
            'category': 'testing'
        })
    }
    
    response = requests.post(url, files=files, params=params)
    print("Upload Response:", response.json())

def test_query_with_filters():
    """Test querying with tag and metadata filters"""
    url = f"{BASE_URL}/query"
    
    data = {
        "query": "What is this document about?",
        "model": "gpt-4o-mini",
        "temperature": 0.1,
        "tags": ["test", "AI"],
        "metadata_filter": {
            "author": "Test User",
            "year": 2024
        }
    }
    
    response = requests.post(url, json=data)
    result = response.json()
    
    print("\nQuery Response:")
    print(f"Success: {result['success']}")
    print(f"Answer: {result['answer']}")
    print(f"Chunks Retrieved: {result['chunks_retrieved']}")
    
    if result.get('similarity_scores'):
        print("\nSimilarity Scores:")
        for score in result['similarity_scores']:
            print(f"  - Score: {score['score']}")
            print(f"    Tags: {score.get('tags')}")
            print(f"    Metadata: {score.get('metadata')}")

if __name__ == "__main__":
    test_upload_with_tags_metadata()
    test_query_with_filters()
```

## Troubleshooting

### Q: Tags not working?
A: Make sure tags are comma-separated string: `tags=research,AI,technical`

### Q: Metadata not working?
A: Ensure metadata is valid JSON string: `metadata={"key":"value"}`

### Q: No results with filters?
A: Check if documents were uploaded with matching tags/metadata

### Q: How to see all document tags?
A: Use `GET /documents` endpoint to list all documents with their tags and metadata

## Advanced Examples

### Complex Filtering
```python
# Upload documents with rich metadata
documents = [
    {
        'file': 'paper1.pdf',
        'tags': ['research', 'AI', 'deep-learning'],
        'metadata': {
            'author': 'John Doe',
            'year': 2024,
            'citations': 150,
            'field': 'Computer Vision',
            'conference': 'CVPR'
        }
    },
    {
        'file': 'paper2.pdf',
        'tags': ['research', 'AI', 'NLP'],
        'metadata': {
            'author': 'Jane Smith',
            'year': 2024,
            'citations': 200,
            'field': 'Natural Language Processing',
            'conference': 'ACL'
        }
    }
]

# Query with multiple criteria
query = {
    'query': 'What are the latest advances in AI?',
    'tags': ['research', 'AI'],
    'metadata_filter': {
        'year': 2024,
        'field': 'Computer Vision'
    }
}
```

## Support

For issues or questions:
- Check API documentation: `http://localhost:8003/docs`
- Review error messages in response
- Enable debug logging to see filtering process
- Contact support team

## Changelog

### Version 1.1.0 (Current)
- ✅ Added tags support for documents
- ✅ Added metadata support for documents
- ✅ Added tag filtering in queries
- ✅ Added metadata filtering in queries
- ✅ Enhanced response with tag and metadata info
- ✅ Updated API documentation

### Version 1.0.0
- Initial release without tags/metadata support
