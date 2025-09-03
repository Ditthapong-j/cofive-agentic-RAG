#!/usr/bin/env python3
"""
Installation and setup script for Agentic RAG
"""
import subprocess
import sys
import os
from pathlib import Path

def install_package(package_name):
    """Install a Python package"""
    try:
        print(f"📦 Installing {package_name}...")
        result = subprocess.run([
            sys.executable, "-m", "pip", "install", package_name, "--break-system-packages"
        ], capture_output=True, text=True, check=True)
        print(f"✅ {package_name} installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install {package_name}: {e}")
        return False

def install_requirements():
    """Install all required packages"""
    print("🚀 Installing required packages...")
    
    # Essential packages for the system to work
    packages = [
        "python-dotenv",
        "requests",
        "beautifulsoup4",
        "numpy",
        "pandas",
        "streamlit>=1.28.0",
        "openai>=1.3.0",
        "langchain>=0.1.0",
        "langchain-community>=0.0.20",
        "langchain-openai>=0.0.5"
    ]
    
    # Vector store packages (try both FAISS and ChromaDB)
    vector_packages = [
        "faiss-cpu>=1.7.4",  # Primary choice - no SQLite issues
        "sentence-transformers>=2.2.2"
    ]
    
    # Optional packages (may fail but system can still work)
    optional_packages = [
        "pypdf>=3.17.0",
        "python-docx>=0.8.11",
        "tiktoken>=0.5.0",
        "pydantic>=2.0.0"
    ]
    
    # ChromaDB (may fail due to SQLite)
    chromadb_packages = [
        "chromadb>=0.4.15"
    ]
    
    success_count = 0
    
    # Install essential packages
    print("\n📦 Installing essential packages...")
    for package in packages:
        if install_package(package):
            success_count += 1
    
    # Install vector store packages
    print("\n🗂️ Installing vector store packages...")
    vector_success = 0
    for package in vector_packages:
        if install_package(package):
            vector_success += 1
    
    # Try ChromaDB (optional due to SQLite issues)
    print("\n� Attempting ChromaDB installation (may fail due to SQLite)...")
    chromadb_success = False
    for package in chromadb_packages:
        if install_package(package):
            chromadb_success = True
            print("✅ ChromaDB installed successfully")
        else:
            print("⚠️ ChromaDB installation failed - will use FAISS instead")
    
    # Install optional packages
    print("\n📦 Installing optional packages...")
    for package in optional_packages:
        install_package(package)  # Don't count failures for optional packages
    
    # Summary
    print(f"\n📊 Installation Summary:")
    print(f"Essential packages: {success_count}/{len(packages)}")
    print(f"Vector store packages: {vector_success}/{len(vector_packages)}")
    print(f"ChromaDB: {'✅ Available' if chromadb_success else '❌ Not available (using FAISS)'}")
    
    if vector_success == 0:
        print("❌ No vector store available! System will not work.")
        return False
    
    return success_count >= len(packages) - 2  # Allow some failures

def create_env_file():
    """Create .env file if needed"""
    print("\n📝 Setting up environment file...")
    
    env_file = Path(".env")
    env_example = Path(".env.example")
    
    if env_file.exists():
        print("✅ .env file already exists")
        return True
    
    if env_example.exists():
        print("📋 Creating .env from .env.example...")
        try:
            with open(env_example, 'r') as src:
                content = src.read()
            with open(env_file, 'w') as dst:
                dst.write(content)
            print("✅ .env file created successfully")
            return True
        except Exception as e:
            print(f"❌ Failed to create .env file: {e}")
            return False
    else:
        print("📝 Creating basic .env file...")
        env_content = """# Agentic RAG Environment Variables
OPENAI_API_KEY=your_openai_api_key_here
LANGCHAIN_TRACING_V2=true
LANGCHAIN_API_KEY=your_langchain_api_key_here
"""
        try:
            with open(env_file, 'w') as f:
                f.write(env_content)
            print("✅ Basic .env file created")
            return True
        except Exception as e:
            print(f"❌ Failed to create .env file: {e}")
            return False

def create_sample_data():
    """Create sample data if data directory is empty"""
    print("\n📚 Setting up sample data...")
    
    data_dir = Path("data")
    data_dir.mkdir(exist_ok=True)
    
    existing_files = list(data_dir.glob("*.md"))
    if existing_files:
        print(f"✅ Found {len(existing_files)} existing sample files")
        return True
    
    print("📝 Creating sample data files...")
    
    # Sample file 1: Thai introduction
    intro_content = """# ระบบ Agentic RAG

## ภาพรวม
ระบบ Agentic RAG เป็นเทคโนโลยีที่ผสมผสาน:
- การค้นหาเอกสารอัจฉริยะ (Retrieval)
- การเพิ่มข้อมูลเข้ากับการสร้างคำตอบ (Augmented Generation)
- การใช้ AI Agent ในการตัดสินใจ

## คุณสมบัติ
- ค้นหาเอกสารด้วย Vector Similarity
- ตอบคำถามอย่างชาญฉลาด
- อ้างอิงแหล่งที่มาได้
- รองรับภาษาไทย

## การใช้งาน
1. อัปโหลดเอกสาร
2. ถามคำถาม
3. รับคำตอบพร้อมแหล่งอ้างอิง

ระบบนี้เหมาะสำหรับองค์กรที่ต้องการจัดการความรู้อย่างมีประสิทธิภาพ
"""
    
    try:
        with open(data_dir / "agentic_rag_intro.md", "w", encoding="utf-8") as f:
            f.write(intro_content)
        print("✅ Created sample introduction file")
        return True
    except Exception as e:
        print(f"❌ Failed to create sample data: {e}")
        return False

