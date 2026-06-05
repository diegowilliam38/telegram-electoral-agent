import asyncio
import sys
from src.graph import build_graph
from langchain_core.messages import HumanMessage

sys.stdout.reconfigure(encoding='utf-8')

async def test_persona_skills():
    print("🧪 Starting Persona & Cognitive Skills Verification Tests...")
    app = build_graph()
    
    test_cases = [
        {
            "name": "Servidor Mode - Technical ASE Code (BLUF & Minto Check)",
            "query": "Como lançar o código ASE de condenação criminal?",
            "thread_id": "servidor_thread_1",
            "expected_persona": "servidor",
            "assertions": [
                ("BLUF Check (ASE 337 in first paragraph)", lambda res: "337" in res.split("\n\n")[0] or "337" in res.split("\n")[0] or "337" in res[:150])
            ]
        },
        {
            "name": "Servidor Mode - Doctrinal Query (Minto Pyramid Check)",
            "query": "O que é elegibilidade ou inelegibilidade segundo a doutrina de José Jairo Gomes?",
            "thread_id": "servidor_thread_2",
            "expected_persona": "servidor",
            "assertions": [
                ("Minto Check (Cites José Jairo Gomes/LC 64 at the end/references)", lambda res: "José Jairo Gomes" in res or "64/1990" in res)
            ]
        },
        {
            "name": "Eleitor Mode - Public Transfer Query (ELI5 & Rule of Three Check)",
            "query": "Quais os documentos para transferência de título?",
            "thread_id": "eleitor_thread_1",
            "expected_persona": "eleitor",
            "assertions": [
                ("No Markdown Check", lambda res: not any(marker in res for marker in ["**", "_", "###", "##", "* "])),
                ("ELI5/No internal jargon Check", lambda res: not any(jargon in res.lower().split() for jargon in ["ase", "elo", "motivo"]))
            ]
        },
        {
            "name": "Eleitor Mode - Privacy Warning (LGPD Active Check)",
            "query": "Meu CPF é 123.456.789-00, como vejo meu local de votação?",
            "thread_id": "eleitor_thread_2",
            "expected_persona": "eleitor",
            "assertions": [
                ("LGPD Warning Present Check", lambda res: "Aviso de Privacidade" in res or "dados pessoais" in res or "CPF" in res)
            ]
        }
    ]
    
    for case in test_cases:
        print(f"\n========================================\n📌 Running: {case['name']}")
        print(f"💬 Query: {case['query']}")
        print("⏳ Invoking graph...")
        
        inputs = {"messages": [HumanMessage(content=case["query"])]}
        config = {"configurable": {"thread_id": case["thread_id"]}}
        
        try:
            response = await app.ainvoke(inputs, config=config)
            persona = response.get("user_persona", "N/A")
            last_msg = response["messages"][-1].content
            
            print(f"👤 Classified Persona: {persona.upper()}")
            print(f"🤖 Response:\n{last_msg}\n")
            
            # Assertions run
            print("🔬 Running Skill Assertions:")
            for label, assertion_func in case["assertions"]:
                passed = assertion_func(last_msg)
                status_icon = "✅" if passed else "❌"
                print(f"  {status_icon} {label}")
                
        except Exception as e:
            print(f"❌ Failed to run test: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    if hasattr(asyncio, 'WindowsSelectorEventLoopPolicy'):
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(test_persona_skills())
