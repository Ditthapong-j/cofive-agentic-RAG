"""
Test script to measure query response time
Target: 2-3 seconds
"""
import requests
import time
import json
from typing import Dict, List

BASE_URL = "http://localhost:8000"

def test_query_speed(query: str, tags: List[str] = None, metadata_filter: Dict = None) -> Dict:
    """Test query speed and return timing info"""
    url = f"{BASE_URL}/query"
    payload = {
        "query": query,
        "tags": tags or [],
        "metadata_filter": metadata_filter or {}
    }
    
    print(f"\n{'='*70}")
    print(f"Testing Query: {query}")
    if tags:
        print(f"Tags: {tags}")
    if metadata_filter:
        print(f"Metadata: {metadata_filter}")
    print(f"{'='*70}")
    
    # Measure request time
    start = time.time()
    
    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()
        
        elapsed = time.time() - start
        result = response.json()
        
        print(f"\n✅ Request completed in {elapsed:.2f} seconds")
        
        # Extract timing from response if available
        if "timing" in result:
            print(f"\nDetailed Timing:")
            for key, value in result["timing"].items():
                print(f"  - {key}: {value}")
        
        # Show answer preview
        answer = result.get("answer", "")
        print(f"\nAnswer Preview: {answer[:200]}..." if len(answer) > 200 else f"\nAnswer: {answer}")
        
        # Speed assessment
        if elapsed <= 3:
            print(f"\n🎯 EXCELLENT: Within target (2-3 seconds)")
        elif elapsed <= 5:
            print(f"\n⚠️  ACCEPTABLE: Slightly above target")
        else:
            print(f"\n❌ SLOW: Needs optimization")
        
        return {
            "query": query,
            "elapsed_time": elapsed,
            "success": True,
            "answer_length": len(answer),
            "timing": result.get("timing", {})
        }
        
    except requests.exceptions.RequestException as e:
        elapsed = time.time() - start
        print(f"\n❌ Request failed in {elapsed:.2f} seconds")
        print(f"Error: {str(e)}")
        
        return {
            "query": query,
            "elapsed_time": elapsed,
            "success": False,
            "error": str(e)
        }

def run_speed_tests():
    """Run multiple speed tests"""
    print("\n" + "="*70)
    print("SPEED TEST SUITE - Target: 2-3 seconds per query")
    print("="*70)
    
    # Check if server is running
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code != 200:
            print("❌ Server not responding. Please start the server first.")
            return
    except:
        print("❌ Cannot connect to server. Please start with: python api_server.py")
        return
    
    test_cases = [
        {
            "query": "Python คืออะไร",
            "tags": [],
            "metadata_filter": {}
        },
        {
            "query": "Python มีข้อดีอะไรบ้าง",
            "tags": ["python"],
            "metadata_filter": {}
        },
        {
            "query": "AI คืออะไร",
            "tags": ["ai"],
            "metadata_filter": {"category": "technology"}
        },
        {
            "query": "อธิบายเกี่ยวกับ machine learning",
            "tags": [],
            "metadata_filter": {}
        },
    ]
    
    results = []
    total_time = 0
    success_count = 0
    
    for i, test in enumerate(test_cases, 1):
        print(f"\n\n{'#'*70}")
        print(f"TEST CASE {i}/{len(test_cases)}")
        print(f"{'#'*70}")
        
        result = test_query_speed(
            query=test["query"],
            tags=test.get("tags"),
            metadata_filter=test.get("metadata_filter")
        )
        
        results.append(result)
        
        if result["success"]:
            total_time += result["elapsed_time"]
            success_count += 1
        
        # Wait between tests
        if i < len(test_cases):
            print("\nWaiting 2 seconds before next test...")
            time.sleep(2)
    
    # Summary
    print("\n\n" + "="*70)
    print("SUMMARY")
    print("="*70)
    
    if success_count > 0:
        avg_time = total_time / success_count
        print(f"\nTotal Tests: {len(test_cases)}")
        print(f"Successful: {success_count}")
        print(f"Failed: {len(test_cases) - success_count}")
        print(f"\nAverage Response Time: {avg_time:.2f} seconds")
        
        # Performance assessment
        if avg_time <= 3:
            print(f"\n🎯 EXCELLENT: Average time within target!")
            print(f"   Target: 2-3 seconds")
            print(f"   Actual: {avg_time:.2f} seconds")
        elif avg_time <= 5:
            print(f"\n⚠️  GOOD: Close to target but can improve")
            print(f"   Target: 2-3 seconds")
            print(f"   Actual: {avg_time:.2f} seconds")
        else:
            print(f"\n❌ NEEDS IMPROVEMENT")
            print(f"   Target: 2-3 seconds")
            print(f"   Actual: {avg_time:.2f} seconds")
        
        print("\nIndividual Test Times:")
        for i, result in enumerate(results, 1):
            if result["success"]:
                status = "✅" if result["elapsed_time"] <= 3 else "⚠️"
                print(f"  {status} Test {i}: {result['elapsed_time']:.2f}s - {result['query'][:50]}")
    else:
        print("\n❌ All tests failed!")
    
    # Save results
    output_file = f"speed_test_results_{int(time.time())}.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    print(f"\n📄 Results saved to: {output_file}")
    print("="*70)

if __name__ == "__main__":
    run_speed_tests()
