#!/usr/bin/env python3
"""
Simple test script without OpenAI dependencies
"""
import os
import sys
from pathlib import Path

def test_imports():
    """Test if basic imports work"""
    print("🧪 Testing Python imports...")
    
    try:
        import sys
        print("✅ sys - OK")
        
        import os
        print("✅ os - OK")
        
        from pathlib import Path
        print("✅ pathlib - OK")
        
    except Exception as e:
        print(f"❌ Basic imports failed: {e}")
        return False
    
    return True

def test_dotenv():
    """Test dotenv import"""
    print("\n🧪 Testing dotenv...")
    
    try:
        from dotenv import load_dotenv
        print("✅ python-dotenv - OK")
        return True
    except ImportError:
        print("❌ python-dotenv not installed")
        print("📦 Install with: pip install python-dotenv --break-system-packages")
        return False

def test_directory_structure():
    """Test directory structure"""
    print("\n🧪 Testing directory structure...")
    
    current_dir = Path.cwd()
    print(f"📁 Current directory: {current_dir}")
    
    required_dirs = ["src", "data"]
    required_files = ["main.py", "requirements.txt", ".env.example"]
    
    all_good = True
    
    for dir_name in required_dirs:
        if (current_dir / dir_name).exists():
            print(f"✅ {dir_name}/ - OK")
        else:
            print(f"❌ {dir_name}/ - Missing")
            all_good = False
    
    for file_name in required_files:
        if (current_dir / file_name).exists():
            print(f"✅ {file_name} - OK")
        else:
            print(f"❌ {file_name} - Missing")
            all_good = False
    
    return all_good

def test_data_files():
    """Test if sample data exists"""
    print("\n🧪 Testing sample data...")
    
    data_dir = Path("./data")
    if not data_dir.exists():
        print("❌ data/ directory not found")
        return False
    
    data_files = list(data_dir.glob("*.md"))
    if data_files:
        print(f"✅ Found {len(data_files)} sample documents:")
        for file in data_files:
            print(f"   📄 {file.name}")
        return True
    else:
        print("⚠️ No sample data found in data/ directory")
        return False

def test_env_setup():
    """Test environment setup"""
    print("\n🧪 Testing environment setup...")
    
    env_file = Path(".env")
    env_example = Path(".env.example")
    
    if env_example.exists():
        print("✅ .env.example - OK")
    else:
        print("❌ .env.example - Missing")
    
    if env_file.exists():
        print("✅ .env file exists")
        
        # Check if API key is set
        try:
            from dotenv import load_dotenv
            load_dotenv()
            api_key = os.getenv("OPENAI_API_KEY")
            if api_key and api_key != "your_openai_api_key_here":
                print("✅ OPENAI_API_KEY is configured")
                return True
            else:
                print("⚠️ OPENAI_API_KEY not configured in .env")
                return False
        except:
            print("⚠️ Could not load .env file")
            return False
    else:
        print("⚠️ .env file not found")
        print("💡 Copy from .env.example and add your API key")
        return False

def main():
    """Run all tests"""
    print("🚀 Cofive Agentic RAG - System Check")
    print("=" * 50)
    
    tests = [
        ("Basic Imports", test_imports),
        ("Python-dotenv", test_dotenv),
        ("Directory Structure", test_directory_structure),
        ("Sample Data", test_data_files),
        ("Environment Setup", test_env_setup),
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n🔍 {test_name}...")
        try:
            success = test_func()
            results.append((test_name, success))
        except Exception as e:
            print(f"❌ Test failed: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 Test Results")
    print("=" * 50)
    
    passed = 0
    for test_name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status:10} {test_name}")
        if success:
            passed += 1
    
    print(f"\n📈 {passed}/{len(results)} tests passed")
    
    if passed == len(results):
        print("\n🎉 All tests passed! System is ready.")
        print("\n🚀 Next steps:")
        print("1. Set your OpenAI API key in .env file")
        print("2. Run: python main.py")
    else:
        print("\n⚠️ Some issues found. Please fix them before running the system.")
        
        if not any(result[1] for result in results if result[0] == "Environment Setup"):
            print("\n💡 Quick fix for environment:")
            print("1. cp .env.example .env")
            print("2. Edit .env and add your OpenAI API key")

if __name__ == "__main__":
    main()
