#!/usr/bin/env python3
"""
End-to-end chat test for Agentic RAG API
- Ensures server is running
- Uploads test files if needed
- Initializes agent
- Sends multiple chat messages to /query
- Saves results to tests/chat_test_results.json
"""

import requests
import time
import json
import os
from pathlib import Path

BASE_URL = os.environ.get('API_BASE_URL', 'http://localhost:8003')
TEST_FILES_DIR = Path(__file__).parent / 'test_files'
OUTPUT_FILE = Path(__file__).parent / 'chat_test_results.json'

TEST_MESSAGES = [
    'ระบบนี้ทำอะไรได้บ้าง?',
    'รองรับไฟล์อะไรบ้าง?',
    'อธิบายการทำงานของ RAG แบบสั้นๆ',
    'ขั้นตอนการใช้งานคืออะไร?',
]

session = requests.Session()


def ensure_server_running(timeout=5):
    try:
        r = session.get(f'{BASE_URL}/health', timeout=timeout)
        return r.status_code == 200
    except Exception:
        return False


def upload_test_files():
    files = []
    for p in TEST_FILES_DIR.glob('*'):
        if p.suffix.lower() in ['.txt', '.md', '.pdf']:
            files.append(('files', (p.name, open(p, 'rb'), 'text/plain')))
    if not files:
        return {'uploaded': False, 'details': 'No test files found'}
    try:
        r = session.post(f'{BASE_URL}/upload', files=files, timeout=60)
        # close file handles
        for _, (_, fh, _) in files:
            fh.close()
        return r.json()
    except Exception as e:
        return {'uploaded': False, 'error': str(e)}


def initialize_agent():
    try:
        r = session.post(f'{BASE_URL}/initialize', json={'model': 'gpt-4o-mini', 'temperature': 0.1}, timeout=60)
        return {'status_code': r.status_code, 'json': r.json()}
    except Exception as e:
        return {'error': str(e)}


def query_message(message):
    try:
        start = time.time()
        r = session.post(f'{BASE_URL}/query', json={'query': message, 'model': 'gpt-4o-mini', 'temperature': 0.1}, timeout=120)
        elapsed = time.time() - start
        return {'status_code': r.status_code, 'json': r.json(), 'elapsed': elapsed}
    except Exception as e:
        return {'error': str(e)}


def run_chat_test():
    results = {'base_url': BASE_URL, 'timestamp': time.time(), 'server': {}, 'upload': None, 'initialize': None, 'messages': []}

    # Check server
    server_ok = ensure_server_running()
    results['server']['running'] = server_ok
    if not server_ok:
        print('❌ API server not running at', BASE_URL)
        results['error'] = 'server_not_running'
        with open(OUTPUT_FILE, 'w') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        return results
    else:
        print('✅ Server is running')

    # Check status
    try:
        status = session.get(f'{BASE_URL}/status', timeout=10).json()
        results['server']['status'] = status
    except Exception as e:
        results['server']['status_error'] = str(e)

    # Upload files if document_count == 0
    doc_count = results['server']['status'].get('document_count') if results['server'].get('status') else None
    if doc_count == 0 or doc_count is None:
        print('📁 Uploading test files...')
        upload_res = upload_test_files()
        results['upload'] = upload_res
        print('   ', upload_res)
    else:
        print(f'📁 Documents already loaded: {doc_count}')

    # Initialize agent
    print('⚙️  Initializing agent...')
    init_res = initialize_agent()
    results['initialize'] = init_res
    print('   ', init_res)

    # If initialization failed and indicates no documents, attempt upload again
    if init_res.get('status_code') == 400 and 'No documents' in json.dumps(init_res.get('json', {})):
        print('   No documents available, uploading and retrying...')
        upload_res = upload_test_files()
        results['upload_retry'] = upload_res
        init_res = initialize_agent()
        results['initialize_retry'] = init_res

    # Query messages
    print('💬 Sending test messages...')
    for m in TEST_MESSAGES:
        print('  →', m)
        res = query_message(m)
        results['messages'].append({'message': m, 'result': res})
        print('    ', res.get('status_code') if 'status_code' in res else res)
        time.sleep(0.5)

    # Save results
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    print('💾 Results saved to', OUTPUT_FILE)
    return results


if __name__ == '__main__':
    run_chat_test()
