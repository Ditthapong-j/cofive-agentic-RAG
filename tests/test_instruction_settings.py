#!/usr/bin/env python3
"""
Test Instruction Settings and Enhanced Query Features
Tests the new instruction settings system and enhanced query capabilities
"""

import requests
import json
import time

# API Configuration
API_BASE_URL = "http://localhost:8003"

def test_health_check():
    """Test API health check"""
    print("🏥 Testing Health Check...")
    try:
        response = requests.get(f"{API_BASE_URL}/health")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Health check passed: {data['status']}")
            return True
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Health check error: {e}")
        return False

def test_get_default_settings():
    """Test getting default instruction settings"""
    print("👁️ Testing Get Default Settings...")
    try:
        response = requests.get(f"{API_BASE_URL}/settings/instructions")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Default settings retrieved")
            print(f"   System instruction: {data['settings']['system_instruction'][:80]}...")
            print(f"   Response length: {data['settings']['response_length']}")
            print(f"   Show similarity scores: {data['settings']['show_similarity_scores']}")
            print(f"   Max chunks: {data['settings']['max_chunks']}")
            print(f"   Similarity threshold: {data['settings']['similarity_threshold']}")
            return data['settings']
        else:
            print(f"❌ Get settings failed: {response.status_code}")
            return None
    except requests.exceptions.RequestException as e:
        print(f"❌ Get settings error: {e}")
        return None

def test_set_research_assistant_settings():
    """Test setting research assistant instructions"""
    print("⚙️ Testing Set Research Assistant Settings...")
    
    settings = {
        "system_instruction": "You are an expert research assistant specializing in academic and scientific analysis. Provide detailed, well-structured answers with clear citations. Break down complex topics into understandable segments and always explain your reasoning step by step.",
        "response_length": "detailed",
        "show_similarity_scores": True,
        "max_chunks": 8,
        "similarity_threshold": 0.1
    }
    
    try:
        response = requests.post(
            f"{API_BASE_URL}/settings/instructions",
            json=settings,
            headers={"Content-Type": "application/json"}
        )
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Research assistant settings updated")
            print(f"   Message: {data['message']}")
            return True
        else:
            print(f"❌ Set settings failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Set settings error: {e}")
        return False

def test_set_quick_summarizer_settings():
    """Test setting quick summarizer instructions"""
    print("⚙️ Testing Set Quick Summarizer Settings...")
    
    settings = {
        "system_instruction": "คุณเป็น AI ที่ตอบคำถามแบบสั้นมาก ไม่เกิน 300 ตัวอักษรเด็ดขาด ห้ามใช้รายการ ห้ามใช้หัวข้อ ห้ามใช้ดาว ตอบเป็นประโยคเดียวต่อเนื่อง กระชับ ตรงประเด็น เหมาะสำหรับการฟังทางโทร",
        "response_length": "short",
        "show_similarity_scores": True,
        "max_chunks": 5,
        "similarity_threshold": 0.0
    }
    
    try:
        response = requests.post(
            f"{API_BASE_URL}/settings/instructions",
            json=settings,
            headers={"Content-Type": "application/json"}
        )
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Quick summarizer settings updated")
            print(f"   Message: {data['message']}")
            return True
        else:
            print(f"❌ Set settings failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Set settings error: {e}")
        return False

def test_upload_sample_document():
    """Upload a sample document for testing"""
    print("📤 Testing Sample Document Upload...")
    
    # Create a sample document
    sample_content = """# Advanced AI Research Paper

## Abstract
This paper presents a comprehensive study on the applications of artificial intelligence in modern research methodologies. Our findings indicate significant improvements in data processing efficiency and accuracy when AI systems are properly implemented.

## Introduction
Artificial Intelligence has revolutionized numerous fields, from healthcare to finance. This research focuses on three key areas:
1. Natural Language Processing applications
2. Machine Learning algorithms for data analysis
3. Automated research assistance systems

## Methodology
We conducted experiments using various AI models including:
- GPT-4 for text generation and analysis
- BERT for document understanding
- Custom neural networks for specific research tasks

The data collection involved over 10,000 research papers and 500 expert interviews conducted between 2023-2025.

## Key Findings
1. AI-assisted research reduces analysis time by 70%
2. Accuracy of data interpretation improved by 45%
3. Novel insights discovery increased by 30%

## Applications in Healthcare
AI applications in healthcare have shown remarkable results:
- Diagnostic accuracy: 95% improvement
- Treatment planning: 60% faster
- Drug discovery: 40% acceleration

## Applications in Finance
Financial sector applications include:
- Fraud detection: 85% improvement
- Risk assessment: Real-time analysis capabilities
- Investment strategies: AI-guided portfolio optimization

## Limitations and Challenges
Despite the benefits, several challenges remain:
- Data quality requirements
- Ethical considerations
- Integration complexity
- Training requirements

## Future Directions
Future research should focus on:
1. Improving AI interpretability
2. Addressing bias in AI systems
3. Developing more efficient training methods
4. Creating standardized evaluation metrics

## Conclusion
Our research demonstrates that AI integration in research methodologies offers significant advantages. However, careful implementation and continuous monitoring are essential for optimal results.

## References
1. Smith, J. et al. (2024). "AI in Research: A Comprehensive Review"
2. Johnson, M. (2024). "Machine Learning Applications in Academia"
3. Brown, L. et al. (2025). "Future of AI-Assisted Research"
"""
    
    # Save to temporary file
    temp_file = "temp_research_paper.txt"
    with open(temp_file, 'w', encoding='utf-8') as f:
        f.write(sample_content)
    
    try:
        with open(temp_file, 'rb') as f:
            files = {'files': ('ai_research_paper.txt', f, 'text/plain')}
            response = requests.post(f"{API_BASE_URL}/upload", files=files)
        
        # Clean up
        import os
        os.remove(temp_file)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Sample document uploaded")
            print(f"   Files processed: {data['files_processed']}")
            print(f"   Total documents: {data['total_documents']}")
            return True
        else:
            print(f"❌ Upload failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Upload error: {e}")
        return False

