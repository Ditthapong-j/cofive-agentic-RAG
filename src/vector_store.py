"""
Vector Store Manager for document embeddings and similarity search.
"""
import os
import logging
from typing import List, Optional, Tuple, Any
import tempfile
import shutil

try:
    from langchain.schema import Document
    from langchain_openai import OpenAIEmbeddings
    from langchain_chroma import Chroma
    from langchain_community.vectorstores import FAISS
    from langchain.vectorstores.base import VectorStore
    DEPENDENCIES_AVAILABLE = True
except ImportError as e:
    logging.warning(f"Vector store dependencies not available: {e}")
    # Fallback to community imports if langchain_chroma not available
    try:
        from langchain.schema import Document
        from langchain_openai import OpenAIEmbeddings
        from langchain_community.vectorstores import Chroma, FAISS
        from langchain.vectorstores.base import VectorStore
        DEPENDENCIES_AVAILABLE = True
    except ImportError as e2:
        logging.warning(f"Fallback vector store dependencies not available: {e2}")
        DEPENDENCIES_AVAILABLE = False


class VectorStoreManager:
    """Manages vector stores for document embeddings and similarity search."""
    
    def __init__(self, 
                 embeddings_model: str = "text-embedding-ada-002",
                 persist_directory: str = "./chroma_db",
                 use_chroma: bool = True):
        """
        Initialize VectorStoreManager.
        
        Args:
            embeddings_model: OpenAI embeddings model to use
            persist_directory: Directory to persist ChromaDB
            use_chroma: Whether to use ChromaDB (True) or FAISS (False)
        """
        self.embeddings_model = embeddings_model
        self.persist_directory = persist_directory
        self.use_chroma = use_chroma
        self.vector_store: Optional[VectorStore] = None
        self.documents: List[Document] = []
        
        if DEPENDENCIES_AVAILABLE:
            try:
                self.embeddings = OpenAIEmbeddings(model=embeddings_model)
            except Exception as e:
                logging.warning(f"Failed to initialize OpenAI embeddings: {e}")
                self.embeddings = None
        else:
            self.embeddings = None

    def _create_chroma_store(self, documents: List[Document]) -> Optional[VectorStore]:
        """Create ChromaDB vector store."""
        try:
            # Ensure persist directory exists
            os.makedirs(self.persist_directory, exist_ok=True)
            
            vector_store = Chroma.from_documents(
                documents=documents,
                embedding=self.embeddings,
                persist_directory=self.persist_directory
            )
            vector_store.persist()
            return vector_store
        except Exception as e:
            logging.error(f"Failed to create ChromaDB store: {e}")
            return None

    def _create_faiss_store(self, documents: List[Document]) -> Optional[VectorStore]:
        """Create FAISS vector store."""
        try:
            vector_store = FAISS.from_documents(
                documents=documents,
                embedding=self.embeddings
            )
            return vector_store
        except Exception as e:
            logging.error(f"Failed to create FAISS store: {e}")
            return None

    def _create_memory_store(self, documents: List[Document]) -> 'MemoryVectorStore':
        """Create in-memory vector store as fallback."""
        return MemoryVectorStore(documents)

    def add_documents(self, documents: List[Document]) -> bool:
        """Add documents to the vector store."""
        if not documents:
            logging.warning("No documents provided")
            return False
            
        if not DEPENDENCIES_AVAILABLE:
            logging.warning("Dependencies not available, using memory store")
            self.vector_store = self._create_memory_store(documents)
            self.documents.extend(documents)
            return True
            
        if not self.embeddings:
            logging.error("Embeddings not available")
            return False

        self.documents.extend(documents)
        
        # Try ChromaDB first, then FAISS, then memory
        if self.use_chroma:
            self.vector_store = self._create_chroma_store(self.documents)
            if self.vector_store:
                logging.info(f"Created ChromaDB store with {len(self.documents)} documents")
                return True
        
        # Fallback to FAISS
        logging.info("Falling back to FAISS vector store")
        self.vector_store = self._create_faiss_store(self.documents)
        if self.vector_store:
            logging.info(f"Created FAISS store with {len(self.documents)} documents")
            return True
            
        # Final fallback to memory
        logging.warning("Falling back to memory vector store")
        self.vector_store = self._create_memory_store(self.documents)
        return True

    def similarity_search(self, query: str, k: int = 4) -> List[Document]:
        """Perform similarity search."""
        if not self.vector_store:
            logging.error("Vector store not initialized")
            return []
            
        try:
            return self.vector_store.similarity_search(query, k=k)
        except Exception as e:
            logging.error(f"Error in similarity search: {e}")
            return []

    def similarity_search_with_score(self, query: str, k: int = 4) -> List[Tuple[Document, float]]:
        """Perform similarity search with scores."""
        if not self.vector_store:
            logging.error("Vector store not initialized")
            return []
            
        try:
            if hasattr(self.vector_store, 'similarity_search_with_score'):
                return self.vector_store.similarity_search_with_score(query, k=k)
            else:
                # Fallback for stores without score support
                docs = self.vector_store.similarity_search(query, k=k)
                return [(doc, 1.0) for doc in docs]
        except Exception as e:
            logging.error(f"Error in similarity search with score: {e}")
            return []

    def get_document_count(self) -> int:
        """Get the number of documents in the store."""
        return len(self.documents)

    def reset(self) -> bool:
        """Reset the vector store."""
        try:
            self.documents = []
            self.vector_store = None
            
            # Clean up ChromaDB directory if it exists
            if os.path.exists(self.persist_directory):
                shutil.rmtree(self.persist_directory)
                
            logging.info("Vector store reset successfully")
            return True
        except Exception as e:
            logging.error(f"Error resetting vector store: {e}")
            return False

    def load_existing_store(self) -> bool:
        """Load existing ChromaDB store if available."""
        if not DEPENDENCIES_AVAILABLE or not self.embeddings:
            return False
            
        try:
            if os.path.exists(self.persist_directory) and os.listdir(self.persist_directory):
                self.vector_store = Chroma(
                    persist_directory=self.persist_directory,
                    embedding_function=self.embeddings
                )
                logging.info("Loaded existing ChromaDB store")
                return True
        except Exception as e:
            logging.error(f"Failed to load existing store: {e}")
            
        return False


class MemoryVectorStore:
    """Simple in-memory vector store for fallback."""
    
    def __init__(self, documents: List[Document]):
        self.documents = documents
    
    def similarity_search(self, query: str, k: int = 4) -> List[Document]:
        """Simple keyword-based search."""
        query_lower = query.lower()
        scored_docs = []
        
        for doc in self.documents:
            content_lower = doc.page_content.lower()
            score = sum(1 for word in query_lower.split() if word in content_lower)
            if score > 0:
                scored_docs.append((doc, score))
        
        # Sort by score and return top k
        scored_docs.sort(key=lambda x: x[1], reverse=True)
        return [doc for doc, _ in scored_docs[:k]]
