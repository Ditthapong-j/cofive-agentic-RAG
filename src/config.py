"""
Configuration settings for Agentic RAG system
"""
import os
from dataclasses import dataclass
from typing import Optional


@dataclass
class ModelConfig:
    """Configuration for language models"""
    name: str = "gpt-3.5-turbo"
    temperature: float = 0.1
    max_tokens: Optional[int] = None
    top_p: float = 1.0


@dataclass
class EmbeddingConfig:
    """Configuration for embeddings"""
    model: str = "text-embedding-ada-002"
    chunk_size: int = 1000
    chunk_overlap: int = 200


@dataclass
class VectorStoreConfig:
    """Configuration for vector store"""
    persist_directory: str = "./vectorstore"
    collection_name: str = "documents"
    search_k: int = 4
    search_type: str = "similarity"


@dataclass
class AgentConfig:
    """Configuration for agent"""
    max_iterations: int = 10
    verbose: bool = True
    return_intermediate_steps: bool = True


@dataclass
class SystemConfig:
    """Main system configuration"""
    model: ModelConfig = ModelConfig()
    embedding: EmbeddingConfig = EmbeddingConfig()
    vector_store: VectorStoreConfig = VectorStoreConfig()
    agent: AgentConfig = AgentConfig()
    
    # API Keys
    openai_api_key: Optional[str] = None
    langchain_api_key: Optional[str] = None
    
    # Paths
    data_directory: str = "./data"
    
    def __post_init__(self):
        """Load API keys from environment if not provided"""
        if not self.openai_api_key:
            self.openai_api_key = os.getenv("OPENAI_API_KEY")
        
        if not self.langchain_api_key:
            self.langchain_api_key = os.getenv("LANGCHAIN_API_KEY")
    
    def validate(self) -> bool:
        """Validate configuration"""
        if not self.openai_api_key:
            raise ValueError("OPENAI_API_KEY is required")
        
        return True


# Default configuration instance
default_config = SystemConfig()


def get_config() -> SystemConfig:
    """Get the default configuration"""
    return default_config


def update_config(**kwargs) -> SystemConfig:
    """Update the default configuration"""
    for key, value in kwargs.items():
        if hasattr(default_config, key):
            setattr(default_config, key, value)
    return default_config
