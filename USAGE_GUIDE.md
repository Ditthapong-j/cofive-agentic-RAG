# Agentic RAG System - วิธีการใช้งาน

ระบบ Agentic RAG ที่สามารถทำงานได้ 3 รูปแบบ:

## 🔧 การติดตั้ง

```bash
# ติดตั้ง dependencies
pip install -r requirements.txt

# ตั้งค่า OpenAI API Key
export OPENAI_API_KEY="your-openai-api-key"
```

## 📋 รูปแบบการใช้งาน

### 1. **รูปแบบดั้งเดิม (Original Interactive Mode)**
```bash
python main.py
```
- ใช้งานแบบ command line interface
- เหมาะสำหรับการทดสอบและใช้งานส่วนตัว
- มี conversation memory
- รองรับการอัปโหลดจาก folder, URL, และไฟล์

### 2. **API Mode - สำหรับระบบอื่นเรียกใช้**
```bash
# เริ่ม API server
python api_server.py
# หรือ
uvicorn api_server:app --host 0.0.0.0 --port 8000
```

**API Endpoints:**
- `GET /health` - ตรวจสอบสถานะ server
- `GET /status` - ดูสถานะระบบ
- `POST /upload` - อัปโหลดเอกสาร
- `POST /initialize` - เริ่มต้น agent
- `POST /query` - ถามคำถาม
- `GET /models` - ดู model ที่รองรับ
- `POST /reset` - รีเซ็ตระบบ

**ตัวอย่างการใช้ API:**
```bash
# อัปโหลดไฟล์
curl -X POST http://localhost:8000/upload \
  -F "files=@document.pdf"

# เริ่มต้น agent
curl -X POST http://localhost:8000/initialize \
  -d '{"model": "gpt-3.5-turbo", "temperature": 0.1}'

# ถามคำถาม
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{"query": "สรุปเอกสารให้ฟัง", "model": "gpt-3.5-turbo"}'
```

### 3. **Streamlit UI Mode**
```bash
# รัน UI แบบ standalone
streamlit run streamlit_ui.py

# หรือเชื่อมต่อกับ API backend
BACKEND_URL=http://localhost:8000 streamlit run streamlit_ui.py
```

## 🔄 การทำงานร่วมกัน

### แบบแยกส่วน (Recommended for Production)
1. รัน API server สำหรับระบบอื่นเรียกใช้:
   ```bash
   python api_server.py
   ```

2. รัน Streamlit UI สำหรับ user interface:
   ```bash
   BACKEND_URL=http://localhost:8000 streamlit run streamlit_ui.py
   ```

### แบบ Standalone (สำหรับ Development)
```bash
# รัน UI โดยไม่ต้องมี API server
streamlit run streamlit_ui.py
```

## 📁 โครงสร้างไฟล์

```
cofive-agentic-RAG/
├── src/                    # Core modules
│   ├── document_loader.py  # Document loading
│   ├── vector_store.py     # Vector store management
│   ├── agentic_rag.py      # Main RAG agent
│   └── tools.py           # Agent tools
├── main.py                # Original CLI interface
├── api_server.py          # FastAPI backend
├── streamlit_ui.py        # Streamlit UI
├── requirements.txt       # Dependencies
├── data/                  # Documents directory
└── vectorstore/          # Vector database
```

## 🎯 Features

- **Multi-format document support**: PDF, TXT, MD
- **Multiple vector stores**: ChromaDB, FAISS fallback
- **AI Models**: GPT-3.5-turbo, GPT-4, GPT-4-turbo
- **Agent tools**: Document search, calculator, summarizer
- **Memory**: Conversation history
- **Sources**: Citation tracking
- **API**: REST endpoints for integration
- **UI**: Web interface for easy use

## 📝 ตัวอย่างการใช้งาน

### Original Mode
```bash
python main.py
# จะสร้างไฟล์ตัวอย่างใน ./data/ ถ้าไม่มีเอกสาร
# พิมพ์คำถามได้เลย เช่น "สรุปเอกสารให้ฟัง"
```

### API Integration
```python
import requests

# อัปโหลดเอกสาร
files = {'files': open('document.pdf', 'rb')}
response = requests.post('http://localhost:8000/upload', files=files)

# เริ่มต้น agent
response = requests.post('http://localhost:8000/initialize')

# ถามคำถาม
query = {"query": "สรุปเอกสารหลัก", "model": "gpt-3.5-turbo"}
response = requests.post('http://localhost:8000/query', json=query)
print(response.json()['answer'])
```

## 🚀 Deployment

### Local Development
```bash
# Terminal 1: API Server
python api_server.py

# Terminal 2: UI Server  
BACKEND_URL=http://localhost:8000 streamlit run streamlit_ui.py --server.port 8501
```

### Production
- API Server: `uvicorn api_server:app --host 0.0.0.0 --port 8000`
- UI Server: Deploy to Streamlit Cloud with `BACKEND_URL` environment variable

## 🔍 Troubleshooting

1. **Import Error**: ตรวจสอบว่าติดตั้ง dependencies ครบ
2. **OpenAI API Error**: ตรวจสอบ `OPENAI_API_KEY`
3. **Vector Store Error**: ลองใช้ FAISS แทน ChromaDB
4. **File Upload Error**: ตรวจสอบ format ไฟล์ (.pdf, .txt, .md)

## 💡 Tips

- ใช้ GPT-3.5-turbo สำหรับความเร็ว
- ใช้ GPT-4 สำหรับความแม่นยำ
- Temperature 0.1 สำหรับคำตอบที่สม่ำเสมอ
- Temperature 0.7-1.0 สำหรับความคิดสร้างสรรค์
