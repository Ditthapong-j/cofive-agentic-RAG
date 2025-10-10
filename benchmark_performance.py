"""
Performance benchmark script for Agentic RAG system
Tests query speed with and without filters
"""
import requests
import time
import json
from statistics import mean, stdev

BASE_URL = "http://localhost:8003"

def benchmark_query(query_data, description, runs=5):
    """Run a query multiple times and measure performance"""
    print(f"\n{'='*60}")
    print(f"🧪 Benchmarking: {description}")
    print(f"{'='*60}")
    
    times = []
    chunks_retrieved = []
    
    for i in range(runs):
        start = time.time()
        response = requests.post(f"{BASE_URL}/query", json=query_data)
        elapsed = time.time() - start
        
        if response.status_code == 200:
            result = response.json()
            times.append(elapsed)
            chunks_retrieved.append(result.get('chunks_retrieved', 0))
            
            if i == 0:  # Show first result
                print(f"\n📝 First Run Result:")
                print(f"   Answer (preview): {result['answer']}")
                print(f"   Chunks: {result.get('chunks_retrieved', 0)}")
        else:
            print(f"❌ Run {i+1} failed: {response.status_code}")
    
    if times:
        avg_time = mean(times)
        std_time = stdev(times) if len(times) > 1 else 0
        avg_chunks = mean(chunks_retrieved)
        
        print(f"\n📊 Performance Stats ({runs} runs):")
        print(f"   Average Time: {avg_time:.3f}s")
        print(f"   Std Dev: {std_time:.3f}s")
        print(f"   Min Time: {min(times):.3f}s")
        print(f"   Max Time: {max(times):.3f}s")
        print(f"   Avg Chunks: {avg_chunks:.1f}")
        
        # Performance rating
        if avg_time < 1.5:
            rating = "⚡ EXCELLENT"
        elif avg_time < 2.5:
            rating = "✅ GOOD"
        elif avg_time < 4.0:
            rating = "⚠️  ACCEPTABLE"
        else:
            rating = "❌ SLOW"
        
        print(f"   Rating: {rating}")
        
        return avg_time, avg_chunks
    
    return None, None

def upload_test_documents():
    """Upload test documents for benchmarking"""
    print("\n" + "="*60)
    print("📤 Uploading Test Documents")
    print("="*60)
    
    url = f"{BASE_URL}/upload"
    
    # Create test documents with varying complexity
    docs = [
        {
            'content': """AI Research Paper 2024
            This paper discusses advanced machine learning techniques for natural language processing.
            Our experiments show significant improvements in text classification accuracy.
            The proposed model achieves 95% accuracy on benchmark datasets.
            Future work includes extending the model to multilingual scenarios.""",
            'filename': 'ai_research.txt',
            'tags': 'research,AI,NLP',
            'metadata': json.dumps({'author': 'Dr. Smith', 'year': 2024, 'department': 'R&D'})
        },
        {
            'content': """Q4 2024 Business Report
            Marketing campaign results exceeded expectations with 45% growth.
            Revenue increased by 30% compared to Q3 2024.
            Customer satisfaction scores reached all-time high of 9.2/10.
            Recommendations include expanding digital marketing efforts.""",
            'filename': 'business_q4.txt',
            'tags': 'business,marketing,quarterly',
            'metadata': json.dumps({'author': 'Jane Doe', 'year': 2024, 'quarter': 'Q4', 'department': 'Marketing'})
        },
        {
            'content': """Technical Documentation v2.0
            System architecture uses microservices pattern for scalability.
            API response time is consistently under 100ms.
            Database optimization includes indexing and query caching.
            Monitoring shows 99.9% uptime over the past month.""",
            'filename': 'tech_doc.txt',
            'tags': 'technical,documentation,backend',
            'metadata': json.dumps({'project': 'AI-Assistant', 'team': 'Backend', 'version': '2.0'})
        }
    ]
    
    for doc in docs:
        files = [('files', (doc['filename'], doc['content'], 'text/plain'))]
        params = {
            'tags': doc['tags'],
            'metadata': doc['metadata']
        }
        
        start = time.time()
        response = requests.post(url, files=files, params=params)
        elapsed = time.time() - start
        
        if response.status_code == 200:
            print(f"✅ Uploaded {doc['filename']} in {elapsed:.3f}s")
        else:
            print(f"❌ Failed to upload {doc['filename']}")
    
    time.sleep(2)  # Wait for processing

