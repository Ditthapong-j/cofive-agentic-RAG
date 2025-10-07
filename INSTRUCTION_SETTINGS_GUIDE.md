# 🎯 Instruction Settings & Enhanced Query Guide

## 🌟 Overview
This guide explains the advanced instruction settings system that allows you to customize AI behavior, control response length, and view similarity scores for enhanced document querying.

## 🎛️ Features

### ⚙️ **System Instructions**
Configure how the AI should behave and respond to queries.

**影响范围:**
- Response tone and style
- Level of detail and explanation
- How sources are cited
- Overall AI personality

### 📏 **Response Length Control**
Control the length and detail level of AI responses.

**Options:**
- **short**: Concise, 1-2 paragraphs maximum
- **medium**: Balanced response, 2-4 paragraphs
- **long**: Comprehensive response, 4-6 paragraphs  
- **detailed**: Exhaustive analysis with all relevant information

### 📊 **Similarity Scores**
Display how closely retrieved document chunks match your query.

**Benefits:**
- Understand retrieval quality
- Debug search effectiveness
- Verify source relevance
- Optimize query formulation

### 🎯 **Chunk Control**
Fine-tune document retrieval parameters.

**Settings:**
- **max_chunks**: Maximum document chunks to retrieve (1-20)
- **similarity_threshold**: Minimum similarity score (0.0-1.0)

## 🚀 API Endpoints

### 📝 Set Instructions
Configure AI behavior and response settings.

**Endpoint:** `POST /settings/instructions`

**Request Body:**
```json
{
  "system_instruction": "You are an expert research assistant. Provide detailed, accurate answers based on the documents. Always cite sources and explain your reasoning step by step.",
  "response_length": "detailed",
  "show_similarity_scores": true,
  "max_chunks": 8,
  "similarity_threshold": 0.1
}
```

**Example - Research Assistant:**
```bash
curl -X POST "http://localhost:8003/settings/instructions" \
  -H "Content-Type: application/json" \
  -d '{
    "system_instruction": "You are an expert research assistant specializing in academic analysis. Provide detailed, well-structured answers with clear citations.",
    "response_length": "detailed",
    "show_similarity_scores": true,
    "max_chunks": 8,
    "similarity_threshold": 0.1
  }'
```

**Example - Quick Summarizer:**
```bash
curl -X POST "http://localhost:8003/settings/instructions" \
  -H "Content-Type: application/json" \
  -d '{
    "system_instruction": "You are a concise summarizer. Provide brief, to-the-point answers based on the documents.",
    "response_length": "short",
    "show_similarity_scores": false,
    "max_chunks": 3,
    "similarity_threshold": 0.3
  }'
```

### 👁️ View Instructions
Get current AI behavior and similarity settings.

**Endpoint:** `GET /settings/instructions`

**Example:**
```bash
curl -X GET "http://localhost:8003/settings/instructions"
```

**Response:**
```json
{
  "success": true,
  "message": "Current settings retrieved successfully",
  "settings": {
    "system_instruction": "You are a helpful AI assistant...",
    "response_length": "medium",
    "show_similarity_scores": true,
    "max_chunks": 5,
    "similarity_threshold": 0.0
  }
}
```

### 💬 Enhanced Query
Query documents with similarity scores and custom instructions.

**Endpoint:** `POST /query`

**Enhanced Response:**
```json
{
  "success": true,
  "answer": "Based on the uploaded documents, the main findings include...",
  "sources": ["document1.pdf", "research_notes.txt"],
  "similarity_scores": [
    {
      "source": "document1.pdf",
      "content": "This section discusses the main findings...",
      "score": 0.89
    },
    {
      "source": "research_notes.txt", 
      "content": "Additional research shows...",
      "score": 0.76
    }
  ],
  "model_used": "gpt-4o-mini",
  "processing_time": 2.34,
  "chunks_retrieved": 5,
  "settings_used": {
    "response_length": "detailed",
    "max_chunks": 8,
    "similarity_threshold": 0.1,
    "show_similarity_scores": true
  },
  "error": null
}
```

## 🔄 Complete Workflow

### 1. **Check Current Settings**
```bash
curl -X GET "http://localhost:8003/settings/instructions"
```

### 2. **Upload Documents**
```bash
curl -X POST "http://localhost:8003/upload" \
  -F "files=@research_paper.pdf"
```

### 3. **Configure AI Behavior**
```bash
curl -X POST "http://localhost:8003/settings/instructions" \
  -H "Content-Type: application/json" \
  -d '{
    "system_instruction": "You are an expert analyst. Provide comprehensive insights with clear evidence.",
    "response_length": "detailed",
    "show_similarity_scores": true,
    "max_chunks": 10,
    "similarity_threshold": 0.0
  }'
```

### 4. **Initialize Agent**
```bash
curl -X POST "http://localhost:8003/initialize?model=gpt-4o-mini&temperature=0.1"
```

### 5. **Query with Enhanced Features**
```bash
curl -X POST "http://localhost:8003/query" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What are the key findings and their implications?",
    "model": "gpt-4o-mini",
    "temperature": 0.1
  }'
```

## 🎯 Use Cases & Examples

