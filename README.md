# 🤖 Cofive Agentic RAG System

ระบบ Agentic RAG (Retrieval-Augmented Generation) ที่ขับเคลื่อนด้วย LangChain และ OpenAI สำหรับการค้นหาข้อมูลอัจฉริยะและการตอบคำถามแบบมีเหตุผล

## ✨ คุณสมบัติหลัก

- 🔍 **การค้นหาเอกสารอัจฉริยะ**: ใช้ vector embeddings เพื่อค้นหาเอกสารที่เกี่ยวข้อง
- 🧠 **Agent-based Reasoning**: ตัดสินใจใช้เครื่องมือที่เหมาะสมสำหรับแต่ละคำถาม
- 🛠️ **เครื่องมือหลากหลาย**: ค้นหาเอกสาร, คำนวณ, สรุปเอกสาร, ค้นหาเว็บ
- 💬 **หน่วยความจำการสนทนา**: จดจำบริบทของการสนทนา
- 📚 **การอ้างอิงแหล่งที่มา**: แสดงแหล่งที่มาของข้อมูลอย่างชัดเจน
- 🌐 **Web Interface**: ใช้งานผ่าน Streamlit อย่างง่ายดาย

## 🚀 การติดตั้งและเริ่มต้น

### 1. Clone Repository
```bash
git clone <repository-url>
cd cofive-agentic-RAG
```

### 2. ติดตั้ง Dependencies
```bash
python setup.py
```
หรือ
```bash
pip install -r requirements.txt
```

### 3. ตั้งค่า Environment Variables
```bash
cp .env.example .env
```
แก้ไขไฟล์ `.env` และใส่ API keys ของคุณ:
```
OPENAI_API_KEY=your_openai_api_key_here
LANGCHAIN_TRACING_V2=true
LANGCHAIN_API_KEY=your_langchain_api_key_here
```

### 4. เพิ่มเอกสาร
วางไฟล์เอกสารของคุณในโฟลเดอร์ `data/`:
- รองรับไฟล์: PDF, TXT, MD
- สามารถใส่ URL ของเว็บไซต์ได้ด้วย

### 5. เริ่มใช้งาน

#### CLI Interface
```bash
python main.py
```

#### Web Interface
```bash
streamlit run streamlit_app.py
```

## 📁 โครงสร้างโปรเจกต์

```
cofive-agentic-RAG/
├── src/
│   ├── document_loader.py    # โหลดเอกสารจากหลายแหล่ง
│   ├── vector_store.py       # จัดการ vector database
│   ├── tools.py             # เครื่องมือสำหรับ agent
│   └── agentic_rag.py       # ระบบ agent หลัก
├── data/                    # โฟลเดอร์สำหรับเอกสาร
├── vectorstore/            # ฐานข้อมูล vector
├── main.py                 # CLI interface
├── streamlit_app.py        # Web interface
├── setup.py               # สคริปต์ติดตั้ง
├── requirements.txt       # dependencies
└── README.md             # คู่มือการใช้งาน
```

## 🔧 การใช้งาน

### CLI Interface
```python
from main import AgenticRAGSystem

# สร้าง system
rag_system = AgenticRAGSystem()

# เพิ่มเอกสาร
sources = ["./data", "https://example.com"]
rag_system.add_documents_from_sources(sources)

# เริ่มต้น agent
rag_system.initialize_agent()

# ถามคำถาม
result = rag_system.query("สรุปเนื้อหาหลักของเอกสาร")
print(result["answer"])
```

### Web Interface Features
- 📤 **อัปโหลดเอกสาร**: ลากและวางไฟล์เพื่ออัปโหลด
- 💬 **Chat Interface**: สนทนากับ agent แบบเรียลไทม์
- 📊 **System Status**: ตรวจสอบสถานะระบบ
- ⚙️ **การตั้งค่า**: ปรับแต่ง model และ parameters
- 📚 **แสดงแหล่งที่มา**: ดูแหล่งที่มาของข้อมูล

## 🛠️ เครื่องมือของ Agent

1. **document_search**: ค้นหาข้อมูลจาก knowledge base
2. **calculator**: คำนวณทางคณิตศาสตร์
3. **web_search**: ค้นหาข้อมูลปัจจุบันจากอินเทอร์เน็ต
4. **document_summary**: สรุปเอกสารตามหัวข้อที่กำหนด

## 💡 ตัวอย่างคำถาม

- "สรุปเนื้อหาหลักของเอกสารทั้งหมด"
- "หาข้อมูลเกี่ยวกับ [หัวข้อที่สนใจ]"
- "คำนวณ 15% ของ 1000"
- "มีการพัฒนาอะไรใหม่ๆ บ้าง"
- "เปรียบเทียบข้อมูลใน [เอกสาร A] กับ [เอกสาร B]"

## 🎯 Use Cases

### งานวิจัยและการจัดการความรู้
- วิจัยวิชาการด้วยเอกสารจำนวนมาก
- ฐานความรู้ขององค์กร
- ค้นหาเอกสารทางเทคนิค
- วิเคราะห์เอกสารกฎหมาย

### การศึกษา
- ช่วยเหลือนักเรียนในการวิจัย
- สำรวจเนื้อหาวิชา
- ช่วยทำการบ้านพร้อมอ้างอิงแหล่งที่มา
- ทำ literature review อัตโนมัติ

### Business Intelligence
- วิเคราะห์การวิจัยตลาด
- ข่าวกรองคู่แข่ง
- ค้นหานโยบายและขั้นตอนการทำงาน
- ช่วยเหลือในการฝึกอบรม

## ⚙️ การปรับแต่ง

### Model Configuration
```python
# เปลี่ยน model
rag_system.initialize_agent(
    model_name="gpt-4",
    temperature=0.2
)
```

### Vector Store Settings
```python
# ปรับ chunk size
document_loader = DocumentLoader(
    chunk_size=1500,
    chunk_overlap=300
)
```

## 🐛 การแก้ปัญหา

### ปัญหาที่พบบ่อย

**API Key Errors**
- ตรวจสอบว่าตั้งค่า `OPENAI_API_KEY` ถูกต้อง
- ลองรีสตาร์ทแอปพลิเคชัน

**ไม่มีผลลัพธ์การค้นหา**
- ตรวจสอบว่าเอกสารถูกโหลดเข้า vector store แล้ว
- ลองเปลี่ยนคำค้นหาให้เฉพาะเจาะจงมากขึ้น

**ปัญหาประสิทธิภาพ**
- ลดขนาด chunk หรือจำนวนเอกสาร
- ใช้ model ที่เร็วกว่า เช่น gpt-3.5-turbo

## 🤝 การมีส่วนร่วม

ยินดีรับ contributions! กรุณา:
1. Fork โปรเจกต์
2. สร้าง feature branch
3. Commit การเปลี่ยนแปลง
4. สร้าง Pull Request

## 📝 License

MIT License - ดูรายละเอียดในไฟล์ LICENSE

## 🙏 เครดิต

- [LangChain](https://langchain.com/) - Framework สำหรับสร้าง LLM applications
- [OpenAI](https://openai.com/) - LLM และ embeddings
- [Chroma](https://www.trychroma.com/) - Vector database
- [Streamlit](https://streamlit.io/) - Web framework

---

พัฒนาด้วย ❤️ โดยใช้ Python และ LangChain

