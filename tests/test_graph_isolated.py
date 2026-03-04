import asyncio
from src.graph import build_graph
from langchain_core.messages import HumanMessage

async def test_graph():
    print("🧪 Testing LangGraph Logic...")
    try:
        app = build_graph()
        print("✅ Graph compiled successfully.")
        
        inputs = {"messages": [HumanMessage(content="Quais os documentos para alistamento?")]}
        config = {"configurable": {"thread_id": "test_user_1"}}
        
        print("⏳ Invoking graph...")
        response = await app.ainvoke(inputs, config=config)
        
        last_msg = response["messages"][-1]
        print(f"🤖 Response: {last_msg.content[:50]}...")
        
        print("✅ Graph invocation successful.")
    except Exception as e:
        print(f"❌ Graph Failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    if hasattr(asyncio, 'WindowsSelectorEventLoopPolicy'):
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(test_graph())
