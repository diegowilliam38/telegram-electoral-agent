import sys
import os

print("--- Python Info ---")
print(f"Executable: {sys.executable}")
print(f"Version: {sys.version}")

print("\n--- sys.path ---")
for p in sys.path:
    print(p)

print("\n--- Langchain Import Check ---")
try:
    import langchain
    print(f"✅ Langchain found at: {langchain.__file__}")
    
    try:
        from langchain import chains
        print(f"✅ langchain.chains found: {chains}")
    except ImportError as e:
        print(f"❌ Failed to import langchain.chains: {e}")
        print(f"langchain dir: {dir(langchain)}")

except ImportError as e:
    print(f"❌ Failed to import langchain: {e}")

print("\n--- Pypdf Check ---")
try:
    import pypdf
    print(f"✅ pypdf found at: {pypdf.__file__}")
except ImportError as e:
    print(f"❌ Failed to import pypdf: {e}")
