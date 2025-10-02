# 🚀 Swagger UI & ReDoc Guide

## 📖 Overview
This guide explains how to access and use the comprehensive API documentation for the Agentic RAG API.

## 🌐 Access URLs

Once the API server is running, you can access the documentation at:

### 🔧 Swagger UI (Interactive Documentation)
```
http://localhost:8003/docs
```
- **Interactive API testing**
- **Try it out** functionality
- **Request/Response examples**
- **Schema validation**

### 📚 ReDoc (Alternative Documentation)
```
http://localhost:8003/redoc
```
- **Clean, professional layout**
- **Better for reading documentation**
- **Printable format**
- **Mobile-friendly**

### 📋 OpenAPI Schema (JSON)
```
http://localhost:8003/openapi.json
```
- **Machine-readable API specification**
- **For importing into other tools**
- **API client generation**

## 🚀 Getting Started

### 1. Start the API Server
```bash
cd /Users/ditthapong/Desktop/cofive-agentic-RAG
python3 api_server.py
```

### 2. Open Swagger UI
Open your browser and navigate to: `http://localhost:8003/docs`

### 3. Explore the API
- Browse different endpoint categories (Health, Documents, Agent, Query, System)
- Read detailed descriptions and examples
- Test endpoints directly in the browser

## 📚 API Categories

### 🏥 Health
- `GET /health` - Basic health check
- `GET /status` - Detailed system status

### 📄 Documents
- `POST /upload` - Upload documents (PDF, TXT, MD)

### 🤖 Agent
- `POST /initialize` - Initialize AI agent with model settings

### 💬 Query
- `POST /query` - Ask questions about uploaded documents

### ⚙️ System
- `POST /reset` - Reset entire system
- `GET /models` - Get available AI models

## 🧪 Testing Workflow in Swagger UI

### Step 1: Check System Health
1. Expand the **Health** section
2. Click on `GET /health`
3. Click **"Try it out"**
4. Click **"Execute"**
5. Verify you get a `200` response

### Step 2: Upload Documents
1. Expand the **Documents** section
2. Click on `POST /upload`
3. Click **"Try it out"**
4. Click **"Choose Files"** and select your documents
5. Click **"Execute"**
6. Verify successful upload response

### Step 3: Initialize Agent
1. Expand the **Agent** section
2. Click on `POST /initialize`
3. Click **"Try it out"**
4. Optionally modify model and temperature
5. Click **"Execute"**
6. Verify agent initialization

### Step 4: Query Documents
1. Expand the **Query** section
2. Click on `POST /query`
3. Click **"Try it out"**
4. Enter your question in the request body:
   ```json
   {
     "query": "What is the main topic of the documents?",
     "model": "gpt-4o-mini",
     "temperature": 0.1
   }
   ```
5. Click **"Execute"**
6. Review the AI-generated response

## 🎯 Swagger UI Features

### 📝 Interactive Testing
- **Try it out**: Test any endpoint directly
- **Parameters**: Fill in required and optional parameters
- **Request Body**: Edit JSON request bodies with validation
- **Response**: See actual API responses with status codes

### 📋 Documentation Features
- **Detailed Descriptions**: Comprehensive endpoint documentation
- **Examples**: Real-world usage examples
- **Schema Information**: Data model specifications
- **Error Codes**: Possible error responses

### 🔧 Advanced Features
- **Authorization**: API key configuration (if needed)
- **Servers**: Switch between different API environments
- **Download**: Export OpenAPI specification
- **Curl Commands**: Copy curl commands for terminal use

## 🛠️ Customization Options

### Model Configuration
```json
{
  "query": "Your question here",
  "model": "gpt-4o-mini",     // Choose from available models
  "temperature": 0.1          // 0.0 (focused) to 2.0 (creative)
}
```

### Available Models
- `gpt-3.5-turbo` - Fast and cost-effective
- `gpt-4` - High quality reasoning
- `gpt-4-turbo` - Enhanced performance
- `gpt-4o` - Optimized for various tasks
- `gpt-4o-mini` - Lightweight (recommended)
- `gpt-5-mini` - Next generation

### Temperature Guidelines
- **0.0-0.3**: Focused, deterministic responses
- **0.3-0.7**: Balanced creativity and consistency
- **0.7-1.0**: More creative responses
- **1.0-2.0**: Highly creative but potentially inconsistent

## 🔍 Example Queries

### Basic Information
```json
{
  "query": "What is the main topic of the uploaded documents?",
  "model": "gpt-4o-mini",
  "temperature": 0.1
}
```

### Summarization
```json
{
  "query": "Provide a comprehensive summary of all key points mentioned in the documents",
  "model": "gpt-4",
  "temperature": 0.3
}
```

### Specific Search
```json
{
  "query": "List all dates, numbers, or statistics mentioned in the documents",
  "model": "gpt-4o-mini",
  "temperature": 0.0
}
```

### Creative Analysis
```json
{
  "query": "What insights and recommendations can you derive from these documents?",
  "model": "gpt-4",
  "temperature": 0.7
}
```

## 🚨 Troubleshooting

### Common Issues

1. **API Server Not Running**
   - Error: "This site can't be reached"
   - Solution: Start the server with `python3 api_server.py`

2. **OpenAI API Key Missing**
   - Error: API key not configured
   - Solution: Set environment variable `export OPENAI_API_KEY=your_key_here`

3. **No Documents Error**
   - Error: "No documents available"
   - Solution: Upload documents first using `/upload` endpoint

4. **Agent Not Ready**
   - Error: "Agent not ready"
   - Solution: Initialize agent using `/initialize` endpoint

### Debug Steps
1. Check `/health` endpoint first
2. Verify `/status` shows correct configuration
3. Upload documents via `/upload`
4. Initialize agent via `/initialize`
5. Test with simple query via `/query`

## 🎉 Benefits of Using Swagger UI

### For Developers
- **API Discovery**: Explore all available endpoints
- **Testing**: Test API without writing code
- **Documentation**: Always up-to-date documentation
- **Integration**: Generate client code for various languages

### For Users
- **User-Friendly**: No programming knowledge required
- **Visual Interface**: Clean, intuitive design
- **Real-Time**: Test and see results immediately
- **Learning**: Understand API capabilities and limitations

## 📞 Support

If you encounter any issues:
1. Check the troubleshooting section above
2. Verify all prerequisites are met
3. Check the terminal for error messages
4. Ensure your OpenAI API key is valid and has credits

Happy API testing! 🚀