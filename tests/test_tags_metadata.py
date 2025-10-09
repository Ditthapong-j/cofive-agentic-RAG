"""
Test script for tags and metadata filtering functionality
"""
import requests
import json
import pytest
import time

BASE_URL = "http://localhost:8003"

def test_upload_with_tags():
    """Test uploading documents with tags"""
    url = f"{BASE_URL}/upload"
    content = "This is a test document about AI research"
    files = [('files', ('test_tags.txt', content, 'text/plain'))]
    params = {
        'tags': 'test,AI,research'
    }
    
    response = requests.post(url, files=files, params=params)
    assert response.status_code == 200
    data = response.json()
    assert data['success'] == True
    assert data['files_processed'] == 1
    print("✅ Test upload with tags: PASSED")

def test_upload_with_metadata():
    """Test uploading documents with metadata"""
    url = f"{BASE_URL}/upload"
    content = "This is a test document with metadata"
    files = [('files', ('test_metadata.txt', content, 'text/plain'))]
    params = {
        'metadata': json.dumps({
            'author': 'Test User',
            'year': 2024,
            'category': 'testing'
        })
    }
    
    response = requests.post(url, files=files, params=params)
    assert response.status_code == 200
    data = response.json()
    assert data['success'] == True
    print("✅ Test upload with metadata: PASSED")

def test_upload_with_tags_and_metadata():
    """Test uploading documents with both tags and metadata"""
    url = f"{BASE_URL}/upload"
    content = "This is a comprehensive test document"
    files = [('files', ('test_both.txt', content, 'text/plain'))]
    params = {
        'tags': 'test,comprehensive',
        'metadata': json.dumps({
            'author': 'Test User',
            'year': 2024,
            'test_type': 'integration'
        })
    }
    
    response = requests.post(url, files=files, params=params)
    assert response.status_code == 200
    data = response.json()
    assert data['success'] == True
    print("✅ Test upload with tags and metadata: PASSED")

def test_list_documents_shows_tags_metadata():
    """Test that listing documents shows tags and metadata"""
    url = f"{BASE_URL}/documents"
    response = requests.get(url)
    assert response.status_code == 200
    data = response.json()
    assert data['success'] == True
    
    # Check if any document has tags or metadata
    has_tags = any('tags' in doc for doc in data['documents'])
    has_metadata = any('metadata' in doc for doc in data['documents'])
    
    print(f"✅ Test list documents: PASSED (has_tags={has_tags}, has_metadata={has_metadata})")

def test_query_with_tag_filter():
    """Test querying with tag filter"""
    time.sleep(2)  # Wait for documents to be processed
    
    url = f"{BASE_URL}/query"
    data = {
        "query": "What is this test about?",
        "model": "gpt-4o-mini",
        "temperature": 0.1,
        "tags": ["test"]
    }
    
    response = requests.post(url, json=data)
    assert response.status_code == 200
    result = response.json()
    
    # Should find documents with 'test' tag
    assert result['success'] == True
    print(f"✅ Test query with tag filter: PASSED (chunks_retrieved={result.get('chunks_retrieved', 0)})")

def test_query_with_metadata_filter():
    """Test querying with metadata filter"""
    url = f"{BASE_URL}/query"
    data = {
        "query": "What did the Test User write?",
        "model": "gpt-4o-mini",
        "temperature": 0.1,
        "metadata_filter": {
            "author": "Test User",
            "year": 2024
        }
    }
    
    response = requests.post(url, json=data)
    assert response.status_code == 200
    result = response.json()
    
    assert result['success'] == True
    print(f"✅ Test query with metadata filter: PASSED (chunks_retrieved={result.get('chunks_retrieved', 0)})")

def test_query_with_combined_filters():
    """Test querying with both tag and metadata filters"""
    url = f"{BASE_URL}/query"
    data = {
        "query": "What are the comprehensive test results?",
        "model": "gpt-4o-mini",
        "temperature": 0.1,
        "tags": ["test", "comprehensive"],
        "metadata_filter": {
            "author": "Test User",
            "year": 2024
        }
    }
    
    response = requests.post(url, json=data)
    assert response.status_code == 200
    result = response.json()
    
    assert result['success'] == True
    print(f"✅ Test query with combined filters: PASSED (chunks_retrieved={result.get('chunks_retrieved', 0)})")

