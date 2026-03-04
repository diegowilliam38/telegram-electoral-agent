import langchain
import os

print(f"File: {langchain.__file__}")
try:
    with open(langchain.__file__, 'r', encoding='utf-8') as f:
        print("--- CONTENT ---")
        print(f.read())
        print("--- END CONTENT ---")
except Exception as e:
    print(f"Error reading file: {e}")
