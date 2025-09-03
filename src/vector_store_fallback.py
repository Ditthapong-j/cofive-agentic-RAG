"""
Vector Store Manager with FAISS fallback for SQLite compatibility issues
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
except ImportError:
    FAISS_AVAILABLE = False

try:
    from langchain_community.vectorstores import Chroma
    CHROMA_AVAILABLE = True
except ImportError:
    CHROMA_AVAILABLE = False

class VectorStoreFallbackManager:
    """Vector store manager with automatic fallback from ChromaDB to FAISS"""
    
    def __init__(self, persist_directory: str = "vectorstore_fallback"):
        self.persist_directory = Path(persist_directory)
        self.persist_directory.mkdir(exist_ok=True)
        
        self.embeddings = None
        self.vectorstore = None
        self.store_type = None
        
        # Initialize embeddings
        try:
            self.embeddings = OpenAIEmbeddings()
        except Exception as e:
            print(f"Failed to initialize OpenAI embeddings: {e}")
            return
        
        # Try to load existing store or create new one
        self._initialize_vectorstore()
    
    def _initialize_vectorstore(self):
        """Initialize vector store with fallback logic"""
        
        # First try to load existing FAISS store
        faiss_path = self.persist_directory / "faiss_index"
        if faiss_path.exists() and FAISS_AVAILABLE:
            try:
                self.vectorstore = FAISS.load_local(
                    str(faiss_path), 
                    self.embeddings,
                    allow_dangerous_deserialization=True
                )
                self.store_type = "faiss"
                print("✅ Loaded existing FAISS vector store")
                return
            except Exception as e:
                print(f"Failed to load FAISS store: {e}")
        
        # Try to load existing Chroma store
        chroma_path = self.persist_directory / "chroma"
        if chroma_path.exists() and CHROMA_AVAILABLE:
            try:
                self.vectorstore = Chroma(
                    persist_directory=str(chroma_path),
                    embedding_function=self.embeddings
                )
                self.store_type = "chroma"
                print("✅ Loaded existing Chroma vector store")
                return
            except Exception as e:
                print(f"Failed to load Chroma store (SQLite issue): {e}")
        
        # Create new vector store - prefer FAISS for compatibility
        if FAISS_AVAILABLE:
            self._create_faiss_store()
        elif CHROMA_AVAILABLE:
            self._create_chroma_store()
        else:
            raise ImportError("Neither FAISS nor ChromaDB is available")
    
    def _create_faiss_store(self):
        """Create new FAISS vector store"""
        try:
            # Create empty FAISS store
            dummy_docs = [Document(page_content="dummy", metadata={})]
            self.vectorstore = FAISS.from_documents(dummy_docs, self.embeddings)
            
            # Remove dummy document
            self.vectorstore.delete([self.vectorstore.index_to_docstore_id[0]])
            
            self.store_type = "faiss"
            print("✅ Created new FAISS vector store")
        except Exception as e:
            print(f"Failed to create FAISS store: {e}")
            raise
    
    def _create_chroma_store(self):
        """Create new Chroma vector store"""
        try:
            chroma_path = self.persist_directory / "chroma"
            self.vectorstore = Chroma(
                persist_directory=str(chroma_path),
                embedding_function=self.embeddings
            )
            self.store_type = "chroma"
            print("✅ Created new Chroma vector store")
        except Exception as e:
            print(f"Failed to create Chroma store: {e}")
            raise
    
    def add_documents(self, documents: List[Document]) -> bool:
        """Add documents to vector store"""
        if not self.vectorstore:
            return False
        
        try:
            self.vectorstore.add_documents(documents)
            self._save_vectorstore()
            return True
        except Exception as e:
            print(f"Error adding documents: {e}")
            return False
    
    def similarity_search(self, query: str, k: int = 5) -> List[Document]:
        """Search for similar documents"""
        if not self.vectorstore:
            return []
        
        try:
            return self.vectorstore.similarity_search(query, k=k)
        except Exception as e:
            print(f"Error searching documents: {e}")
            return []
    
    def get_document_count(self) -> int:
        """Get total number of documents in vector store"""
        if not self.vectorstore:
            return 0
        
        try:
            if self.store_type == "faiss":
                return self.vectorstore.index.ntotal
            elif self.store_type == "chroma":
                return self.vectorstore._collection.count()
            return 0
        except Exception as e:
            print(f"Error getting document count: {e}")
            return 0
    
    def clear_vectorstore(self) -> bool:
        """Clear all documents from vector store"""
        try:
            if self.store_type == "faiss":
                # Recreate FAISS store
                self._create_faiss_store()
            elif self.store_type == "chroma":
                # Delete and recreate Chroma store
                import shutil
                chroma_path = self.persist_directory / "chroma"
                if chroma_path.exists():
                    shutil.rmtree(chroma_path)
                self._create_chroma_store()
            
            self._save_vectorstore()
            return True
        except Exception as e:
            print(f"Error clearing vector store: {e}")
            return False
    
    def _save_vectorstore(self):
        """Save vector store to disk"""
        try:
            if self.store_type == "faiss":
                faiss_path = self.persist_directory / "faiss_index"
                self.vectorstore.save_local(str(faiss_path))
            elif self.store_type == "chroma":
                # Chroma auto-persists
                pass
        except Exception as e:
            print(f"Error saving vector store: {e}")
    
    def get_retriever(self, search_kwargs: Optional[dict] = None):
        """Get retriever for the vector store"""
        if not self.vectorstore:
            return None
        
        search_kwargs = search_kwargs or {"k": 5}
        return self.vectorstore.as_retriever(search_kwargs=search_kwargs)
