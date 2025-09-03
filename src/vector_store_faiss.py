"""
Simple FAISS-only vector store manager (no SQLite dependencies)
"""
import os
import pickle
from pathlib import Path
from typing import List, Optional, Any
import warnings
warnings.filterwarnings("ignore")

try:
    from langchain_community.vectorstores import FAISS
    from langchain_openai import OpenAIEmbeddings
    from langchain.schema import Document
    FAISS_AVAILABLE = True
except ImportError as e:
    print(f"FAISS import failed: {e}")
    FAISS_AVAILABLE = False

class FAISSVectorStore:
    """Simple FAISS-only vector store manager"""
    
    def __init__(self, persist_directory: str = "vectorstore_faiss"):
        self.persist_directory = Path(persist_directory)
        self.persist_directory.mkdir(exist_ok=True)
        
        self.embeddings = None
        self.vectorstore = None
        
        # Initialize embeddings
        try:
            self.embeddings = OpenAIEmbeddings()
            print("✅ OpenAI embeddings initialized")
        except Exception as e:
            print(f"❌ Failed to initialize OpenAI embeddings: {e}")
            return
        
        # Try to load existing store or create new one
        self._initialize_vectorstore()
    
    def _initialize_vectorstore(self):
        """Initialize FAISS vector store"""
        
        if not FAISS_AVAILABLE:
            raise ImportError("FAISS is not available. Install with: pip install faiss-cpu")
        
        # Try to load existing FAISS store
        faiss_path = self.persist_directory / "faiss_index"
        if faiss_path.exists():
            try:
                self.vectorstore = FAISS.load_local(
                    str(faiss_path), 
                    self.embeddings,
                    allow_dangerous_deserialization=True
                )
                print("✅ Loaded existing FAISS vector store")
                return
            except Exception as e:
                print(f"⚠️ Failed to load existing FAISS store: {e}")
                print("🔄 Creating new store...")
        
        # Create new FAISS store
        self._create_new_store()
    
    def _create_new_store(self):
        """Create new FAISS vector store"""
        try:
            # Create empty FAISS store with dummy document
            dummy_docs = [Document(page_content="initialization dummy", metadata={"type": "dummy"})]
            self.vectorstore = FAISS.from_documents(dummy_docs, self.embeddings)
            
            # Remove dummy document immediately
            if hasattr(self.vectorstore, 'docstore') and len(self.vectorstore.docstore._dict) > 0:
                dummy_id = list(self.vectorstore.docstore._dict.keys())[0]
                del self.vectorstore.docstore._dict[dummy_id]
                # Reset index
                import numpy as np
                self.vectorstore.index = type(self.vectorstore.index)(self.embeddings.embed_query("test").__len__())
            
            print("✅ Created new FAISS vector store")
            self._save_vectorstore()
        except Exception as e:
            print(f"❌ Failed to create FAISS store: {e}")
            raise
    
    def add_documents(self, documents: List[Document]) -> bool:
        """Add documents to vector store"""
        if not self.vectorstore or not documents:
            return False
        
        try:
            # Filter out empty documents
            valid_docs = [doc for doc in documents if doc.page_content.strip()]
            
            if not valid_docs:
                print("⚠️ No valid documents to add")
                return False
            
            print(f"📄 Adding {len(valid_docs)} documents...")
            
            # If vectorstore is empty, recreate it with the documents
            if self.get_document_count() == 0:
                self.vectorstore = FAISS.from_documents(valid_docs, self.embeddings)
            else:
                self.vectorstore.add_documents(valid_docs)
            
            self._save_vectorstore()
            print(f"✅ Added {len(valid_docs)} documents successfully")
            return True
            
        except Exception as e:
            print(f"❌ Error adding documents: {e}")
            return False
    
    def similarity_search(self, query: str, k: int = 5) -> List[Document]:
        """Search for similar documents"""
        if not self.vectorstore:
            return []
        
        try:
            return self.vectorstore.similarity_search(query, k=k)
        except Exception as e:
            print(f"❌ Error searching documents: {e}")
            return []
    
    def get_document_count(self) -> int:
        """Get total number of documents in vector store"""
        if not self.vectorstore:
            return 0
        
        try:
            # Count non-dummy documents
            count = 0
            if hasattr(self.vectorstore, 'docstore'):
                for doc_id, doc in self.vectorstore.docstore._dict.items():
                    if doc.metadata.get("type") != "dummy":
                        count += 1
            return count
        except Exception as e:
            print(f"❌ Error getting document count: {e}")
            return 0
    
    def clear_vectorstore(self) -> bool:
        """Clear all documents from vector store"""
        try:
            self._create_new_store()
            print("🗑️ Vector store cleared")
            return True
        except Exception as e:
            print(f"❌ Error clearing vector store: {e}")
            return False
    
    def _save_vectorstore(self):
        """Save vector store to disk"""
        try:
            if self.vectorstore:
                faiss_path = self.persist_directory / "faiss_index"
                self.vectorstore.save_local(str(faiss_path))
        except Exception as e:
            print(f"⚠️ Warning: Could not save vector store: {e}")
    
    def get_retriever(self, search_kwargs: Optional[dict] = None):
        """Get retriever for the vector store"""
        if not self.vectorstore:
            return None
        
        search_kwargs = search_kwargs or {"k": 5}
        return self.vectorstore.as_retriever(search_kwargs=search_kwargs)
