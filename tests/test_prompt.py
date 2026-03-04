import asyncio
import os
import sys

# Ensure UTF-8 output
sys.stdout.reconfigure(encoding='utf-8')

# Mock running from root
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.rag.researcher import node_researcher
from src.rag.legal_writer import node_legal_writer
from langchain_core.messages import HumanMessage

async def main():
    print("🤖 Querying Researcher Node...")
    query = "Segundo a resolução de gestão de cadastro (Resolução TSE nº 23.659/2021) como ela trata eleitores suspensos, eles podem realizar transferencia ou titulo?"
    
    state = {"messages": [HumanMessage(content=query)]}
    
    res = await node_researcher(state)
    print('\n--- RESEARCHER OUTPUT ---')
    print(res['messages'][-1].content)
    
    print("\n\n🤖 Querying Legal Writer Node...")
    state["messages"].append(res['messages'][-1])
    state["validation_passed"] = True
    
    res2 = await node_legal_writer(state)
    print('\n--- LEGAL WRITER OUTPUT ---')
    print(res2['messages'][-1].content)

if __name__ == "__main__":
    asyncio.run(main())
