"""
Example script demonstrating tags and metadata filtering in Agentic RAG
"""
import requests
import json
import time

# Configuration
BASE_URL = "http://localhost:8003"

def print_section(title):
    """Print a formatted section header"""
    print("\n" + "="*60)
    print(f"  {title}")
    print("="*60 + "\n")

def upload_test_documents():
    """Upload test documents with different tags and metadata"""
    print_section("1. UPLOADING TEST DOCUMENTS")
    
    url = f"{BASE_URL}/upload"
    
    # Test document 1: AI Research Paper
    doc1_content = """
    Artificial Intelligence Research Paper
    Title: Advanced Neural Networks in Computer Vision
    Author: Dr. John Smith
    
    This paper presents novel approaches to computer vision using deep learning.
    Our research demonstrates significant improvements in image classification.
    The neural network architecture achieves 95% accuracy on standard benchmarks.
    """
    
    files1 = [('files', ('ai_research_2024.txt', doc1_content, 'text/plain'))]
    params1 = {
        'tags': 'research,AI,computer-vision,deep-learning',
        'metadata': json.dumps({
            'author': 'Dr. John Smith',
            'year': 2024,
            'department': 'R&D',
            'field': 'Computer Vision',
            'citations': 150,
            'priority': 'high'
        })
    }
    
    print("📤 Uploading AI Research Paper...")
    response1 = requests.post(url, files=files1, params=params1)
    print(f"✅ Response: {response1.json()}\n")
    
    # Test document 2: Business Report
    doc2_content = """
    Marketing Department Quarterly Report Q4 2024
    Prepared by: Jane Doe
    
    This quarter showed exceptional growth in digital marketing campaigns.
    Social media engagement increased by 45% compared to Q3.
    Our AI-powered recommendation system contributed to 30% revenue increase.
    Total marketing ROI: 320%
    """
    
    files2 = [('files', ('marketing_q4_2024.txt', doc2_content, 'text/plain'))]
    params2 = {
        'tags': 'business,marketing,quarterly-report',
        'metadata': json.dumps({
            'author': 'Jane Doe',
            'year': 2024,
            'quarter': 'Q4',
            'department': 'Marketing',
            'document_type': 'report',
            'status': 'approved'
        })
    }
    
    print("📤 Uploading Business Report...")
    response2 = requests.post(url, files=files2, params=params2)
    print(f"✅ Response: {response2.json()}\n")
    
    # Test document 3: Technical Documentation
    doc3_content = """
    AI Assistant Development Documentation
    Technical Specification v2.0
    Team: Backend Development
    
    The AI Assistant project uses advanced NLP techniques for natural language understanding.
    System architecture includes microservices for scalability.
    Current implementation supports multiple languages including Thai and English.
    Performance: 99.9% uptime, <100ms response time
    """
    
    files3 = [('files', ('tech_doc_backend.txt', doc3_content, 'text/plain'))]
    params3 = {
        'tags': 'technical,documentation,NLP,backend',
        'metadata': json.dumps({
            'project': 'AI-Assistant-2024',
            'team': 'Backend',
            'version': '2.0',
            'phase': 'development',
            'language': 'English',
            'priority': 'high'
        })
    }
    
    print("📤 Uploading Technical Documentation...")
    response3 = requests.post(url, files=files3, params=params3)
    print(f"✅ Response: {response3.json()}\n")
    
    time.sleep(2)  # Wait for processing

def list_all_documents():
    """List all uploaded documents"""
    print_section("2. LISTING ALL DOCUMENTS")
    
    url = f"{BASE_URL}/documents"
    response = requests.get(url)
    data = response.json()
    
    print(f"📚 Total Documents: {data['total_count']}\n")
    
    for doc in data['documents']:
        print(f"📄 Document ID: {doc['id']}")
        print(f"   Filename: {doc['filename']}")
        print(f"   Tags: {doc.get('tags', [])}")
        print(f"   Metadata: {doc.get('metadata', {})}")
        print(f"   Chunks: {doc['chunk_count']}")
        print()

def query_without_filters():
    """Query without any filters"""
    print_section("3. QUERY WITHOUT FILTERS")
    
    url = f"{BASE_URL}/query"
    data = {
        "query": "What documents do we have about AI?",
        "model": "gpt-4o-mini",
        "temperature": 0.1
    }
    
    print("❓ Query: What documents do we have about AI?")
    print("🔍 Filters: None\n")
    
    response = requests.post(url, json=data)
    result = response.json()
    
    print(f"✅ Success: {result['success']}")
    print(f"📝 Answer: {result['answer']}\n")
    print(f"📊 Chunks Retrieved: {result['chunks_retrieved']}")
    
    if result.get('similarity_scores'):
        print("\n🎯 Similarity Scores:")
        for score in result['similarity_scores']:
            print(f"  - Source: {score['source']}")
            print(f"    Score: {score['score']}")
            print(f"    Tags: {score.get('tags', [])}")
            print(f"    Metadata: {score.get('metadata', {})}")
            print()

def query_with_tags():
    """Query with tag filtering"""
    print_section("4. QUERY WITH TAG FILTERING")
    
    url = f"{BASE_URL}/query"
    data = {
        "query": "What are the main findings in research documents?",
        "model": "gpt-4o-mini",
        "temperature": 0.1,
        "tags": ["research", "AI"]
    }
    
    print("❓ Query: What are the main findings in research documents?")
    print("🏷️  Tags Filter: ['research', 'AI']\n")
    
    response = requests.post(url, json=data)
    result = response.json()
    
    print(f"✅ Success: {result['success']}")
    print(f"📝 Answer: {result['answer']}\n")
    print(f"📊 Chunks Retrieved: {result['chunks_retrieved']}")
    
    if result.get('similarity_scores'):
        print("\n🎯 Similarity Scores:")
        for score in result['similarity_scores']:
            print(f"  - Source: {score['source']}")
            print(f"    Score: {score['score']}")
            print(f"    Tags: {score.get('tags', [])}")
            print()

