import asyncio
import sys
from src.rag.researcher import _retriever, node_researcher
from langchain_core.messages import HumanMessage

sys.stdout.reconfigure(encoding='utf-8')

async def test():
    query = "Quais os documentos para transferência de título?"
    print(f"🔍 Query: {query}")
    
    docs = _retriever.invoke(query)
    print(f"\n📄 Retrieved {len(docs)} documents:")
    for idx, doc in enumerate(docs):
        print(f"\n--- Document {idx+1} (Source: {doc.metadata.get('source', 'unknown')}) ---")
        print(doc.page_content[:300] + "...")
        
    state = {"messages": [HumanMessage(content=query)], "user_persona": "eleitor"}
    result = await node_researcher(state)
    print(f"\n🤖 Researcher output content:")
    print(result["messages"][0].content)

if __name__ == "__main__":
    asyncio.run(test())
