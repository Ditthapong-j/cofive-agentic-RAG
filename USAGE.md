# 🚀 วิธีการใช้งาน Agentic RAG System

## การติดตั้งและเริ่มต้น

### 1. ตรวจสอบการติดตั้ง Python
```bash
python --version
# ควรเป็น Python 3.8 หรือสูงกว่า
```

### 2. ติดตั้ง Dependencies
```bash
pip install -r requirements.txt
```

### 3. ตั้งค่า API Key
แก้ไขไฟล์ `.env` และใส่ OpenAI API key ของคุณ:
```
OPENAI_API_KEY=sk-your-api-key-here
```

### 4. ทดสอบระบบ
```bash
python demo.py
```

## การใช้งาน

### CLI Interface
```bash
python main.py
```

### Web Interface  
```bash
streamlit run streamlit_app.py
```

## ตัวอย่างการใช้งาน

### 1. การถามคำถามพื้นฐาน
- "สรุปเนื้อหาหลักของเอกสาร"
- "Python คืออะไร?"
- "บริษัท Cofive ทำอะไร?"

### 2. การคำนวณ
- "คำนวณ 15% ของ 1000"
- "หา square root ของ 144"

### 3. การสรุปเอกสาร
- "สรุปข้อมูลเกี่ยวกับการเขียนโปรแกรม Python"
- "มีหัวข้ออะไรบ้างในเอกสาร"

## การเพิ่มเอกสารใหม่

### วิธีที่ 1: ผ่าน Web Interface
1. เปิด Streamlit app
2. ใช้ sidebar "Upload Documents"
3. เลือกไฟล์ PDF, TXT, หรือ MD
4. กด "Process Files"

### วิธีที่ 2: วางไฟล์ในโฟลเดอร์ data/
1. วางไฟล์ในโฟลเดอร์ `data/`
2. รันใหม่ หรือใช้ฟังก์ชัน add_documents

## คุณสมบัติหลัก

### 🔍 การค้นหาอัจฉริยะ
- ใช้ Vector embeddings
- ค้นหาตามความหมาย
- รองรับภาษาไทย

### 🧠 Agent Tools
- **document_search**: ค้นหาจากเอกสาร
- **calculator**: คำนวณ  
- **document_summary**: สรุปเอกสาร
- **web_search**: ค้นหาเว็บ (placeholder)

### 💬 หน่วยความจำ
- จำบริบทการสนทนา
- ตอบคำถามต่อเนื่อง
- สามารถล้างประวัติได้

### 📚 การอ้างอิงแหล่งที่มา
- แสดงแหล่งที่มาของข้อมูล
- ความโปร่งใสในการตอบ
- ตรวจสอบได้

## การแก้ปัญหา

### ❌ ModuleNotFoundError
```bash
pip install -r requirements.txt
```

### ❌ OpenAI API Error
ตรวจสอบ API key ในไฟล์ `.env`:
```
OPENAI_API_KEY=sk-your-real-api-key
```

### ❌ ไม่มีเอกสารในระบบ
1. เพิ่มไฟล์ในโฟลเดอร์ `data/`
2. หรือใช้ web interface upload

### ❌ ปัญหา Vector Store
ลบโฟลเดอร์ `vectorstore/` และสร้างใหม่

## ตัวอย่างโค้ด

### การใช้งานพื้นฐาน
```python
from main import AgenticRAGSystem

# สร้างระบบ
rag = AgenticRAGSystem()

# เพิ่มเอกสาร
rag.add_documents_from_sources(["./data"])

# เริ่มต้น agent  
rag.initialize_agent()

# ถามคำถาม
result = rag.query("Python คืออะไร?")
print(result["answer"])
```

### การปรับแต่ง
```python
# ใช้ GPT-4
rag.initialize_agent(
    model_name="gpt-4",
    temperature=0.2
)

# เปลี่ยน chunk size
from src.document_loader import DocumentLoader
loader = DocumentLoader(
    chunk_size=1500,
    chunk_overlap=300
)
```

## สนับสนุน

### เอกสารประกอบ
- [LangChain Documentation](https://python.langchain.com/)
- [OpenAI API Reference](https://platform.openai.com/docs)
- [Streamlit Documentation](https://docs.streamlit.io/)

### ช่องทางติดต่อ
- GitHub Issues สำหรับ bug reports
- Email: support@cofive.tech
- หรือติดต่อทีมพัฒนา

---
**Cofive Agentic RAG** - Intelligent Document Search & Q&A System 🤖
