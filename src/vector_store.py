"""
Vector Store Module for Agentic RAG
"""
import os
from typing import List, Optional
from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain_core.documents import Document


class VectorStoreManager:
    """Vector store manager using Chroma"""
    
    def __init__(self, persist_directory: str = "./vectorstore", embedding_model: str = "text-embedding-ada-002"):
        self.persist_directory = persist_directory
        self.embedding_model = embedding_model
        self.embeddings = OpenAIEmbeddings(model=embedding_model)
        self.vectorstore = None
        
        # Create directory if it doesn't exist
        os.makedirs(persist_directory, exist_ok=True)
    
    def create_vectorstore(self, documents: List[Document]) -> None:
        """Create a new vector store from documents"""
        if not documents:
            raise ValueError("No documents provided to create vector store")
        
        print(f"Creating vector store with {len(documents)} documents...")
        self.vectorstore = Chroma.from_documents(
            documents=documents,
            embedding=self.embeddings,
            persist_directory=self.persist_directory
        )
        print("Vector store created successfully!")
    
    def load_vectorstore(self) -> bool:
        """Load existing vector store"""
        try:
            self.vectorstore = Chroma(
                persist_directory=self.persist_directory,
                embedding_function=self.embeddings
            )
            # Check if vectorstore has any documents
            if self.vectorstore._collection.count() > 0:
                print(f"Loaded existing vector store with {self.vectorstore._collection.count()} documents")
                return True
            else:
                print("Vector store is empty")
                return False
        except Exception as e:
            print(f"Error loading vector store: {e}")
            return False
    
    def add_documents(self, documents: List[Document]) -> None:
        """Add new documents to existing vector store"""
        if not self.vectorstore:
            self.create_vectorstore(documents)
        else:
            print(f"Adding {len(documents)} documents to vector store...")
            self.vectorstore.add_documents(documents)
            print("Documents added successfully!")
    
    def search(self, query: str, k: int = 4) -> List[Document]:
        """Search for similar documents"""
        if not self.vectorstore:
            raise ValueError("Vector store not initialized. Load or create vector store first.")
        
        return self.vectorstore.similarity_search(query, k=k)
    
    def search_with_score(self, query: str, k: int = 4) -> List[tuple]:
        """Search for similar documents with similarity scores"""
        if not self.vectorstore:
            raise ValueError("Vector store not initialized. Load or create vector store first.")
        
        return self.vectorstore.similarity_search_with_score(query, k=k)
    
    def get_retriever(self, search_type: str = "similarity", k: int = 4):
        """Get retriever for RAG chain"""
        if not self.vectorstore:
            raise ValueError("Vector store not initialized. Load or create vector store first.")
        
        return self.vectorstore.as_retriever(
            search_type=search_type,
            search_kwargs={"k": k}
        )
    
    def delete_collection(self) -> None:
        """Delete the vector store collection"""
        if self.vectorstore:
            self.vectorstore.delete_collection()
            print("Vector store collection deleted")
    
    def get_document_count(self) -> int:
        """Get the number of documents in vector store"""
        if not self.vectorstore:
            return 0
        return self.vectorstore._collection.count()
