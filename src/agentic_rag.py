"""
Agentic RAG Agent
"""
from typing import List, Optional, Any, Dict
from langchain_openai import ChatOpenAI
from langchain.agents import AgentExecutor, create_openai_tools_agent
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
from langchain.memory import ConversationBufferMemory
from src.vector_store import VectorStoreManager
from src.tools import get_tools


class AgenticRAG:
    """Agentic RAG system with reasoning capabilities"""
    
    def __init__(
        self,
        vector_store_manager: VectorStoreManager,
        model_name: str = "gpt-3.5-turbo",
        temperature: float = 0.1,
        max_iterations: int = 10,
        verbose: bool = True
    ):
        self.vector_store_manager = vector_store_manager
        self.model_name = model_name
        self.temperature = temperature
        self.max_iterations = max_iterations
        self.verbose = verbose
        
        # Initialize LLM
        self.llm = ChatOpenAI(
            model=model_name,
            temperature=temperature
        )
        
        # Initialize tools
        self.tools = get_tools(vector_store_manager, self.llm)
        
        # Initialize memory
        self.memory = ConversationBufferMemory(
            memory_key="chat_history",
            return_messages=True
        )
        
        # Create agent
        self._create_agent()
    
    def _create_agent(self):
        """Create the OpenAI tools agent"""
        
        # Define the prompt template
        prompt = ChatPromptTemplate.from_messages([
            ("system", self._get_system_prompt()),
            MessagesPlaceholder(variable_name="chat_history"),
            ("human", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad"),
        ])
        
        # Create agent
        agent = create_openai_tools_agent(
            llm=self.llm,
            tools=self.tools,
            prompt=prompt
        )
        
        # Create agent executor
        self.agent_executor = AgentExecutor(
            agent=agent,
            tools=self.tools,
            memory=self.memory,
            verbose=self.verbose,
            max_iterations=self.max_iterations,
            return_intermediate_steps=True,
            handle_parsing_errors=True
        )
    
    def _get_system_prompt(self) -> str:
        """Get the system prompt for the agent"""
        return """You are an intelligent AI assistant with access to a knowledge base containing documents in Thai and English. 

MANDATORY WORKFLOW:
1. ALWAYS use document_search tool first for any question
2. ANALYZE and PROCESS the search results
3. PROVIDE a complete answer based on the documents found
4. DO NOT just reference the source files - EXTRACT and SUMMARIZE the actual information

RESPONSE REQUIREMENTS:
- Give direct answers based on document content
- Quote specific information from the documents
- Synthesize information from multiple documents if needed
- Provide actionable information, not just file references
- If multiple relevant documents are found, combine the information intelligently

EXAMPLE OF GOOD RESPONSE:
"ตามเอกสารที่พบ วิธีแก้ปัญหาการลืมรหัสผ่าน Venio คือ: 
1. ติดต่อแอดมินเพื่อรีเซ็ตรหัสผ่าน
2. ใช้ฟีเจอร์ Forgot Password ในหน้าล็อกอิน
3. ตรวจสอบอีเมลเพื่อรับลิงก์รีเซ็ตรหัสผ่าน"

EXAMPLE OF BAD RESPONSE:
"คุณสามารถตรวจสอบข้อมูลเพิ่มเติมในเอกสาร file.txt"

SEARCH STRATEGY:
- For Python: search "Python", "โปรแกรม", "programming" 
- For Cofive: search "Cofive", "บริษัท", "company"
- For passwords/login: search "รหัสผ่าน", "password", "login", "เข้าสู่ระบบ"
- For Venio: search "Venio", "ระบบ"

Available tools:
- document_search: Search knowledge base (USE FIRST, PROCESS RESULTS)
- calculator: Mathematical calculations  
- document_summary: Document summaries
- web_search: Web search (only if no relevant documents)

Remember: EXTRACT, SYNTHESIZE, and PROVIDE complete answers from the documents. Never just point to files."""
    
    def query(self, question: str) -> Dict[str, Any]:
        """
        Process a query and return the response with intermediate steps
        
        Args:
            question: The user's question
            
        Returns:
            Dict containing the response and intermediate steps
        """
        try:
            result = self.agent_executor.invoke({"input": question})
            
            return {
                "answer": result["output"],
                "intermediate_steps": result.get("intermediate_steps", []),
                "success": True
            }
        except Exception as e:
            return {
                "answer": f"I encountered an error while processing your question: {str(e)}",
                "intermediate_steps": [],
                "success": False,
                "error": str(e)
            }
    
    def chat(self, message: str) -> str:
        """
        Simple chat interface
        
        Args:
            message: User message
            
        Returns:
            Agent's response
        """
        result = self.query(message)
        return result["answer"]
    
    def get_conversation_history(self) -> List[BaseMessage]:
        """Get the conversation history"""
        return self.memory.chat_memory.messages
    
    def clear_memory(self):
        """Clear the conversation memory"""
        self.memory.clear()
    
    def add_documents(self, documents):
        """Add new documents to the vector store"""
        self.vector_store_manager.add_documents(documents)
    
    def get_sources_used(self, result: Dict[str, Any]) -> List[str]:
        """Extract sources used in the response"""
        sources = []
        
        for step in result.get("intermediate_steps", []):
            if step[0].tool == "document_search":
                # Parse the document search results to extract sources
                output = step[1]
                if "Source:" in output:
                    lines = output.split("\n")
                    for line in lines:
                        if "Source:" in line:
                            source = line.split("Source:")[1].split(")")[0].strip()
                            if source not in sources:
                                sources.append(source)
        
        return sources
