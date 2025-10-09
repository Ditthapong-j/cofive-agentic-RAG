# Tags and Metadata Feature - Quick Start Guide

## 🎯 Overview

ฟีเจอร์ใหม่นี้เพิ่มความสามารถในการจัดระเบียบและกรองเอกสารด้วย **Tags** และ **Metadata** ทำให้คุณสามารถค้นหาข้อมูลได้แม่นยำและมีประสิทธิภาพมากขึ้น

## 🚀 Quick Start

### 1. เริ่มต้น API Server

```bash
python api_server.py
```

### 2. Upload เอกสารพร้อม Tags และ Metadata

#### ตัวอย่าง 1: Upload ด้วย Tags
```bash
curl -X POST "http://localhost:8003/upload?tags=research,AI,machine-learning" \
     -F "files=@document.pdf"
```

#### ตัวอย่าง 2: Upload ด้วย Metadata
```bash
curl -X POST "http://localhost:8003/upload?metadata={\"author\":\"John\",\"year\":2024}" \
     -F "files=@document.pdf"
```

#### ตัวอย่าง 3: Upload ด้วยทั้ง Tags และ Metadata
```bash
curl -X POST "http://localhost:8003/upload?tags=research,AI&metadata={\"author\":\"John\",\"year\":2024,\"department\":\"R&D\"}" \
     -F "files=@document1.pdf" \
     -F "files=@document2.pdf"
```

### 3. Query เอกสารด้วยการกรอง

#### ตัวอย่าง 1: กรองด้วย Tags
```bash
curl -X POST "http://localhost:8003/query" \
     -H "Content-Type: application/json" \
     -d '{
       "query": "What are the key findings?",
       "tags": ["research", "AI"]
     }'
```

#### ตัวอย่าง 2: กรองด้วย Metadata
```bash
curl -X POST "http://localhost:8003/query" \
     -H "Content-Type: application/json" \
     -d '{
       "query": "What did John write?",
       "metadata_filter": {"author": "John", "year": 2024}
     }'
```

#### ตัวอย่าง 3: กรองด้วยทั้ง Tags และ Metadata
```bash
curl -X POST "http://localhost:8003/query" \
     -H "Content-Type: application/json" \
     -d '{
       "query": "Summarize R&D research",
       "tags": ["research"],
       "metadata_filter": {"department": "R&D", "year": 2024}
     }'
```

## 📝 การใช้งานใน Python

### Upload Documents
```python
import requests
import json

url = "http://localhost:8003/upload"

# เตรียมไฟล์
files = [('files', open('document.pdf', 'rb'))]

# เตรียม tags และ metadata
params = {
    'tags': 'research,AI,technical',
    'metadata': json.dumps({
        'author': 'John Doe',
        'year': 2024,
        'department': 'R&D',
        'priority': 'high'
    })
}

# Upload
response = requests.post(url, files=files, params=params)
print(response.json())
```

### Query with Filters
```python
import requests

url = "http://localhost:8003/query"

# Query พร้อม filters
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

# แสดงผลลัพธ์
print(f"Answer: {result['answer']}")
print(f"Chunks retrieved: {result['chunks_retrieved']}")

# ดูข้อมูล similarity scores พร้อม tags และ metadata
if result.get('similarity_scores'):
    for score_info in result['similarity_scores']:
        print(f"\nSource: {score_info['source']}")
        print(f"Score: {score_info['score']}")
        print(f"Tags: {score_info.get('tags', [])}")
        print(f"Metadata: {score_info.get('metadata', {})}")
```

## 🎨 Use Cases

### 1. การจัดการเอกสารวิจัย
```python
# Upload research papers
metadata = {
    "author": "Dr. Smith",
    "year": 2024,
    "journal": "Nature AI",
    "field": "Machine Learning",
    "citations": 150
}
tags = ["research", "peer-reviewed", "ML"]

# Query เฉพาะ papers จากปี 2024
query_data = {
    "query": "What are the latest ML breakthroughs?",
    "tags": ["research", "ML"],
    "metadata_filter": {"year": 2024}
}
```

