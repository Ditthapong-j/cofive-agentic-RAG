"""
Advanced Prompt Management System for Agentic RAG
"""
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum
import json
import os
from pathlib import Path


class ResponseStyle(Enum):
    BALANCED = "balanced"
    TECHNICAL = "technical"
    CASUAL = "casual"
    ACADEMIC = "academic"
    CONCISE = "concise"
    DETAILED = "detailed"


class OutputLanguage(Enum):
    AUTO = "auto"
    THAI = "thai"
    ENGLISH = "english"
    MIXED = "mixed"


class ResponseLength(Enum):
    SHORT = "short"
    MEDIUM = "medium"
    LONG = "long"
    COMPREHENSIVE = "comprehensive"


@dataclass
class PromptTemplate:
    """Structure for prompt templates"""
    name: str
    description: str
    system_prompt: str
    style_instructions: Dict[str, str]
    language_instructions: Dict[str, str]
    length_instructions: Dict[str, str]
    tags: List[str]
    examples: List[Dict[str, str]]


class PromptManager:
    """Advanced prompt management system"""
    
    def __init__(self, templates_dir: Optional[str] = None):
        self.templates_dir = templates_dir or "./prompt_templates"
        self.templates: Dict[str, PromptTemplate] = {}
        self.load_default_templates()
        self.load_custom_templates()
    
    def load_default_templates(self):
        """Load default prompt templates"""
        
        # Default RAG template
        default_rag = PromptTemplate(
            name="default_rag",
            description="Standard RAG system prompt",
            system_prompt="""You are an intelligent AI assistant with access to a knowledge base containing documents in Thai and English. 

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
- If multiple relevant documents are found, combine the information intelligently""",
            style_instructions={
                "balanced": "Provide balanced, clear responses with practical information.",
                "technical": "Use technical terminology and provide detailed technical explanations with code examples when relevant.",
                "casual": "Use conversational tone and simple language. Make it easy to understand.",
                "academic": "Provide scholarly, well-researched responses with proper citations and formal language.",
                "concise": "Be brief and to the point. Provide only essential information.",
                "detailed": "Provide comprehensive, thorough explanations with examples and context."
            },
            language_instructions={
                "auto": "Respond in the same language as the question, or Thai if uncertain.",
                "thai": "Always respond in Thai language.",
                "english": "Always respond in English language.",
                "mixed": "Use both Thai and English as appropriate for technical terms."
            },
            length_instructions={
                "short": "Keep responses under 100 words. Be concise.",
                "medium": "Provide moderate-length responses (100-300 words).",
                "long": "Provide detailed responses (300-500 words).",
                "comprehensive": "Provide thorough, comprehensive responses (500+ words) with examples."
            },
            tags=["rag", "default", "general"],
            examples=[
                {
                    "query": "What is Python?",
                    "response": "According to the documents, Python is a high-level programming language..."
                }
            ]
        )
        
        # Teacher template
        teacher_template = PromptTemplate(
            name="teacher",
            description="Educational assistant that explains concepts step-by-step",
            system_prompt="""You are a patient and knowledgeable teacher. Your goal is to help students understand concepts clearly.

TEACHING APPROACH:
1. Search for relevant information in the knowledge base
2. Break down complex concepts into simple parts
3. Use analogies and real-world examples
4. Provide step-by-step explanations
5. Check for understanding and provide practice opportunities

TEACHING STYLE:
- Start with basic concepts before advanced ones
- Use simple language and explain technical terms
- Provide examples and analogies
- Encourage questions and exploration
- Be supportive and encouraging""",
            style_instructions={
                "beginner": "Use very simple language, lots of examples, and basic concepts only.",
                "intermediate": "Include some technical terms with explanations and practical examples.",
                "advanced": "Use technical language but still provide clear explanations and complex examples."
            },
            language_instructions={
                "auto": "Use the student's preferred language for maximum understanding.",
                "thai": "Explain in Thai with Thai examples and cultural context.",
                "english": "Use clear English with international examples.",
                "mixed": "Use both languages to explain technical terms clearly."
            },
            length_instructions={
                "brief": "Give quick, focused explanations (50-100 words).",
                "standard": "Provide thorough explanations with examples (200-400 words).",
                "comprehensive": "Give detailed lessons with multiple examples and practice (500+ words)."
            },
            tags=["education", "teaching", "learning"],
            examples=[
                {
                    "query": "How does a function work in Python?",
                    "response": "Think of a function like a recipe. Just like a recipe takes ingredients and produces a dish, a function takes inputs and produces outputs..."
                }
            ]
        )
        
        # Business consultant template
        business_template = PromptTemplate(
            name="business_consultant",
            description="Business-focused responses with practical applications",
            system_prompt="""You are a business consultant providing practical, actionable advice based on the knowledge base.

BUSINESS APPROACH:
1. Search for relevant business information
2. Focus on practical applications and ROI
3. Provide actionable recommendations
4. Consider business constraints and resources
5. Emphasize measurable outcomes

BUSINESS FOCUS:
- Cost-effectiveness and ROI
- Implementation feasibility
- Risk assessment
- Scalability considerations
- Competitive advantages""",
            style_instructions={
                "executive": "High-level strategic insights for decision makers.",
                "operational": "Detailed implementation guidance for managers.",
                "tactical": "Specific action items and immediate steps."
            },
            language_instructions={
                "auto": "Use business-appropriate language for the context.",
                "thai": "Use Thai business terminology and local market context.",
                "english": "Use international business language and global examples.",
                "mixed": "Combine both languages for technical business terms."
            },
            length_instructions={
                "summary": "Brief executive summary (100-150 words).",
                "proposal": "Detailed business proposal (300-500 words).",
                "comprehensive": "Full business analysis with recommendations (500+ words)."
            },
            tags=["business", "consulting", "strategy"],
            examples=[
                {
                    "query": "How to implement Python in our business?",
                    "response": "Based on the technical documentation, implementing Python in your business can provide significant ROI through automation..."
                }
            ]
        )
        
        self.templates["default_rag"] = default_rag
        self.templates["teacher"] = teacher_template
        self.templates["business_consultant"] = business_template
    
    def load_custom_templates(self):
        """Load custom templates from files"""
        templates_path = Path(self.templates_dir)
        if templates_path.exists():
            for template_file in templates_path.glob("*.json"):
                try:
                    with open(template_file, 'r', encoding='utf-8') as f:
                        template_data = json.load(f)
                        template = PromptTemplate(**template_data)
                        self.templates[template.name] = template
                except Exception as e:
                    print(f"Error loading template {template_file}: {e}")
    
    def save_template(self, template: PromptTemplate):
        """Save a custom template to file"""
        templates_path = Path(self.templates_dir)
        templates_path.mkdir(exist_ok=True)
        
        template_file = templates_path / f"{template.name}.json"
        template_dict = {
            "name": template.name,
            "description": template.description,
            "system_prompt": template.system_prompt,
            "style_instructions": template.style_instructions,
            "language_instructions": template.language_instructions,
            "length_instructions": template.length_instructions,
            "tags": template.tags,
            "examples": template.examples
        }
        
        with open(template_file, 'w', encoding='utf-8') as f:
            json.dump(template_dict, f, indent=2, ensure_ascii=False)
        
        self.templates[template.name] = template
    
    def get_template(self, name: str) -> Optional[PromptTemplate]:
        """Get a template by name"""
        return self.templates.get(name)
    
    def list_templates(self) -> List[str]:
        """List all available template names"""
        return list(self.templates.keys())
    
    def search_templates(self, tags: List[str]) -> List[PromptTemplate]:
        """Search templates by tags"""
        matching_templates = []
        for template in self.templates.values():
            if any(tag in template.tags for tag in tags):
                matching_templates.append(template)
        return matching_templates
    
    def create_enhanced_prompt(
        self,
        template_name: str,
        style: str = "balanced",
        language: str = "auto",
        length: str = "medium",
        custom_instructions: str = "",
        enhancement_options: Optional[Dict[str, Any]] = None
    ) -> str:
        """Create an enhanced prompt with all customizations"""
        
        template = self.get_template(template_name)
        if not template:
            raise ValueError(f"Template '{template_name}' not found")
        
        # Start with base prompt
        enhanced_prompt = template.system_prompt
        
        # Add style instructions
        if style in template.style_instructions:
            enhanced_prompt += f"\n\nSTYLE: {template.style_instructions[style]}"
        
        # Add language instructions
        if language in template.language_instructions:
            enhanced_prompt += f"\nLANGUAGE: {template.language_instructions[language]}"
        
        # Add length instructions
        if length in template.length_instructions:
            enhanced_prompt += f"\nLENGTH: {template.length_instructions[length]}"
        
        # Add custom instructions
        if custom_instructions:
            enhanced_prompt += f"\nCUSTOM INSTRUCTIONS: {custom_instructions}"
        
        # Add enhancement options
        if enhancement_options:
            enhanced_prompt += "\n\nENHANCEMENT OPTIONS:"
            
            if enhancement_options.get("include_examples", False):
                enhanced_prompt += "\n- Always provide practical examples"
            
            if enhancement_options.get("include_citations", False):
                enhanced_prompt += "\n- Include source citations and references"
            
            if enhancement_options.get("step_by_step", False):
                enhanced_prompt += "\n- Break down explanations into step-by-step format"
            
            if enhancement_options.get("include_confidence", False):
                enhanced_prompt += "\n- Include confidence scores for your answers"
            
            # Tone adjustments
            formality = enhancement_options.get("formality", 5)
            enthusiasm = enhancement_options.get("enthusiasm", 5)
            
            if formality <= 3:
                enhanced_prompt += "\n- Use casual, informal tone"
            elif formality >= 7:
                enhanced_prompt += "\n- Use formal, professional tone"
            
            if enthusiasm >= 7:
                enhanced_prompt += "\n- Be enthusiastic and engaging"
            elif enthusiasm <= 3:
                enhanced_prompt += "\n- Be neutral and matter-of-fact"
            
            # Content focus
            focus_areas = enhancement_options.get("content_focus", [])
            if focus_areas:
                enhanced_prompt += f"\n- Focus on: {', '.join(focus_areas)}"
            
            exclude_areas = enhancement_options.get("exclude_content", [])
            if exclude_areas:
                enhanced_prompt += f"\n- Avoid: {', '.join(exclude_areas)}"
        
        return enhanced_prompt
    
    def create_query_with_prompt(
        self,
        user_query: str,
        template_name: str = "default_rag",
        **prompt_options
    ) -> str:
        """Create a query with embedded prompt instructions"""
        
        # Get the enhanced prompt
        enhanced_prompt = self.create_enhanced_prompt(template_name, **prompt_options)
        
        # Create query with prompt instructions
        query_with_prompt = f"""
{user_query}

SYSTEM INSTRUCTIONS FOR THIS QUERY:
{enhanced_prompt}
"""
        return query_with_prompt


def get_prompt_manager() -> PromptManager:
    """Get or create prompt manager instance"""
    if not hasattr(get_prompt_manager, "_instance"):
        get_prompt_manager._instance = PromptManager()
    return get_prompt_manager._instance
