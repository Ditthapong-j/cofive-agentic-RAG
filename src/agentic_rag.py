"""
Agentic RAG system with tool support and conversation memory.
"""
import logging
from typing import List, Dict, Any, Optional
import json

try:
    from langchain.agents import AgentExecutor, create_openai_tools_agent
    from langchain_community.chat_models import ChatOpenAI
    from langchain.memory import ConversationBufferWindowMemory
    from langchain.schema import Document, BaseMessage
    from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
    from langchain.tools import Tool
    from .vector_store import VectorStoreManager
    from .tools import create_rag_tools
    DEPENDENCIES_AVAILABLE = True
except ImportError as e:
    logging.warning(f"Agentic RAG dependencies not available: {e}")
    DEPENDENCIES_AVAILABLE = False


class AgenticRAG:
    """Agentic RAG system with tools and conversation memory."""
    
    def __init__(self, 
                 vector_store_manager: VectorStoreManager,
                 model_name: str = "gpt-5-mini",
                 temperature: float = 0.7,
                 memory_window: int = 10):
        """
        Initialize AgenticRAG.
        
        Args:
            vector_store_manager: Vector store manager instance
            model_name: OpenAI model to use
            temperature: Model temperature
            memory_window: Number of conversation turns to remember
        """
        self.vector_store_manager = vector_store_manager
        self.model_name = model_name
        self.temperature = temperature
        self.memory_window = memory_window
        
        if DEPENDENCIES_AVAILABLE:
            try:
                self.llm = ChatOpenAI(
                    model_name=model_name,
                    temperature=temperature
                )
                
                self.memory = ConversationBufferWindowMemory(
                    k=memory_window,
                    memory_key="chat_history",
                    return_messages=True
                )
                
                self.tools = create_rag_tools(vector_store_manager)
                self.agent_executor = self._create_agent()
                
            except Exception as e:
                logging.error(f"Failed to initialize AgenticRAG: {e}")
                self.llm = None
                self.agent_executor = None
        else:
            self.llm = None
            self.agent_executor = None

    def _create_agent(self) -> Optional[AgentExecutor]:
        """Create the OpenAI tools agent."""
        if not self.llm or not self.tools:
            return None
            
        try:
            # Define the prompt template
            prompt = ChatPromptTemplate.from_messages([
                ("system", """You are a helpful AI assistant with access to a document retrieval system.
                
Use the available tools to search for relevant information to answer user questions.
When you retrieve documents, summarize the key information and provide specific details.
If you can't find relevant information in the documents, say so clearly.

Always be helpful, accurate, and cite your sources when possible."""),
                MessagesPlaceholder(variable_name="chat_history"),
                ("human", "{input}"),
                MessagesPlaceholder(variable_name="agent_scratchpad"),
            ])
            
            # Create the agent
            agent = create_openai_tools_agent(
                llm=self.llm,
                tools=self.tools,
                prompt=prompt
            )
            
            # Create agent executor
            agent_executor = AgentExecutor(
                agent=agent,
                tools=self.tools,
                memory=self.memory,
                verbose=True,
                handle_parsing_errors=True,
                max_iterations=5
            )
            
            return agent_executor
            
        except Exception as e:
            logging.error(f"Error creating agent: {e}")
            return None

    def query(self, question: str) -> Dict[str, Any]:
        """
        Query the agentic RAG system.
        
        Args:
            question: User question
            
        Returns:
            Dictionary containing response and metadata
        """
        if not DEPENDENCIES_AVAILABLE:
            return {
                "answer": "AgenticRAG system not available. Please install required dependencies.",
                "sources": [],
                "error": "Dependencies not available",
                "success": False
            }
            
        if not self.agent_executor:
            return {
                "answer": "AgenticRAG system not properly initialized.",
                "sources": [],
                "error": "System not initialized",
                "success": False
            }
        
        try:
            # Execute the agent
            logging.info(f"Processing query: {question[:50]}...")
            result = self.agent_executor.invoke({"input": question})
            
            # Extract information
            answer = result.get("output", "No answer generated")
            
            # Try to extract sources from tool calls or memory
            sources = self._extract_sources_from_memory()
            
            logging.info(f"Query processed successfully. Answer length: {len(answer)} chars")
            
            return {
                "answer": answer,
                "sources": sources,
                "model": self.model_name,
                "success": True
            }
            
        except Exception as e:
            error_msg = str(e)
            logging.error(f"Error in query processing: {error_msg}")
            
            # Check for specific ChatOpenAI errors and provide helpful feedback
            if "model" in error_msg and "field" in error_msg:
                error_msg = "ChatOpenAI model configuration error. This may be due to LangChain version compatibility."
                logging.error("ChatOpenAI model field error detected - check LangChain version compatibility")
            
            return {
                "answer": f"Error processing query: {error_msg}",
                "sources": [],
                "error": error_msg,
                "success": False
            }

    def chat(self, message: str) -> str:
        """
        Simple chat interface.
        
        Args:
            message: User message
            
        Returns:
            Assistant response
        """
        result = self.query(message)
        return result.get("answer", "Sorry, I couldn't process your request.")

    def _extract_sources_from_memory(self) -> List[str]:
        """Extract sources from recent memory."""
        sources = []
        try:
            if self.memory and hasattr(self.memory, 'chat_memory'):
                messages = self.memory.chat_memory.messages[-10:]  # Last 10 messages
                for message in messages:
                    if hasattr(message, 'content'):
                        content = message.content
                        # Look for source mentions in the content
                        if 'source:' in content.lower():
                            lines = content.split('\n')
                            for line in lines:
                                if 'source:' in line.lower():
                                    source = line.split('source:', 1)[1].strip()
                                    if source and source not in sources:
                                        sources.append(source)
        except Exception as e:
            logging.error(f"Error extracting sources: {e}")
        
        return sources

    def get_conversation_history(self) -> List[Dict[str, Any]]:
        """Get conversation history."""
        history = []
        try:
            if self.memory and hasattr(self.memory, 'chat_memory'):
                messages = self.memory.chat_memory.messages
                for message in messages:
                    if hasattr(message, 'content'):
                        history.append({
                            "type": message.__class__.__name__,
                            "content": message.content
                        })
        except Exception as e:
            logging.error(f"Error getting conversation history: {e}")
        
        return history

    def clear_memory(self) -> bool:
        """Clear conversation memory."""
        try:
            if self.memory:
                self.memory.clear()
                logging.info("Conversation memory cleared")
                return True
        except Exception as e:
            logging.error(f"Error clearing memory: {e}")
        
        return False

    def get_available_tools(self) -> List[Dict[str, str]]:
        """Get list of available tools."""
        if not self.tools:
            return []
            
        return [
            {
                "name": tool.name,
                "description": tool.description
            }
            for tool in self.tools
        ]

    def update_model(self, model_name: str, temperature: float = None) -> bool:
        """Update the model configuration."""
        try:
            if temperature is None:
                temperature = self.temperature
                
            self.model_name = model_name
            self.temperature = temperature
            
            if DEPENDENCIES_AVAILABLE:
                self.llm = ChatOpenAI(
                    model_name=model_name,
                    temperature=temperature
                )
                self.agent_executor = self._create_agent()
                
            logging.info(f"Updated model to {model_name}")
            return True
            
        except Exception as e:
            logging.error(f"Error updating model: {e}")
            return False
