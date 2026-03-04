import sys
import os
sys.stdout.reconfigure(encoding='utf-8')
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.rag.researcher import _vector_store

docs = _vector_store.similarity_search("Art. 51 suspensão de direitos políticos alistamento transferência revisão", k=10)
with open("test_art51.txt", "w", encoding="utf-8") as f:
    for i, d in enumerate(docs):
        f.write(f"--- DOC {i} ---\n")
        f.write(d.page_content + "\n\n")
print("Search complete.")
