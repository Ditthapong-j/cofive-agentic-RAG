# คู่มือการเขียนโปรแกรม Python

## บทนำสู่ Python
Python เป็นภาษาโปรแกรมระดับสูงที่ตีความได้ ซึ่งขึ้นชื่อเรื่องความเรียบง่ายและความสามารถในการอ่านได้

## คุณสมบัติหลัก
- **เรียนรู้ง่าย**: ไวยากรณ์ง่ายคล้ายกับภาษาอังกฤษ
- **หลากหลาย**: ใช้สำหรับการพัฒนาเว็บ, วิทยาศาสตร์ข้อมูล, AI/ML, การทำงานอัตโนมัติ
- **ชุมชนใหญ่**: ไลบรารีมากมายและการสนับสนุนจากชุมชน
- **ข้ามแพลตฟอร์ม**: ทำงานบน Windows, macOS, Linux

## ประเภทข้อมูล
- **ตัวเลข**: int, float, complex
- **สตริง**: ข้อมูลข้อความที่ล้อมด้วยเครื่องหมายคำพูด
- **ลิสต์**: คอลเล็กชันที่เรียงลำดับของรายการ
- **ดิกชันนารี**: คู่ key-value
- **เซต**: คอลเล็กชันที่ไม่เรียงลำดับของรายการที่ไม่ซ้ำ

## โครงสร้างการควบคุม
- **คำสั่ง If-else**: การดำเนินการตามเงื่อนไข
- **ลูป**: ลูป for และ while สำหรับการทำซ้ำ
- **ฟังก์ชัน**: บล็อกโค้ดที่ใช้ซ้ำได้
- **คลาส**: การเขียนโปรแกรมเชิงวัตถุ

## ไลบรารีสำหรับ AI/ML
- **NumPy**: การคำนวณเชิงตัวเลข
- **Pandas**: การจัดการและวิเคราะห์ข้อมูล
- **Scikit-learn**: อัลกอริทึมการเรียนรู้ของเครื่อง
- **TensorFlow/PyTorch**: เฟรมเวิร์กการเรียนรู้เชิงลึก
- **LangChain**: การสร้างแอปพลิเคชัน LLM

## แนวปฏิบัติที่ดี
1. ปฏิบัติตามแนวทาง PEP 8 style
2. ใช้ชื่อตัวแปรที่มีความหมาย
3. เขียน docstrings สำหรับฟังก์ชัน
4. จัดการข้อยกเว้นอย่างเหมาะสม
5. ใช้ virtual environments

## ตัวอย่างโค้ด
```python
def greet(name):
    """ฟังก์ชันทักทายง่ายๆ"""
    return f"สวัสดี, {name}!"

# การใช้งาน
message = greet("โลก")
print(message)
```

## การใช้งาน LangChain
```python
from langchain.llms import OpenAI
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate

# สร้าง prompt template
prompt = PromptTemplate(
    input_variables=["question"],
    template="ตอบคำถามนี้: {question}"
)

# สร้าง LLM
llm = OpenAI(temperature=0.7)

# สร้าง chain
chain = LLMChain(llm=llm, prompt=prompt)

# ใช้งาน
result = chain.run("Python คืออะไร?")
print(result)
```

## การสร้าง RAG System
```python
from langchain.document_loaders import TextLoader
from langchain.vectorstores import Chroma
from langchain.embeddings import OpenAIEmbeddings
from langchain.text_splitter import CharacterTextSplitter

# โหลดเอกสาร
loader = TextLoader("document.txt")
documents = loader.load()

# แบ่งข้อความ
text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=0)
texts = text_splitter.split_documents(documents)

# สร้าง embeddings
embeddings = OpenAIEmbeddings()

# สร้าง vector store
vectorstore = Chroma.from_documents(texts, embeddings)

# ค้นหา
query = "Python คืออะไร?"
docs = vectorstore.similarity_search(query)
```

## เครื่องมือและทรัพยากร
- เอกสารอย่างเป็นทางการของ Python: python.org
- Python Package Index (PyPI): pypi.org
- บทเรียนออนไลน์และคอร์ส
- ฟอรัมชุมชนและ Stack Overflow

## การติดตั้งและจัดการ packages
```bash
# ติดตั้ง package
pip install package_name

# ติดตั้งจากไฟล์ requirements
pip install -r requirements.txt

# สร้าง virtual environment
python -m venv myenv

# เปิดใช้งาน virtual environment
source myenv/bin/activate  # Linux/Mac
myenv\Scripts\activate     # Windows
```

## การดีบัก
```python
# ใช้ print สำหรับการดีบัก
print(f"ค่าของตัวแปร: {variable}")

# ใช้ debugger
import pdb
pdb.set_trace()

# ใช้ logging
import logging
logging.basicConfig(level=logging.DEBUG)
logging.debug("ข้อความดีบัก")
```

Python เป็นภาษาที่ยอดเยี่ยมสำหรับผู้เริ่มต้นและมีประสิทธิภาพสำหรับนักพัฒนาที่มีประสบการณ์ ด้วยไลบรารีที่หลากหลายและชุมชนที่แข็งแกร่ง ทำให้เป็นตัวเลือกที่ดีสำหรับโครงการ AI และ ML!