def test_basic_functionality():
    """Test if basic imports work"""
    print("\n🧪 Testing basic functionality...")
    
    try:
        # Test basic Python imports
        import os
        import sys
        from pathlib import Path
        print("✅ Basic Python modules - OK")
        
        # Test dotenv
        try:
            from dotenv import load_dotenv
            print("✅ python-dotenv - OK")
        except ImportError:
            print("⚠️ python-dotenv not available")
        
        # Test vector stores
        faiss_available = False
        chroma_available = False
        
        try:
            import faiss
            print("✅ FAISS - OK")
            faiss_available = True
        except ImportError:
            print("❌ FAISS not available")
        
        try:
            import chromadb
            print("✅ ChromaDB - OK")
            chroma_available = True
        except ImportError:
            print("⚠️ ChromaDB not available")
        
        # Test LangChain
        try:
            from langchain_openai import OpenAIEmbeddings
            print("✅ LangChain OpenAI - OK")
        except ImportError:
            print("❌ LangChain OpenAI not available")
        
        # Test if we have at least one vector store
        if not faiss_available and not chroma_available:
            print("❌ No vector store available! Install faiss-cpu or chromadb")
            return False
        
        # Test if our source files are readable
        src_dir = Path("src")
        if src_dir.exists():
            src_files = list(src_dir.glob("*.py"))
            print(f"✅ Found {len(src_files)} source files in src/")
        else:
            print("❌ src/ directory not found")
            return False
        
        # Vector store recommendation
        if faiss_available and not chroma_available:
            print("💡 Recommendation: Using FAISS (no SQLite issues)")
        elif chroma_available and not faiss_available:
            print("💡 Recommendation: Using ChromaDB")
        elif faiss_available and chroma_available:
            print("💡 Recommendation: Both FAISS and ChromaDB available")
        
        return True
        
    except Exception as e:
        print(f"❌ Basic functionality test failed: {e}")
        return False

def show_next_steps():
    """Show user what to do next"""
    print("\n" + "="*60)
    print("🎉 Setup Complete!")
    print("="*60)
    
    print("\n📋 Next Steps:")
    print("1. 🔑 Add your OpenAI API key to .env file:")
    print("   OPENAI_API_KEY=sk-your-actual-api-key-here")
    print()
    print("2. 📚 Add your documents to the data/ folder")
    print("   (PDF, TXT, or MD files)")
    print()
    print("3. 🚀 Start using the system:")
    print("   • FAISS mode: python main_faiss.py")
    print("   • Web mode: streamlit run streamlit_app.py")
    print()
    print("4. 🔍 Test with sample queries:")
    print("   • 'สรุปเนื้อหาในเอกสาร'")
    print("   • 'Agentic RAG คืออะไร?'")
    print("   • 'คำนวณ 15% ของ 1000'")
    print()
    print("💡 Vector Store Status:")
    
    # Check which vector stores are available
    try:
        import faiss
        print("   ✅ FAISS - Available (recommended)")
    except ImportError:
        print("   ❌ FAISS - Not available")
    
    try:
        import chromadb
        print("   ✅ ChromaDB - Available")
    except ImportError:
        print("   ❌ ChromaDB - Not available")
    
    print()
    print("💡 Need help? Check USAGE.md for detailed instructions")
    print("🔧 SQLite issues? FAISS provides a compatible alternative!")

def main():
    """Main setup function"""
    print("🤖 Cofive Agentic RAG - Setup & Installation")
    print("="*60)
    
    # Step 1: Install packages
    if not install_requirements():
        print("❌ Failed to install essential packages. Please check your Python installation.")
        return
    
    # Step 2: Setup environment
    if not create_env_file():
        print("❌ Failed to setup environment file.")
        return
    
    # Step 3: Create sample data
    if not create_sample_data():
        print("❌ Failed to create sample data.")
        return
    
    # Step 4: Test basic functionality
    if not test_basic_functionality():
        print("❌ Basic functionality test failed.")
        return
    
    # Step 5: Show next steps
    show_next_steps()

if __name__ == "__main__":
    main()
