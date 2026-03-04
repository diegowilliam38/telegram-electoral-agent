import os
import langchain

package_dir = os.path.dirname(langchain.__file__)
print(f"Scanning package dir: {package_dir}")

target_names = ["create_retrieval_chain", "RetrievalQA", "Chroma"]

found = []

for root, dirs, files in os.walk(package_dir):
    for file in files:
        if file.endswith(".py"):
            filepath = os.path.join(root, file)
            relpath = os.path.relpath(filepath, package_dir)
            try:
                with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                    for target in target_names:
                        if target in content:
                            found.append((target, relpath))
            except:
                pass

print("\n--- Findings ---")
for target, path in found:
    print(f"Found '{target}' in: {path}")
