# วิธีการปรับแต่งคำตอบ Agentic RAG

## ภาพรวมการปรับแต่ง

ระบบ Agentic RAG ของคุณสามารถปรับแต่งคำตอบได้หลายวิธี เพื่อให้ได้คำตอบที่ตรงกับความต้องการและรูปแบบที่ต้องการ

## 1. การปรับแต่งผ่าน Streamlit Interface

### 🎭 Response Style (รูปแบบการตอบ)
- **Balanced**: คำตอบที่สมดุล ชัดเจน และให้ข้อมูลที่เป็นประโยชน์
- **Technical**: ใช้คำศัพท์เทคนิค และให้คำอธิบายเชิงเทคนิคพร้อมตัวอย่างโค้ด
- **Casual**: ใช้น้ำเสียงแบบสบายๆ และภาษาที่เข้าใจง่าย
- **Academic**: ให้คำตอบแบบวิชาการ มีการอ้างอิงและใช้ภาษาที่เป็นทางการ
- **Concise**: ตอบแบบกระชับ ตรงประเด็น
- **Detailed**: ให้คำอธิบายละเอียด ครอบคลุม พร้อมตัวอย่าง

### 🌍 Output Language (ภาษาที่ใช้ตอบ)
- **Auto**: ตอบในภาษาเดียวกับคำถาม หรือภาษาไทยหากไม่แน่ใจ
- **Thai**: ตอบเป็นภาษาไทยเสมอ
- **English**: ตอบเป็นภาษาอังกฤษเสมอ  
- **Mixed**: ใช้ทั้งภาษาไทยและอังกฤษตามความเหมาะสม

### 📏 Response Length (ความยาวของคำตอบ)
- **Short**: คำตอบสั้น ไม่เกิน 100 คำ
- **Medium**: คำตอบปานกลาง 100-300 คำ
- **Long**: คำตอบยาว 300-500 คำ
- **Comprehensive**: คำตอบครอบคลุมเชิงลึก 500+ คำ

### ✏️ Custom System Prompt
สามารถเพิ่มคำสั่งเฉพาะเจาะจง เช่น:
- "Always provide examples"
- "Focus on practical applications"
- "Use simple language"
- "Include step-by-step instructions"

## 2. การปรับแต่งขั้นสูง (Advanced Settings)

### ✨ Response Enhancement
- **📚 Include Examples**: รวมตัวอย่างประกอบ
- **📝 Include Citations**: แสดงแหล่งอ้างอิง
- **📊 Show Confidence Score**: แสดงระดับความมั่นใจ
- **🔢 Step-by-step Explanations**: อธิบายเป็นขั้นตอน

### 🎚️ Tone Adjustments
- **Formality Level (0-10)**: ระดับความเป็นทางการ
  - 0-3: สบายๆ ไม่เป็นทางการ
  - 4-6: ปานกลาง
  - 7-10: เป็นทางการ มืออาชีพ

- **Enthusiasm Level (0-10)**: ระดับความกระตือรือร้น
  - 0-3: เป็นกลาง นิ่ง
  - 4-6: ปานกลาง
  - 7-10: กระตือรือร้น น่าสนใจ

### 🎯 Content Focus
**เนื้อหาที่เน้น**:
- Technical Details
- Business Applications  
- Examples
- Best Practices
- Troubleshooting
- Background Theory

**เนื้อหาที่หลีกเลี่ยง**:
- Overly Technical
- Basic Explanations
- Lengthy Background
- Deprecated Information

## 3. Prompt Templates

### 📋 Default RAG Template
เหมาะสำหรับการใช้งานทั่วไป มีคำสั่งพื้นฐานสำหรับการค้นหาและประมวลผลเอกสาร

### 👨‍🏫 Teacher Template  
เหมาะสำหรับการอธิบายแนวคิดต่างๆ แบบขั้นตอน:
- ใช้ภาษาที่เข้าใจง่าย
- แบ่งแนวคิดซับซ้อนเป็นส่วนๆ
- ใช้การเปรียบเทียบและตัวอย่างจากชีวิตจริง
- ให้คำอธิบายแบบขั้นตอน

