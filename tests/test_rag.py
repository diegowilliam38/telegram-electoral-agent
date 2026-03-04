import sys
import os

# Add project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.rag.retrieval import get_rag_chain

def test_rag():
    print("🧠 Testing RAG Chain...")
    try:
        chain = get_rag_chain()
        query = "Quais os documentos necessários para alistamento eleitoral?"
        print(f"❓ Query: {query}")
        
        response = chain.invoke({"input": query})
        print(f"💡 Answer: {response['answer']}")
        print("✅ RAG Test Passed!")
    except Exception as e:
        print(f"❌ RAG Test Failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_rag()
