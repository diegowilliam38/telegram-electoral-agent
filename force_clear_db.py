import os
import shutil
import time
from src.config import DB_DIR

print("🔪 Attempting to force clear DB_DIR...")
retries = 5
for i in range(retries):
    try:
        if os.path.exists(DB_DIR):
            shutil.rmtree(DB_DIR)
        print("✅ DB_DIR cleared successfully.")
        break
    except Exception as e:
        print(f"⚠️ Attempt {i+1} failed: {e}")
        time.sleep(2)
