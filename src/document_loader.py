"""
Document Loader Module for Agentic RAG
"""
import os
from typing import List, Optional
from langchain_community.document_loaders import PyPDFLoader, TextLoader, DirectoryLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
import requests
from bs4 import BeautifulSoup


class DocumentLoader:
    """Document loader class for various file types"""
    
    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 200):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            length_function=len,
        )
    
    def load_pdf(self, file_path: str) -> List[Document]:
        """Load PDF documents"""
        try:
            loader = PyPDFLoader(file_path)
            documents = loader.load()
            return self.text_splitter.split_documents(documents)
        except Exception as e:
            print(f"Error loading PDF {file_path}: {e}")
            return []
    
    def load_text(self, file_path: str) -> List[Document]:
        """Load text documents"""
        try:
            loader = TextLoader(file_path, encoding='utf-8')
            documents = loader.load()
            return self.text_splitter.split_documents(documents)
        except Exception as e:
            print(f"Error loading text file {file_path}: {e}")
            return []
    
    def load_directory(self, directory_path: str) -> List[Document]:
        """Load all documents from a directory"""
        documents = []
        
        for root, dirs, files in os.walk(directory_path):
            for file in files:
                file_path = os.path.join(root, file)
                file_ext = os.path.splitext(file)[1].lower()
                
                if file_ext == '.pdf':
                    documents.extend(self.load_pdf(file_path))
                elif file_ext in ['.txt', '.md']:
                    documents.extend(self.load_text(file_path))
        
        return documents
    
    def load_web_page(self, url: str) -> List[Document]:
        """Load content from a web page"""
        try:
            response = requests.get(url)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Remove script and style elements
            for script in soup(["script", "style"]):
                script.decompose()
            
            # Get text content
            text = soup.get_text()
            
            # Clean up whitespace
            lines = (line.strip() for line in text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            text = ' '.join(chunk for chunk in chunks if chunk)
            
            # Create document
            doc = Document(page_content=text, metadata={"source": url})
            return self.text_splitter.split_documents([doc])
            
        except Exception as e:
            print(f"Error loading web page {url}: {e}")
            return []
    
    def load_multiple_sources(self, sources: List[str]) -> List[Document]:
        """Load documents from multiple sources (files, directories, URLs)"""
        all_documents = []
        
        for source in sources:
            if source.startswith('http://') or source.startswith('https://'):
                # Web URL
                all_documents.extend(self.load_web_page(source))
            elif os.path.isfile(source):
                # Single file
                file_ext = os.path.splitext(source)[1].lower()
                if file_ext == '.pdf':
                    all_documents.extend(self.load_pdf(source))
                elif file_ext in ['.txt', '.md']:
                    all_documents.extend(self.load_text(source))
            elif os.path.isdir(source):
                # Directory
                all_documents.extend(self.load_directory(source))
            else:
                print(f"Unknown source type: {source}")
        
        return all_documents
