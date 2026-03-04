import sys
import os
sys.path.insert(0, os.path.abspath('libs'))

try:
    from langchain.chains import create_retrieval_chain
    print("✅ Success: create_retrieval_chain imported")
except ImportError as e:
    print(f"❌ Failed: {e}")
    import langchain
    print(f"langchain file: {langchain.__file__}")
    print(f"langchain path: {langchain.__path__}")