### 📚 **Academic Research**
```json
{
  "system_instruction": "You are an academic research assistant. Provide scholarly analysis with proper citations, methodology explanations, and critical evaluation of sources.",
  "response_length": "detailed",
  "show_similarity_scores": true,
  "max_chunks": 10,
  "similarity_threshold": 0.05
}
```

### 💼 **Business Analysis**
```json
{
  "system_instruction": "You are a business analyst. Focus on actionable insights, key metrics, and strategic implications. Present findings in a clear, executive-friendly format.",
  "response_length": "long",
  "show_similarity_scores": true,
  "max_chunks": 8,
  "similarity_threshold": 0.1
}
```

### ⚡ **Quick Q&A**
```json
{
  "system_instruction": "You are a quick reference assistant. Provide direct, concise answers to specific questions without unnecessary elaboration.",
  "response_length": "short",
  "show_similarity_scores": false,
  "max_chunks": 3,
  "similarity_threshold": 0.2
}
```

### 🎓 **Educational Content**
```json
{
  "system_instruction": "You are an educational assistant. Break down complex concepts into understandable parts, provide examples, and explain step-by-step reasoning.",
  "response_length": "long",
  "show_similarity_scores": true,
  "max_chunks": 7,
  "similarity_threshold": 0.1
}
```

## 📊 Similarity Scores Explained

### 🔍 **Score Interpretation**
- **0.9-1.0**: Extremely relevant, near-perfect match
- **0.7-0.8**: Highly relevant, strong semantic similarity
- **0.5-0.6**: Moderately relevant, some useful information
- **0.3-0.4**: Somewhat relevant, tangential information
- **0.0-0.2**: Low relevance, minimal connection

### 📈 **Using Scores Effectively**
1. **High Threshold (0.3-0.5)**: For precise, focused answers
2. **Medium Threshold (0.1-0.2)**: For comprehensive coverage
3. **Low Threshold (0.0)**: For maximum information gathering

### 🔧 **Optimization Tips**
- **Low scores across all chunks**: Refine your query
- **Few chunks retrieved**: Lower similarity threshold
- **Too many irrelevant chunks**: Raise similarity threshold
- **Missing information**: Increase max_chunks

## 💾 Settings Persistence

### 📁 **JSON File Storage**
Settings are automatically saved to `instruction_settings.json`:

```json
{
  "system_instruction": "You are an expert research assistant...",
  "response_length": "detailed",
  "show_similarity_scores": true,
  "max_chunks": 8,
  "similarity_threshold": 0.1
}
```

### 🔄 **Automatic Loading**
- Settings persist across server restarts
- Loaded automatically when system initializes
- Applied to all queries until changed
- Default values used if no custom configuration exists

## 🧪 Testing

### **Run Test Suite**
```bash
cd /Users/ditthapong/Desktop/cofive-agentic-RAG
python3 tests/test_instruction_settings.py
```

### **Interactive Testing via Swagger UI**
1. Start API server: `python3 api_server.py`
2. Open Swagger UI: `http://localhost:8003/docs`
3. Navigate to "System" section
4. Test `/settings/instructions` endpoints

## ⚡ Performance Considerations

### 🚀 **Response Time Factors**
- **Detailed responses**: Longer processing time
- **More chunks**: Increased retrieval time
- **Lower threshold**: More chunks to process
- **Complex instructions**: More AI processing

### 💡 **Optimization Strategies**
- Use appropriate response length for your needs
- Set reasonable chunk limits (5-10 for most cases)
- Use higher thresholds for faster, focused responses
- Cache settings to avoid repeated configuration

## 🔮 Advanced Features

### 🎯 **Dynamic Instruction Adjustment**
- Modify instructions based on query type
- Adjust similarity thresholds for different domains
- Change response length for different audiences

### 📊 **Response Quality Monitoring**
- Track similarity scores over time
- Monitor chunk retrieval patterns
- Analyze response length effectiveness

### 🔧 **Custom Instruction Templates**
Create reusable instruction templates for different scenarios:

```python
TEMPLATES = {
    "research": {
        "system_instruction": "Research assistant with academic focus...",
        "response_length": "detailed",
        "show_similarity_scores": True,
        "max_chunks": 10,
        "similarity_threshold": 0.05
    },
    "business": {
        "system_instruction": "Business analyst with strategic focus...",
        "response_length": "long", 
        "show_similarity_scores": True,
        "max_chunks": 8,
        "similarity_threshold": 0.1
    }
}
```

## 🎉 Benefits Summary

### ✨ **Enhanced Control**
- **Custom AI Personality**: Tailor responses to your domain
- **Response Length Management**: Get exactly the detail level you need
- **Quality Insights**: See how well documents match your queries
- **Retrieval Optimization**: Fine-tune document search parameters

### 🎯 **Improved Accuracy**
- **Better Relevance**: Filter documents by similarity
- **Focused Responses**: Control information scope
- **Source Transparency**: See exactly what documents contribute
- **Configurable Precision**: Adjust retrieval sensitivity

### 📈 **Better User Experience**
- **Consistent Behavior**: Settings persist across sessions
- **Predictable Responses**: Control output format and length
- **Debugging Support**: Similarity scores help optimize queries
- **Flexible Configuration**: Easy to adjust for different use cases

This comprehensive instruction settings system gives you complete control over how the AI processes and responds to your document queries, making it a powerful tool for various professional and research applications!