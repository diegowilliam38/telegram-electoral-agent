import sys
import os
import importlib.util
import platform
import asyncio

def check_import(name):
    try:
        importlib.import_module(name)
        return f"✅ {name}"
    except ImportError as e:
        return f"❌ {name}: {e}"

def check_env():
    print(f"Python: {sys.version}")
    print(f"Platform: {platform.platform()}")
    print(f"Event Loop Policy (Win32): {asyncio.get_event_loop_policy().__class__.__name__}")
    
    deps = [
        "langchain", "langchain_core", "langchain_community", 
        "langchain_openai", "telegram", "chromadb", "pydantic", "httpx"
    ]
    print("\n--- Dependencies ---")
    for dep in deps:
        print(check_import(dep))

def check_files():
    print("\n--- Critical Files ---")
    files = [
        "src/bot.py", "src/config.py", "src/rag/retrieval.py", 
        "src/rag/ingestion.py", ".env", "data/chroma_db"
    ]
    for f in files:
        exists = os.path.exists(f)
        status = "✅ Found" if exists else "❌ Missing"
        print(f"{f}: {status}")

if __name__ == "__main__":
    check_env()
    check_files()
