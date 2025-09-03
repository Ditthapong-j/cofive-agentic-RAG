"""
Demo script for prompt customization
"""
import streamlit as st

def show_prompt_examples():
    """Show examples of different prompt styles"""
    
    st.title("🎨 ตัวอย่างการปรับแต่ง Prompt")
    
    # Sample query
    sample_query = "อธิบายการใช้งาน Python ในงานธุรกิจ"
    
    st.subheader("📝 คำถามตัวอย่าง")
    st.code(sample_query)
    
    st.subheader("🎭 ตัวอย่างคำตอบตามรูปแบบต่างๆ")
    
    # Technical Style
    with st.expander("💻 Technical Style"):
        st.markdown("""
        **Python** เป็น high-level programming language ที่มี syntax ที่อ่านง่าย เหมาะสำหรับการพัฒนา business applications หลากหลายประเภท:
        
        **1. Data Analysis & Business Intelligence**
        ```python
        import pandas as pd
        import matplotlib.pyplot as plt
        
        # วิเคราะห์ข้อมูลขาย
        sales_data = pd.read_csv('sales.csv')
        monthly_revenue = sales_data.groupby('month')['revenue'].sum()
        ```
        
        **2. Web Development**
        - Django/Flask frameworks สำหรับ web applications
        - FastAPI สำหรับ REST APIs
        - Streamlit สำหรับ data dashboards
        
        **3. Automation & Process Optimization**
        - RPA (Robotic Process Automation)
        - ETL pipelines
        - Report generation
        """)
    
    # Casual Style  
    with st.expander("😊 Casual Style"):
        st.markdown("""
        Python นี่แหละครับ! เป็นภาษาโปรแกรมที่นิยมใช้ในธุรกิจมากๆ เพราะอะไรหรือ? 
        
        🎯 **ทำไม Python ถึงเจ๋ง?**
        - เขียนง่าย อ่านง่าย (แม้แต่คนไม่ใช่โปรแกรมเมอร์ก็เข้าใจได้!)
        - มี library เยอะมาก ทำอะไรก็มีคนทำไว้แล้ว
        - community ใหญ่ หาความช่วยเหลือง่าย
        
        🏢 **ใช้ทำอะไรได้บ้าง?**
        - วิเคราะห์ข้อมูลขาย (ดูว่าสินค้าไหนขายดี)
        - ทำเว็บไซต์ (เหมือน Netflix, Instagram ใช้ Python!)  
        - ระบบอัตโนมัติ (ส่งรายงานเมลอัตโนมัติ)
        - AI/Machine Learning (แนะนำสินค้า, chatbot)
        
        เริ่มจากงานง่ายๆ ไปก่อนนะครับ แล้วค่อยๆ เพิ่มความซับซ้อน!
        """)
    
    # Academic Style
    with st.expander("🎓 Academic Style"):
        st.markdown("""
        Python programming language ได้รับการยอมรับอย่างกว้างขวางในวงการธุรกิจสมัยใหม่ เนื่องจากคุณสมบัติและความสามารถที่หลากหลาย (van Rossum & Drake, 2009).
        
        **การประยุกต์ใช้ในเชิงธุรกิจ:**
        
        1. **Business Intelligence และ Data Analytics**
           - การวิเคราะห์ข้อมูลเชิงสถิติด้วย libraries เช่น NumPy, Pandas
           - การสร้าง visualization ด้วย Matplotlib, Seaborn  
           - การพัฒนา predictive models ด้วย scikit-learn
        
        2. **Enterprise Application Development**
           - Web frameworks (Django, Flask) สำหรับ enterprise systems
           - API development สำหรับ microservices architecture
           - Integration กับระบบ legacy ผ่าน database connectivity
        
        3. **Process Automation และ Operational Efficiency**
           - RPA implementations สำหรับ repetitive tasks
           - ETL processes สำหรับ data warehousing
           - Automated reporting และ business monitoring
        
        **ข้อดีเชิงกลยุทธ์:** Python มี low barrier to entry แต่ high scalability, ทำให้องค์กรสามารถเริ่มต้นด้วย pilot projects และขยายผลไปสู่ enterprise-wide implementations ได้อย่างมีประสิทธิภาพ.
        """)
    
    # Business Style
    with st.expander("💼 Business Style"):
        st.markdown("""
        **Python: เครื่องมือขับเคลื่อนการเติบโตทางธุรกิจ**
        
        **📈 ROI และ Business Value:**
        - ลดต้นทุนการพัฒนาซอฟต์แวร์ 30-50%
        - เพิ่มความเร็วในการตัดสินใจด้วย real-time analytics
        - ปรับปรุงประสิทธิภาพการทำงาน 25-40% ผ่าน automation
        
        **🎯 Use Cases ที่สร้างผลกำไรโดยตรง:**
        
        1. **Customer Analytics & CRM Enhancement**
           - วิเคราะห์พฤติกรรมลูกค้า → เพิ่มยอดขาย 15-20%
           - Personalized marketing campaigns → ปรับปรุง conversion rate
           - Churn prediction → ลด customer loss
        
        2. **Operational Excellence**
           - Inventory optimization → ลดต้นทุน holding 10-15%
           - Supply chain automation → เพิ่มความแม่นยำ 99%+
           - Financial reporting automation → ประหยัดเวลา 40-60%
        
        3. **Revenue Generation**
           - Dynamic pricing algorithms
           - E-commerce recommendation engines  
           - Fraud detection systems
        
        **⏰ Implementation Timeline:**
        - Phase 1 (1-3 เดือน): Pilot project และ proof of concept
        - Phase 2 (3-6 เดือน): Core business processes automation  
        - Phase 3 (6-12 เดือน): Advanced analytics และ AI integration
        
        **💰 Investment Required:** 
        จาก 100,000 - 500,000 บาท ขึ้นอยู่กับขนาดและความซับซ้อน พร้อม ROI คาดการณ์ 200-400% ภายใน 18 เดือน
        """)
        
    # Beginner Style
    with st.expander("🔰 Beginner Style"):
        st.markdown("""
        **Python คืออะไร? และใช้ในธุรกิจยังไง?**
        
        Python เป็นภาษาคอมพิวเตอร์ที่ออกแบบมาให้เข้าใจง่าย เหมือนการเขียนภาษาอังกฤษธรรมดาๆ!
        
        **🤔 ทำไมธุรกิจถึงชอบใช้ Python?**
        
        **1. ง่ายต่อการเรียนรู้**
        - ไม่ต้องเป็น programmer มืออาชีพก็เขียนได้
        - พนักงานทั่วไปสามารถเรียนรู้พื้นฐานได้ใน 2-3 เดือน
        
        **2. ประหยัดเงิน**
        - ฟรี! ไม่ต้องซื้อ license
        - ลดค่าใช้จ่ายในการจ้างบริษัทภายนอก
        
        **3. ทำอะไรได้เยอะ**
        - **จัดการข้อมูล**: อ่านไฟล์ Excel, สร้างกราฟ, คำนวณตัวเลข
        - **ทำเว็บไซต์**: สร้างเว็บขายของ, ระบบจัดการสินค้า
        - **ระบบอัตโนมัติ**: ส่งอีเมลอัตโนมัติ, สร้างรายงานประจำวัน
        
        **📚 เริ่มต้นยังไง?**
        1. เรียน online course (Coursera, Udemy)
        2. ฝึกกับข้อมูลจริงในบริษัท (เช่น รายงานขาย)
        3. เริ่มจากโปรเจ็คเล็กๆ (เช่น คำนวณกำไร-ขาดทุน)
        4. ค่อยๆ ขยายไปเรื่องที่ซับซ้อนขึ้น
        
        **💡 ตัวอย่างง่ายๆ:**
        สมมุติคุณต้องคำนวณยอดขายรวมทุกเดือน แทนที่จะนั่งกดเครื่องคิดเลข 
        Python ทำให้ใน 5 วินาที!
        """)

if __name__ == "__main__":
    show_prompt_examples()
