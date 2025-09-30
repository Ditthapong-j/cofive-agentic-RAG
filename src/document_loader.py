"""
Document Loader for various file types.
"""
import os
import logging
from typing import List, Union
from pathlib import Path

try:
    from langchain_community.document_loaders import PyPDFLoader, TextLoader, DirectoryLoader
    from langchain.text_splitter import RecursiveCharacterTextSplitter
    from langchain.schema import Document
    import requests
    from bs4 import BeautifulSoup
    DEPENDENCIES_AVAILABLE = True
except ImportError as e:
    logging.warning(f"Some dependencies not available: {e}")
    DEPENDENCIES_AVAILABLE = False


class DocumentLoader:
    """Handles loading and processing documents from various sources."""
    
    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 200):
        """
        Initialize DocumentLoader.
        
        Args:
            chunk_size: Size of text chunks
            chunk_overlap: Overlap between chunks
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        
        if DEPENDENCIES_AVAILABLE:
            self.text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=chunk_size,
                chunk_overlap=chunk_overlap,
                length_function=len,
            )
        else:
            self.text_splitter = None

    def load_pdf(self, file_path: str) -> List[Document]:
        """Load PDF file."""
        if not DEPENDENCIES_AVAILABLE:
            raise ImportError("PDF loading requires PyPDF2. Install with: pip install PyPDF2")
            
        try:
            loader = PyPDFLoader(file_path)
            documents = loader.load()
            return self.text_splitter.split_documents(documents) if self.text_splitter else documents
        except Exception as e:
            logging.error(f"Error loading PDF {file_path}: {e}")
            return []

    def load_text(self, file_path: str) -> List[Document]:
        """Load text file."""
        if not DEPENDENCIES_AVAILABLE:
            raise ImportError("Text loading requires langchain. Install with: pip install langchain")
            
        try:
            loader = TextLoader(file_path, encoding='utf-8')
            documents = loader.load()
            return self.text_splitter.split_documents(documents) if self.text_splitter else documents
        except Exception as e:
            logging.error(f"Error loading text file {file_path}: {e}")
            return []

    def load_directory(self, directory_path: str, glob_pattern: str = "**/*") -> List[Document]:
        """Load all documents from a directory."""
        if not DEPENDENCIES_AVAILABLE:
            raise ImportError("Directory loading requires langchain. Install with: pip install langchain")
            
        try:
            loader = DirectoryLoader(
                directory_path,
                glob=glob_pattern,
                loader_cls=TextLoader,
                loader_kwargs={'encoding': 'utf-8'},
                show_progress=True
            )
            documents = loader.load()
            return self.text_splitter.split_documents(documents) if self.text_splitter else documents
        except Exception as e:
            logging.error(f"Error loading directory {directory_path}: {e}")
            return []

    def load_web_page(self, url: str) -> List[Document]:
        """Load content from a web page."""
        try:
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Remove script and style elements
            for script in soup(["script", "style"]):
                script.decompose()
            
            # Get text content
            text = soup.get_text()
            lines = (line.strip() for line in text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            text = ' '.join(chunk for chunk in chunks if chunk)
            
            document = Document(page_content=text, metadata={"source": url})
            
            if self.text_splitter:
                return self.text_splitter.split_documents([document])
            else:
                return [document]
                
        except Exception as e:
            logging.error(f"Error loading web page {url}: {e}")
            return []

    def load_file(self, file_path: str) -> List[Document]:
        """Load a file based on its extension."""
        path = Path(file_path)
        extension = path.suffix.lower()
        
        if extension == '.pdf':
            return self.load_pdf(file_path)
        elif extension in ['.txt', '.md', '.py', '.js', '.html', '.css']:
            return self.load_text(file_path)
        else:
            logging.warning(f"Unsupported file type: {extension}")
            return []
