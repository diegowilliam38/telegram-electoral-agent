import sys
import os

try:
    import langchain
    print(f"Langchain: {langchain.__version__}")
    print(f"File: {langchain.__file__}")
except ImportError:
    print("Langchain not requested to import here explicitly to start search")

# Search strategy
# 1. Try old import
try:
    from langchain.chains import create_retrieval_chain
    print("✅ Found in langchain.chains")
except ImportError:
    print("❌ Not in langchain.chains")

# 2. Try newer location?
try:
    from langchain.chains.retrieval import create_retrieval_chain
    print("✅ Found in langchain.chains.retrieval")
except ImportError:
    print("❌ Not in langchain.chains.retrieval")

# 3. Dir scan
import langchain.chains
print(f"Dir(langchain.chains): {dir(langchain.chains)}")