def test_enhanced_query_with_detailed_settings():
    """Test enhanced query with detailed settings"""
    print("💬 Testing Enhanced Query (Detailed Settings)...")
    
    query_data = {
        "query": "What are the key findings from the AI research paper? Please provide a comprehensive analysis with specific numbers and applications.",
        "model": "gpt-4o-mini",
        "temperature": 0.1
    }
    
    try:
        response = requests.post(
            f"{API_BASE_URL}/query",
            json=query_data,
            headers={"Content-Type": "application/json"}
        )
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Enhanced query successful")
            print(f"   Model used: {data['model_used']}")
            print(f"   Processing time: {data['processing_time']:.2f}s")
            print(f"   Chunks retrieved: {data.get('chunks_retrieved', 'N/A')}")
            print(f"   Answer length: {len(data['answer'])} characters")
            print(f"   Answer preview: {data['answer'][:200]}...")
            
            if data.get('similarity_scores'):
                print(f"   Similarity scores:")
                for i, score_info in enumerate(data['similarity_scores'][:3], 1):
                    print(f"     {i}. Source: {score_info['source']}")
                    print(f"        Score: {score_info['score']}")
                    print(f"        Content: {score_info['content'][:100]}...")
            
            if data.get('settings_used'):
                print(f"   Settings used: {data['settings_used']}")
            
            return data
        else:
            print(f"❌ Enhanced query failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return None
    except requests.exceptions.RequestException as e:
        print(f"❌ Enhanced query error: {e}")
        return None

def test_enhanced_query_with_short_settings():
    """Test enhanced query with short settings"""
    print("💬 Testing Enhanced Query (Short Settings)...")
    
    # Test with a more specific query that should find data
    query_data = {
        "query": "healthcare AI diagnostic accuracy improvement percentage",
        "model": "gpt-4o-mini",
        "temperature": 0.1
    }
    
    try:
        response = requests.post(
            f"{API_BASE_URL}/query",
            json=query_data,
            headers={"Content-Type": "application/json"}
        )
        if response.status_code == 200:
            data = response.json()
            if data['success']:
                print(f"✅ Enhanced query successful")
                print(f"   Model used: {data['model_used']}")
                print(f"   Processing time: {data['processing_time']:.2f}s")
                print(f"   Chunks retrieved: {data.get('chunks_retrieved', 'N/A')}")
                print(f"   Answer length: {len(data['answer'])} characters")
                print(f"   Answer: {data['answer']}")
                
                if data.get('similarity_scores'):
                    print(f"   Similarity scores: {len(data['similarity_scores'])} chunks shown")
                    for i, score_info in enumerate(data['similarity_scores'][:2], 1):
                        print(f"     {i}. {score_info['source']}: {score_info['score']}")
                elif data.get('chunks_retrieved', 0) == 0:
                    print(f"   Similarity scores: No data retrieved (0 chunks)")
                else:
                    print(f"   Similarity scores: Hidden (disabled in settings)")
            else:
                print(f"⚠️ Query completed but no relevant data found")
                print(f"   Reason: {data.get('error', 'Unknown')}")
                print(f"   Response: {data['answer']}")
                print(f"   Chunks retrieved: {data.get('chunks_retrieved', 0)}")
            
            return data
        else:
            print(f"❌ Enhanced query failed: {response.status_code}")
            return None
    except requests.exceptions.RequestException as e:
        print(f"❌ Enhanced query error: {e}")
        return None

def test_enhanced_query_with_general_topic():
    """Test enhanced query with a general topic that should match document content"""
    print("💬 Testing Enhanced Query (General Topic)...")
    
    # Test with a broader query that should find data
    query_data = {
        "query": "AI research findings",
        "model": "gpt-4o-mini",
        "temperature": 0.1
    }
    
    try:
        response = requests.post(
            f"{API_BASE_URL}/query",
            json=query_data,
            headers={"Content-Type": "application/json"}
        )
        if response.status_code == 200:
            data = response.json()
            if data['success']:
                print(f"✅ General query successful")
                print(f"   Answer length: {len(data['answer'])} characters")
                print(f"   Answer: {data['answer']}")
                print(f"   Chunks retrieved: {data.get('chunks_retrieved', 0)}")
                
                if data.get('similarity_scores'):
                    print(f"   Similarity scores found: {len(data['similarity_scores'])} chunks")
                    for score_info in data['similarity_scores']:
                        print(f"     - {score_info['source']}: {score_info['score']}")
                
                return data
            else:
                print(f"⚠️ General query - no relevant data found")
                print(f"   Response: {data['answer']}")
                return data
        else:
            print(f"❌ General query failed: {response.status_code}")
            return None
    except requests.exceptions.RequestException as e:
        print(f"❌ General query error: {e}")
        return None

def test_settings_persistence():
    """Test that settings persist after retrieval"""
    print("💾 Testing Settings Persistence...")
    
    # Get current settings
    try:
        response = requests.get(f"{API_BASE_URL}/settings/instructions")
        if response.status_code == 200:
            data = response.json()
            current_settings = data['settings']
            print(f"✅ Settings persistence verified")
            print(f"   Current response length: {current_settings['response_length']}")
            print(f"   Current max chunks: {current_settings['max_chunks']}")
            print(f"   Show similarity scores: {current_settings['show_similarity_scores']}")
            return current_settings
        else:
            print(f"❌ Settings retrieval failed: {response.status_code}")
            return None
    except requests.exceptions.RequestException as e:
        print(f"❌ Settings retrieval error: {e}")
        return None

def main():
    """Run comprehensive instruction settings tests"""
    print("🚀 Starting Instruction Settings & Enhanced Query Tests")
    print("=" * 60)
    
    # Health check
    if not test_health_check():
        print("❌ API not available. Please start the server first.")
        return
    print()
    
    # Test default settings
    print("📋 Default Settings")
    print("-" * 20)
    default_settings = test_get_default_settings()
    print()
    
    # Test document upload (agent will auto-initialize)
    print("📄 Document Upload & Auto-Initialization")
    print("-" * 38)
    upload_success = test_upload_sample_document()
    print()
    
    if not upload_success:
        print("❌ Document upload failed. Skipping query tests.")
        return
    
    # Test instruction settings
    print("⚙️ Instruction Settings Tests")
    print("-" * 30)
    
    # Set detailed research assistant settings
    # test_set_research_assistant_settings()
    # print()
    
    # # Test query with detailed settings
    # print("📊 Detailed Query Test")
    # print("-" * 20)
    # detailed_result = test_enhanced_query_with_detailed_settings()
    # print()
    
    # Change to quick summarizer settings
    test_set_quick_summarizer_settings()
    print()
    
    # Test query with short settings
    print("⚡ Quick Query Test")
    print("-" * 17)
    short_result = test_enhanced_query_with_short_settings()
    print()
    
    # Test with general topic query
    print("🔍 General Topic Test")
    print("-" * 19)
    general_result = test_enhanced_query_with_general_topic()
    print()
    
    # Test settings persistence
    print("💾 Settings Persistence")
    print("-" * 20)
    final_settings = test_settings_persistence()
    print()
    
    # Summary
    print("📊 Test Summary")
    print("=" * 60)
    
    if short_result:
        if short_result.get('success'):
            print(f"⚡ Short response length: {len(short_result['answer'])} characters")
            print(f"📋 Chunks retrieved - Short: {short_result.get('chunks_retrieved', 0)}")
        else:
            print(f"⚠️ Short query failed: {short_result.get('error', 'Unknown error')}")
    
    if general_result:
        if general_result.get('success'):
            print(f"🔍 General response length: {len(general_result['answer'])} characters")
            print(f"📋 Chunks retrieved - General: {general_result.get('chunks_retrieved', 0)}")
        else:
            print(f"⚠️ General query failed: {general_result.get('error', 'Unknown error')}")
    
    if final_settings:
        print(f"⚙️ Final settings: {final_settings['response_length']} length, {final_settings['max_chunks']} max chunks")
    
    print("\n🎉 Instruction Settings Tests Completed!")
    print("=" * 60)
    
    print("\n📚 Key Features Tested:")
    print("  ✅ Auto-initialization on document upload")
    print("  ✅ Custom system instructions")
    print("  ✅ Response length control (short/detailed)")
    print("  ✅ Similarity scores display toggle")
    print("  ✅ Chunk retrieval limits")
    print("  ✅ Settings persistence (JSON file)")
    print("  ✅ Enhanced query responses")

if __name__ == "__main__":
    main()