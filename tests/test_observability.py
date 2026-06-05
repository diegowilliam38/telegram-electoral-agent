import os
import time
import shutil
import json
import httpx
import sys

sys.stdout.reconfigure(encoding='utf-8')

API_URL = "http://localhost:8123/v1/chat/completions"
LOG_FILE = os.path.join("data", "query_logs.jsonl")
STATE_FILE = os.path.join("data", "last_ingest_state.txt")
REFS_DIR = os.path.join("docs", "references")

def read_last_log_line():
    if not os.path.exists(LOG_FILE):
        return None
    with open(LOG_FILE, "r", encoding="utf-8") as f:
        lines = f.readlines()
        if not lines:
            return None
        return json.loads(lines[-1].strip())

def test_logger():
    print("\n--- Test 1: Testing Query Logging ---")
    # Clean old logs if needed or just count lines
    initial_log_count = 0
    if os.path.exists(LOG_FILE):
        with open(LOG_FILE, "r", encoding="utf-8") as f:
            initial_log_count = len(f.readlines())
            
    payload = {
        "model": "gpt-4o-mini",
        "messages": [
            {"role": "system", "content": "**User**: test_runner\n**Source**: Telegram (DM with test_runner)"},
            {"role": "user", "content": "teste observabilidade: como lançar código ase de condenação?"}
        ],
        "temperature": 0.0,
        "stream": False
    }
    
    print("Sending POST request to API...")
    try:
        response = httpx.post(API_URL, json=payload, timeout=30.0)
        print(f"Response status: {response.status_code}")
        response_json = response.json()
        print(f"Response: {response_json['choices'][0]['message']['content'][:100]}...")
        
        # Verify log file
        time.sleep(1.0) # Wait a bit for file IO
        if not os.path.exists(LOG_FILE):
            print("❌ Failure: Log file was not created!")
            return False
            
        with open(LOG_FILE, "r", encoding="utf-8") as f:
            lines = f.readlines()
            
        if len(lines) <= initial_log_count:
            print("❌ Failure: New log entry was not written to query_logs.jsonl!")
            return False
            
        last_log = json.loads(lines[-1].strip())
        print(f"✅ Success! Found new log entry:")
        print(f"  Timestamp: {last_log.get('timestamp')}")
        print(f"  Query: {last_log.get('query')}")
        print(f"  Persona: {last_log.get('persona')}")
        print(f"  Latency: {last_log.get('elapsed_seconds')}s")
        print(f"  Status: {last_log.get('status')}")
        return True
    except Exception as e:
        print(f"❌ HTTP request failed: {e}")
        return False

def test_watcher():
    print("\n--- Test 2: Testing Auto-Ingestion Watcher ---")
    if not os.path.exists(STATE_FILE):
        print("⚠️ Warning: state file last_ingest_state.txt not found. Waiting for startup watcher to write it...")
        time.sleep(5)
        
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, "r", encoding="utf-8") as f:
            initial_state = f.read().strip()
    else:
        initial_state = ""
        
    print(f"Initial state hash length: {len(initial_state)}")
    
    # 1. Select the smallest reference PDF to copy to speed up test execution
    pdf_files = [f for f in os.listdir(REFS_DIR) if f.endswith(".pdf")]
    if not pdf_files:
        print("❌ Failure: No PDFs found in docs/references/ to use for copy test.")
        return False
        
    smallest_pdf = min(pdf_files, key=lambda f: os.path.getsize(os.path.join(REFS_DIR, f)))
    source_pdf = os.path.join(REFS_DIR, smallest_pdf)
    dest_pdf = os.path.join(REFS_DIR, "mock_temp_copy.pdf")
    
    print(f"Copying smallest PDF: {smallest_pdf} ({os.path.getsize(source_pdf)} bytes) to mock_temp_copy.pdf...")
    shutil.copy(source_pdf, dest_pdf)
    
    print("⏳ Waiting for the watcher loop to detect change and complete ingestion (polling up to 90s)...")
    detected = False
    for elapsed in range(90):
        time.sleep(1.0)
        if os.path.exists(STATE_FILE):
            with open(STATE_FILE, "r", encoding="utf-8") as f:
                new_state = f.read().strip()
            if new_state != initial_state:
                detected = True
                print(f"✅ Ingestion complete detected after {elapsed+1} seconds!")
                break
                
    if not detected:
        print("❌ Failure: Watcher did not update the last_ingest_state.txt within 60 seconds!")
        if os.path.exists(dest_pdf): os.remove(dest_pdf)
        return False
        
    with open(STATE_FILE, "r", encoding="utf-8") as f:
        new_state = f.read().strip()
        
    print(f"New state hash length: {len(new_state)}")
    print("✅ Success! Watcher detected the change and updated the ingestion state.")
    
    # 3. Clean up the copied file
    print("Cleaning up mock_temp_copy.pdf...")
    os.remove(dest_pdf)
    
    print("⏳ Waiting for another ingestion cycle to clean up the index (polling up to 90s)...")
    cleaned = False
    for elapsed in range(90):
        time.sleep(1.0)
        if os.path.exists(STATE_FILE):
            with open(STATE_FILE, "r", encoding="utf-8") as f:
                final_state = f.read().strip()
            if final_state == initial_state:
                cleaned = True
                print(f"✅ Cleanup ingestion complete detected after {elapsed+1} seconds!")
                break
                
    if not cleaned:
        print("⚠️ Warning: Watcher did not revert the state back to initial within 90 seconds after cleanup.")
    else:
        print("✅ Ingestion watcher test completed and state successfully reverted.")
    return True

if __name__ == "__main__":
    time.sleep(2.0) # Wait for uvicorn to settle
    logger_ok = test_logger()
    watcher_ok = test_watcher()
    if logger_ok and watcher_ok:
        print("\n🎉 All observability and ingestion tests PASSED successfully!")
        sys.exit(0)
    else:
        print("\n❌ Some tests failed.")
        sys.exit(1)