### 2. การจัดการเอกสารธุรกิจ
```python
# Upload business reports
metadata = {
    "department": "Marketing",
    "quarter": "Q4",
    "year": 2024,
    "status": "approved"
}
tags = ["business", "marketing", "quarterly"]

# Query เฉพาะ Q4 reports
query_data = {
    "query": "What were the Q4 results?",
    "tags": ["quarterly"],
    "metadata_filter": {"quarter": "Q4", "year": 2024}
}
```

### 3. Multi-Project Management
```python
# Upload project documents
metadata = {
    "project": "AI-Assistant-2024",
    "team": "Backend",
    "phase": "development",
    "priority": "high"
}
tags = ["project", "backend", "development"]

# Query เฉพาะ high priority tasks
query_data = {
    "query": "What are the high priority tasks?",
    "tags": ["project"],
    "metadata_filter": {"priority": "high", "phase": "development"}
}
```

## 🧪 การทดสอบ

### รัน Test Suite
```bash
python tests/test_tags_metadata.py
```

### รัน Examples
```bash
python examples/tags_metadata_example.py
```

## 📖 เอกสารเพิ่มเติม

- **คู่มือฉบับเต็ม**: [TAGS_METADATA_GUIDE.md](TAGS_METADATA_GUIDE.md)
- **API Documentation**: http://localhost:8003/docs
- **Examples**: [examples/tags_metadata_example.py](examples/tags_metadata_example.py)

## 💡 Tips

### Tags
- ใช้สำหรับหมวดหมู่กว้างๆ
- ควรเป็น lowercase และใช้ hyphen แทน space
- ตัวอย่าง: `research`, `ai-research`, `q4-2024`

### Metadata
- ใช้สำหรับข้อมูลเฉพาะเจาะจง
- รองรับ string, number, boolean
- รักษา consistency ของ key names
- ตัวอย่าง: `{"author": "John", "year": 2024, "priority": "high"}`

### การกรอง
- Tags = กรองแบบ OR (มี tag ใดก็ได้ใน list)
- Metadata = กรองแบบ AND (ต้องตรงทุก key-value)
- ใช้ร่วมกัน = ผลลัพธ์แม่นยำที่สุด

## 🔍 Response Format

Query response จะรวม tags และ metadata:

```json
{
  "success": true,
  "answer": "...",
  "sources": ["doc1.pdf"],
  "similarity_scores": [
    {
      "source": "doc1.pdf",
      "content": "...",
      "score": 0.89,
      "tags": ["research", "AI"],
      "metadata": {
        "author": "John",
        "year": 2024,
        "department": "R&D"
      }
    }
  ],
  "chunks_retrieved": 5
}
```

## 🐛 Troubleshooting

### ❌ Tags ไม่ทำงาน
- ตรวจสอบว่าใช้ comma-separated string: `tags=tag1,tag2,tag3`
- ไม่ใช่ JSON array

### ❌ Metadata ไม่ทำงาน
- ตรวจสอบว่า metadata เป็น valid JSON string
- ใช้ double quotes ไม่ใช่ single quotes
- ใช้ `json.dumps()` ใน Python

### ❌ ไม่มีผลลัพธ์จากการกรอง
- ตรวจสอบว่าเอกสารที่ upload มี tags/metadata ที่ตรงกัน
- ใช้ `GET /documents` เพื่อดู tags และ metadata ของเอกสารทั้งหมด

## 🚀 Next Steps

1. อ่านคู่มือฉบับเต็ม: [TAGS_METADATA_GUIDE.md](TAGS_METADATA_GUIDE.md)
2. ทดลองใช้ตัวอย่าง: `python examples/tags_metadata_example.py`
3. รัน tests: `python tests/test_tags_metadata.py`
4. ลองสร้าง use case ของคุณเอง!

## 📞 Support

หากมีปัญหาหรือคำถาม:
- ดู API docs: http://localhost:8003/docs
- ตรวจสอบ logs ของ server
- ดูตัวอย่างใน `examples/` folder