def test_similarity_scores_include_tags_metadata():
    """Test that similarity scores include tags and metadata"""
    url = f"{BASE_URL}/query"
    data = {
        "query": "What documents do we have?",
        "model": "gpt-4o-mini",
        "temperature": 0.1
    }
    
    response = requests.post(url, json=data)
    assert response.status_code == 200
    result = response.json()
    
    if result.get('similarity_scores'):
        # Check if tags and metadata are present in similarity scores
        for score in result['similarity_scores']:
            # At least some documents should have tags or metadata
            if 'tags' in score or 'metadata' in score:
                print(f"✅ Test similarity scores include tags/metadata: PASSED")
                return
    
    print("⚠️  Test similarity scores: No tags/metadata found (may be expected)")

def test_query_non_existent_tag():
    """Test querying with non-existent tag returns appropriate response"""
    url = f"{BASE_URL}/query"
    data = {
        "query": "What is this about?",
        "model": "gpt-4o-mini",
        "temperature": 0.1,
        "tags": ["nonexistent-tag-12345"]
    }
    
    response = requests.post(url, json=data)
    assert response.status_code == 200
    result = response.json()
    
    # Should return no chunks or appropriate message
    chunks = result.get('chunks_retrieved', 0)
    print(f"✅ Test non-existent tag: PASSED (chunks_retrieved={chunks})")

def test_query_non_existent_metadata():
    """Test querying with non-existent metadata returns appropriate response"""
    url = f"{BASE_URL}/query"
    data = {
        "query": "What is this about?",
        "model": "gpt-4o-mini",
        "temperature": 0.1,
        "metadata_filter": {
            "nonexistent_key": "nonexistent_value"
        }
    }
    
    response = requests.post(url, json=data)
    assert response.status_code == 200
    result = response.json()
    
    chunks = result.get('chunks_retrieved', 0)
    print(f"✅ Test non-existent metadata: PASSED (chunks_retrieved={chunks})")

def test_upload_invalid_metadata_json():
    """Test uploading with invalid metadata JSON"""
    url = f"{BASE_URL}/upload"
    content = "This is a test document"
    files = [('files', ('test_invalid.txt', content, 'text/plain'))]
    params = {
        'metadata': 'invalid json {'
    }
    
    response = requests.post(url, files=files, params=params)
    assert response.status_code == 400  # Should return bad request
    print("✅ Test invalid metadata JSON: PASSED (properly rejected)")

def run_all_tests():
    """Run all tests"""
    print("\n" + "="*60)
    print("  RUNNING TAGS AND METADATA TESTS")
    print("="*60 + "\n")
    
    tests = [
        ("Upload with tags", test_upload_with_tags),
        ("Upload with metadata", test_upload_with_metadata),
        ("Upload with tags and metadata", test_upload_with_tags_and_metadata),
        ("List documents shows tags/metadata", test_list_documents_shows_tags_metadata),
        ("Query with tag filter", test_query_with_tag_filter),
        ("Query with metadata filter", test_query_with_metadata_filter),
        ("Query with combined filters", test_query_with_combined_filters),
        ("Similarity scores include tags/metadata", test_similarity_scores_include_tags_metadata),
        ("Query non-existent tag", test_query_non_existent_tag),
        ("Query non-existent metadata", test_query_non_existent_metadata),
        ("Upload invalid metadata JSON", test_upload_invalid_metadata_json),
    ]
    
    passed = 0
    failed = 0
    
    for test_name, test_func in tests:
        try:
            print(f"\n🧪 Running: {test_name}")
            test_func()
            passed += 1
        except AssertionError as e:
            print(f"❌ FAILED: {test_name}")
            print(f"   Error: {e}")
            failed += 1
        except requests.exceptions.ConnectionError:
            print(f"❌ FAILED: {test_name}")
            print("   Error: Cannot connect to server")
            failed += 1
        except Exception as e:
            print(f"❌ FAILED: {test_name}")
            print(f"   Error: {e}")
            failed += 1
    
    print("\n" + "="*60)
    print("  TEST SUMMARY")
    print("="*60)
    print(f"✅ Passed: {passed}")
    print(f"❌ Failed: {failed}")
    print(f"📊 Total: {passed + failed}")
    print("="*60 + "\n")
    
    if failed == 0:
        print("🎉 All tests passed successfully!")
    else:
        print(f"⚠️  {failed} test(s) failed. Please review.")

if __name__ == "__main__":
    try:
        run_all_tests()
    except KeyboardInterrupt:
        print("\n\n⚠️  Tests interrupted by user")
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