def query_with_metadata():
    """Query with metadata filtering"""
    print_section("5. QUERY WITH METADATA FILTERING")
    
    url = f"{BASE_URL}/query"
    data = {
        "query": "What are the marketing results?",
        "model": "gpt-4o-mini",
        "temperature": 0.1,
        "metadata_filter": {
            "department": "Marketing",
            "year": 2024
        }
    }
    
    print("❓ Query: What are the marketing results?")
    print("📋 Metadata Filter: {'department': 'Marketing', 'year': 2024}\n")
    
    response = requests.post(url, json=data)
    result = response.json()
    
    print(f"✅ Success: {result['success']}")
    print(f"📝 Answer: {result['answer']}\n")
    print(f"📊 Chunks Retrieved: {result['chunks_retrieved']}")
    
    if result.get('similarity_scores'):
        print("\n🎯 Similarity Scores:")
        for score in result['similarity_scores']:
            print(f"  - Source: {score['source']}")
            print(f"    Score: {score['score']}")
            print(f"    Metadata: {score.get('metadata', {})}")
            print()

def query_with_both_filters():
    """Query with both tag and metadata filtering"""
    print_section("6. QUERY WITH COMBINED FILTERS")
    
    url = f"{BASE_URL}/query"
    data = {
        "query": "What is the current status of technical projects?",
        "model": "gpt-4o-mini",
        "temperature": 0.1,
        "tags": ["technical"],
        "metadata_filter": {
            "priority": "high",
            "phase": "development"
        }
    }
    
    print("❓ Query: What is the current status of technical projects?")
    print("🏷️  Tags Filter: ['technical']")
    print("📋 Metadata Filter: {'priority': 'high', 'phase': 'development'}\n")
    
    response = requests.post(url, json=data)
    result = response.json()
    
    print(f"✅ Success: {result['success']}")
    print(f"📝 Answer: {result['answer']}\n")
    print(f"📊 Chunks Retrieved: {result['chunks_retrieved']}")
    
    if result.get('similarity_scores'):
        print("\n🎯 Similarity Scores:")
        for score in result['similarity_scores']:
            print(f"  - Source: {score['source']}")
            print(f"    Score: {score['score']}")
            print(f"    Tags: {score.get('tags', [])}")
            print(f"    Metadata: {score.get('metadata', {})}")
            print()

def query_specific_author():
    """Query documents from specific author"""
    print_section("7. QUERY BY SPECIFIC AUTHOR")
    
    url = f"{BASE_URL}/query"
    data = {
        "query": "What did Dr. John Smith write about?",
        "model": "gpt-4o-mini",
        "temperature": 0.1,
        "metadata_filter": {
            "author": "Dr. John Smith"
        }
    }
    
    print("❓ Query: What did Dr. John Smith write about?")
    print("📋 Metadata Filter: {'author': 'Dr. John Smith'}\n")
    
    response = requests.post(url, json=data)
    result = response.json()
    
    print(f"✅ Success: {result['success']}")
    print(f"📝 Answer: {result['answer']}\n")
    print(f"📊 Chunks Retrieved: {result['chunks_retrieved']}")

def query_by_quarter():
    """Query quarterly reports"""
    print_section("8. QUERY BY QUARTER")
    
    url = f"{BASE_URL}/query"
    data = {
        "query": "What were the results in Q4?",
        "model": "gpt-4o-mini",
        "temperature": 0.1,
        "tags": ["quarterly-report"],
        "metadata_filter": {
            "quarter": "Q4",
            "year": 2024
        }
    }
    
    print("❓ Query: What were the results in Q4?")
    print("🏷️  Tags Filter: ['quarterly-report']")
    print("📋 Metadata Filter: {'quarter': 'Q4', 'year': 2024}\n")
    
    response = requests.post(url, json=data)
    result = response.json()
    
    print(f"✅ Success: {result['success']}")
    print(f"📝 Answer: {result['answer']}\n")
    print(f"📊 Chunks Retrieved: {result['chunks_retrieved']}")

def main():
    """Run all examples"""
    print("\n" + "🚀"*30)
    print("  TAGS AND METADATA FILTERING EXAMPLES")
    print("🚀"*30)
    
    try:
        # Step 1: Upload test documents
        upload_test_documents()
        
        # Step 2: List all documents
        list_all_documents()
        
        # Step 3-8: Various query examples
        query_without_filters()
        query_with_tags()
        query_with_metadata()
        query_with_both_filters()
        query_specific_author()
        query_by_quarter()
        
        print_section("✅ ALL TESTS COMPLETED")
        print("You can now experiment with your own queries and filters!")
        print("\nTips:")
        print("- Use tags for broad categorization")
        print("- Use metadata for specific filtering")
        print("- Combine both for precise results")
        print("- Check similarity scores to see which documents matched")
        
    except requests.exceptions.ConnectionError:
        print("\n❌ ERROR: Cannot connect to API server")
        print("Make sure the server is running: python api_server.py")
    except Exception as e:
        print(f"\n❌ ERROR: {e}")

if __name__ == "__main__":
    main()