def run_benchmarks():
    """Run comprehensive performance benchmarks"""
    print("\n" + "🚀"*30)
    print("  PERFORMANCE BENCHMARK SUITE")
    print("🚀"*30)
    
    # Upload test documents
    upload_test_documents()
    
    results = []
    
    # Test 1: Simple query without filters
    result = benchmark_query(
        {
            "query": "What topics are covered in the documents?",
            "model": "gpt-4o-mini",
            "temperature": 0.1
        },
        "Simple Query (No Filters)",
        runs=5
    )
    results.append(("Simple Query", result[0] if result[0] else 0))
    
    # Test 2: Query with tag filter
    result = benchmark_query(
        {
            "query": "What are the research findings?",
            "model": "gpt-4o-mini",
            "temperature": 0.1,
            "tags": ["research"]
        },
        "Query with Tag Filter",
        runs=5
    )
    results.append(("Tag Filter", result[0] if result[0] else 0))
    
    # Test 3: Query with metadata filter
    result = benchmark_query(
        {
            "query": "What are the 2024 results?",
            "model": "gpt-4o-mini",
            "temperature": 0.1,
            "metadata_filter": {"year": 2024}
        },
        "Query with Metadata Filter",
        runs=5
    )
    results.append(("Metadata Filter", result[0] if result[0] else 0))
    
    # Test 4: Query with both filters
    result = benchmark_query(
        {
            "query": "What did the R&D team research?",
            "model": "gpt-4o-mini",
            "temperature": 0.1,
            "tags": ["research"],
            "metadata_filter": {"department": "R&D", "year": 2024}
        },
        "Query with Tag + Metadata Filters",
        runs=5
    )
    results.append(("Combined Filters", result[0] if result[0] else 0))
    
    # Test 5: Query with high max_chunks
    # First update settings
    settings_response = requests.post(
        f"{BASE_URL}/settings/instructions",
        json={
            "system_instruction": "You are a helpful assistant.",
            "response_length": "medium",
            "show_similarity_scores": True,
            "max_chunks": 10,
            "similarity_threshold": 0.0
        }
    )
    
    result = benchmark_query(
        {
            "query": "Summarize all documents",
            "model": "gpt-4o-mini",
            "temperature": 0.1
        },
        "Query with High max_chunks (10)",
        runs=3
    )
    results.append(("High max_chunks", result[0] if result[0] else 0))
    
    # Reset settings to default
    requests.post(
        f"{BASE_URL}/settings/instructions",
        json={
            "system_instruction": "You are a helpful assistant.",
            "response_length": "medium",
            "show_similarity_scores": True,
            "max_chunks": 5,
            "similarity_threshold": 0.1
        }
    )
    
    # Test 6: Query with similarity scores disabled
    result = benchmark_query(
        {
            "query": "What are the key points?",
            "model": "gpt-4o-mini",
            "temperature": 0.1
        },
        "Query with Similarity Scores Disabled",
        runs=5
    )
    results.append(("No Scores", result[0] if result[0] else 0))
    
    # Print summary
    print("\n" + "="*60)
    print("📊 PERFORMANCE SUMMARY")
    print("="*60)
    
    for test_name, avg_time in results:
        if avg_time > 0:
            if avg_time < 1.5:
                emoji = "⚡"
            elif avg_time < 2.5:
                emoji = "✅"
            elif avg_time < 4.0:
                emoji = "⚠️ "
            else:
                emoji = "❌"
            
            print(f"{emoji} {test_name:30s} {avg_time:.3f}s")
    
    print("\n" + "="*60)
    print("🎯 RECOMMENDATIONS")
    print("="*60)
    
    avg_all = mean([t for _, t in results if t > 0])
    
    if avg_all < 2.0:
        print("✅ Performance is EXCELLENT!")
        print("   System is well optimized for production use.")
    elif avg_all < 3.0:
        print("✅ Performance is GOOD!")
        print("   System is ready for production use.")
        print("   Consider reducing max_chunks if faster response needed.")
    else:
        print("⚠️  Performance needs improvement!")
        print("   Recommendations:")
        print("   - Reduce max_chunks to 3-5")
        print("   - Increase similarity_threshold to 0.2-0.3")
        print("   - Disable similarity scores when not needed")
        print("   - Use more specific queries")
    
    print("\n" + "="*60)
    print("✨ Benchmark Complete!")
    print("="*60 + "\n")

if __name__ == "__main__":
    try:
        run_benchmarks()
    except requests.exceptions.ConnectionError:
        print("\n❌ ERROR: Cannot connect to API server")
        print("Make sure the server is running: python api_server.py")
    except KeyboardInterrupt:
        print("\n\n⚠️  Benchmark interrupted by user")
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
