#!/usr/bin/env python3
"""
Setup script for Agentic RAG system
"""
import os
import subprocess
import sys
from pathlib import Path


def install_requirements():
    """Install required packages"""
    print("Installing required packages...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Packages installed successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error installing packages: {e}")
        return False


def create_env_file():
    """Create .env file if it doesn't exist"""
    env_file = Path(".env")
    env_example = Path(".env.example")
    
    if not env_file.exists() and env_example.exists():
        print("Creating .env file from .env.example...")
        with open(env_example, 'r') as src, open(env_file, 'w') as dst:
            dst.write(src.read())
        print("✅ .env file created! Please update it with your actual API keys.")
    elif env_file.exists():
        print("ℹ️ .env file already exists.")
    else:
        print("⚠️ No .env.example file found.")


def create_sample_data():
    """Create sample data if data directory is empty"""
    data_dir = Path("data")
    data_dir.mkdir(exist_ok=True)
    
    if not any(data_dir.iterdir()):
        print("Creating sample data...")
        
        sample_content = """
# Agentic RAG System Documentation

## Overview
The Agentic RAG (Retrieval-Augmented Generation) system is an advanced AI framework that combines:

1. **Document Retrieval**: Efficiently search through large document collections using vector embeddings
2. **Agent-Based Reasoning**: Intelligent decision-making about which tools to use for different queries
3. **Large Language Model Generation**: Generate comprehensive and accurate responses

## Key Components

### 1. Document Loader
- Supports multiple file formats: PDF, TXT, MD
- Can load from directories, individual files, or web URLs
- Automatic text chunking for optimal vector storage

### 2. Vector Store
- Uses Chroma vector database for efficient similarity search
- OpenAI embeddings for high-quality document representations
- Persistent storage for maintaining document collections

### 3. Agent Tools
- **Document Search**: Find relevant information from the knowledge base
- **Calculator**: Perform mathematical calculations
- **Web Search**: Access current information from the internet
- **Document Summary**: Generate comprehensive summaries of document collections

### 4. Conversational Memory
- Maintains context across multiple interactions
- Remembers previous questions and answers
- Supports conversation history clearing

## Use Cases

### Research and Knowledge Management
- Academic research with large document collections
- Corporate knowledge bases
- Technical documentation search
- Legal document analysis

### Educational Applications
- Student research assistance
- Course material exploration
- Homework help with source citation
- Literature review automation

### Business Intelligence
- Market research analysis
- Competitor intelligence
- Policy and procedure queries
- Training material assistance

## Getting Started

1. Install dependencies: `pip install -r requirements.txt`
2. Set up environment variables in `.env` file
3. Add documents to the `data/` directory
4. Run the system: `python main.py` or `streamlit run streamlit_app.py`

## Advanced Features

### Multi-Modal Search
The system can search across different types of content and combine results intelligently.

### Source Citation
All responses include references to the specific documents used, ensuring transparency and verifiability.

### Extensible Tool Framework
Easy to add new tools and capabilities to the agent based on specific needs.

### Performance Optimization
- Efficient vector storage and retrieval
- Optimized chunk sizes for different document types
- Configurable search parameters

## Best Practices

1. **Document Preparation**: Clean and well-structured documents work best
2. **Chunk Size**: Adjust chunk size based on your document types
3. **Query Formulation**: Be specific in your questions for better results
4. **Source Verification**: Always verify important information from the cited sources

## Troubleshooting

### Common Issues
- **API Key Errors**: Ensure OPENAI_API_KEY is set correctly
- **Empty Results**: Check if documents are properly loaded into vector store
- **Performance Issues**: Consider reducing chunk size or document count

### Support
For additional support and customization, refer to the LangChain documentation and OpenAI API guidelines.
"""
        
        with open(data_dir / "agentic_rag_docs.md", "w", encoding="utf-8") as f:
            f.write(sample_content)
        
        # Create another sample file about Python
        python_sample = """
# Python Programming Guide

## Introduction to Python
Python is a high-level, interpreted programming language known for its simplicity and readability.

## Key Features
- **Easy to Learn**: Simple syntax similar to English
- **Versatile**: Used for web development, data science, AI/ML, automation
- **Large Community**: Extensive libraries and community support
- **Cross-Platform**: Runs on Windows, macOS, Linux

## Data Types
- **Numbers**: int, float, complex
- **Strings**: Text data enclosed in quotes
- **Lists**: Ordered collections of items
- **Dictionaries**: Key-value pairs
- **Sets**: Unordered collections of unique items

## Control Structures
- **If-else statements**: Conditional execution
- **Loops**: for and while loops for repetition
- **Functions**: Reusable blocks of code
- **Classes**: Object-oriented programming

## Libraries for AI/ML
- **NumPy**: Numerical computing
- **Pandas**: Data manipulation and analysis
- **Scikit-learn**: Machine learning algorithms
- **TensorFlow/PyTorch**: Deep learning frameworks
- **LangChain**: Building LLM applications

## Best Practices
1. Follow PEP 8 style guidelines
2. Use meaningful variable names
3. Write docstrings for functions
4. Handle exceptions properly
5. Use virtual environments

## Example Code
```python
def greet(name):
    \"\"\"Simple greeting function\"\"\"
    return f"Hello, {name}!"

# Usage
message = greet("World")
print(message)
```

## Resources
- Official Python documentation: python.org
- Python Package Index (PyPI): pypi.org
- Online tutorials and courses
- Community forums and Stack Overflow
"""
        
        with open(data_dir / "python_guide.md", "w", encoding="utf-8") as f:
            f.write(python_sample)
        
        print("✅ Sample data created in data/ directory!")
    else:
        print("ℹ️ Data directory already contains files.")


def main():
    """Main setup function"""
    print("🚀 Setting up Agentic RAG System...")
    print("-" * 50)
    
    # Install requirements
    if not install_requirements():
        print("❌ Setup failed during package installation.")
        return
    
    # Create .env file
    create_env_file()
    
    # Create sample data
    create_sample_data()
    
    print("-" * 50)
    print("✅ Setup completed successfully!")
    print("\nNext steps:")
    print("1. Update your .env file with actual API keys")
    print("2. Add your documents to the data/ directory")
    print("3. Run the system:")
    print("   - CLI: python main.py")
    print("   - Web UI: streamlit run streamlit_app.py")
    print("\n🎉 Happy querying!")


if __name__ == "__main__":
    main()
