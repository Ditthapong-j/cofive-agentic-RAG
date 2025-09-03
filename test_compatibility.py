#!/usr/bin/env python3
"""
Simple test for SQLite and vector store alternatives
"""
import sys
import os

print("🔍 Testing system compatibility...")

# Check SQLite version
try:
    import sqlite3
    sqlite_version = sqlite3.sqlite_version
    print(f"📦 SQLite version: {sqlite_version}")
    
    version_parts = sqlite_version.split('.')
    major, minor = int(version_parts[0]), int(version_parts[1])
    
    if (major > 3) or (major == 3 and minor >= 35):
        print("✅ SQLite version is compatible with ChromaDB")
        chroma_compatible = True
    else:
        print("❌ SQLite version is too old for ChromaDB (requires ≥ 3.35.0)")
        chroma_compatible = False
        
except Exception as e:
    print(f"❌ SQLite check failed: {e}")
    chroma_compatible = False

# Check ChromaDB
try:
    import chromadb
    print("✅ ChromaDB is available")
    if chroma_compatible:
        print("✅ ChromaDB should work")
    else:
        print("⚠️ ChromaDB available but SQLite too old")
except ImportError:
    print("❌ ChromaDB not installed")

# Check FAISS
try:
    import faiss
    print("✅ FAISS is available")
    faiss_available = True
except ImportError:
    print("❌ FAISS not installed")
    faiss_available = False

# Check LangChain components
try:
    from langchain_community.vectorstores import FAISS as LangchainFAISS
    print("✅ LangChain FAISS integration available")
except ImportError:
    print("❌ LangChain FAISS integration not available")

try:
    from langchain_openai import OpenAIEmbeddings
    print("✅ OpenAI embeddings available")
except ImportError:
    print("❌ OpenAI embeddings not available")

# Recommendations
print("\n🛠️ Recommendations:")
if chroma_compatible:
    print("✅ Use ChromaDB (recommended)")
elif faiss_available:
    print("✅ Use FAISS as fallback")
else:
    print("❌ Install FAISS: pip install faiss-cpu")

print("\n📋 Summary:")
print(f"SQLite compatible: {chroma_compatible}")
print(f"FAISS available: {faiss_available}")

if not chroma_compatible and not faiss_available:
    print("❌ No compatible vector store found")
    sys.exit(1)
else:
    print("✅ At least one vector store option available")