### 💼 Business Consultant Template
เหมาะสำหรับการให้คำแนะนำเชิงธุรกิจ:
- เน้นการใช้งานจริงและ ROI
- ให้คำแนะนำที่ปฏิบัติได้
- พิจารณาข้อจำกัดและทรัพยากรทางธุรกิจ
- เน้นผลลัพธ์ที่วัดได้

## 4. การสร้าง Custom Templates

### การบันทึก Template ใหม่
1. ตั้งค่าการปรับแต่งตามต้องการ
2. กรอกชื่อและคำอธิบาย Template
3. คลิก "Save Template"
4. Template จะถูกบันทึกสำหรับใช้ในอนาคต

### Preset Prompts ที่มีให้เลือก
- **Teacher Mode**: อธิบายแนวคิดแบบขั้นตอนเหมือนสอนนักเรียน
- **Expert Mode**: ให้ข้อมูลเทคนิคละเอียดพร้อมแนวปฏิบัติที่ดี
- **Beginner Mode**: ใช้ภาษาง่าย อธิบายคำศัพท์เทคนิค
- **Business Mode**: เน้นการใช้งานจริงและคุณค่าทางธุรกิจ
- **Creative Mode**: คิดนอกกรอบ ให้โซลูชันและแนวทางสร้างสรรค์

## 5. การปรับแต่งในระดับ Code

### การแก้ไข System Prompt ใน agentic_rag.py
```python
def _get_system_prompt(self) -> str:
    return """Your custom system prompt here
    
    ADDITIONAL INSTRUCTIONS:
    - Custom instruction 1
    - Custom instruction 2
    """
```

### การปรับแต่งการทำงานของ Tools
สามารถแก้ไขไฟล์ `src/tools.py` เพื่อ:
- เปลี่ยนวิธีการค้นหาเอกสาร
- ปรับปรุงการประมวลผลผลลัพธ์
- เพิ่ม context หรือ metadata

### การปรับแต่ง Vector Search
แก้ไขไฟล์ `src/vector_store.py` เพื่อ:
- เปลี่ยนจำนวนเอกสารที่ค้นหา (k parameter)
- ปรับปรุงการให้คะแนนความเกี่ยวข้อง
- เพิ่ม filtering หรือ re-ranking

## 6. เทคนิคขั้นสูงในการปรับแต่ง

### Query Enhancement
ปรับแต่งคำถามก่อนส่งให้ Agent:
```python
enhanced_query = f"""
{user_input}

RESPONSE INSTRUCTIONS:
- Style: {style}
- Language: {language}  
- Length: {length}
- Custom: {custom_instructions}
"""
```

### Response Post-processing
ปรับแต่งคำตอบหลังจากได้รับจาก Agent:
- กรองข้อมูลที่ไม่ต้องการ
- เพิ่มการจัดรูปแบบ
- แยกส่วนต่างๆ ของคำตอบ

### Memory Management
ปรับแต่งการจดจำบทสนทนา:
- เลือกข้อมูลที่สำคัญเก็บไว้
- ลบข้อมูลเก่าที่ไม่จำเป็น
- ใช้ memory แบบมีโครงสร้าง

## 7. การติดตาม Performance

### การวัดคุณภาพคำตอบ
- ความเกี่ยวข้องกับคำถาม
- ความถูกต้องของข้อมูล
- ความสมบูรณ์ของคำตอบ
- ความเข้าใจง่าย

### การปรับปรุงอย่างต่อเนื่อง
- เก็บ feedback จากผู้ใช้
- วิเคราะห์ query patterns
- ปรับปรุง prompts ตาม usage
- A/B test prompt variations

## สรุป

การปรับแต่งคำตอบ Agentic RAG สามารถทำได้หลายระดับ:

1. **ระดับ UI**: ผ่าน Streamlit interface (ง่ายที่สุด)
2. **ระดับ Configuration**: ปรับแต่ง prompts และ templates  
3. **ระดับ Code**: แก้ไข logic การทำงาน
4. **ระดับ Architecture**: ปรับปรุงโครงสร้างทั้งระบบ

เริ่มจากการปรับแต่งผ่าน UI ก่อน แล้วค่อยไปสู่การปรับแต่งที่ซับซ้อนมากขึ้นตามความต้องการ
