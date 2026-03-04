import sys
import os
import importlib.util

print("--- Python Info ---")
print(f"Executable: {sys.executable}")
print(f"Version: {sys.version}")

print("\n--- sys.path ---")
for p in sys.path:
    print(p)

print("\n--- Local Directory Check ---")
print(f"Propsective shadowing files in {os.getcwd()}:")
for f in os.listdir("."):
    if "langchain" in f:
        print(f"  !! Found: {f}")

print("\n--- Langchain Import Check ---")
try:
    import langchain
    print(f"✅ Langchain imported. File: {langchain.__file__}")
    print(f"Path: {langchain.__path__}")
    
    # Check if chains exists in dir
    if 'chains' in dir(langchain):
        print("✅ 'chains' is in dir(langchain)")
    else:
        print("❌ 'chains' is NOT in dir(langchain)")
        
    try:
        from langchain import chains
        print(f"✅ from langchain import chains success: {chains}")
    except ImportError as e:
        print(f"❌ Failed to import chains: {e}")

except ImportError as e:
    print(f"❌ Failed to import langchain: {e}")

print("\n--- Pip List (subprocess) ---")
import subprocess
subprocess.run([sys.executable, "-m", "pip", "list"])
