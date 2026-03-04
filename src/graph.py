from typing import TypedDict, Annotated, Sequence
import operator
from langchain_core.messages import BaseMessage
from langgraph.graph import StateGraph, END

from src.rag.intent import node_intent
from src.rag.researcher import node_researcher
from src.rag.validator_skill import node_validator
from src.rag.legal_writer import node_legal_writer

# Define State for Multiagent System
class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], operator.add]
    context_docs: str
    validation_passed: bool
    user_persona: str

# Build Graph
def build_graph():
    # Pre-warm ChromaDB retriever by instantiating the first time if needed
    # But for LangGraph we can just let it initialize at first call.
    
    workflow = StateGraph(AgentState)

    # Add 4 nodes matching the ADR-006 architecture + Intent Routing
    workflow.add_node("intent", node_intent)
    workflow.add_node("researcher", node_researcher)
    workflow.add_node("validator", node_validator)
    workflow.add_node("legal_writer", node_legal_writer)
    
    workflow.set_entry_point("intent")
    workflow.add_edge("intent", "researcher")
    workflow.add_edge("researcher", "validator")
    workflow.add_edge("validator", "legal_writer")
    workflow.add_edge("legal_writer", END)

    # Adding Memory Saver for checkpointing
    from langgraph.checkpoint.memory import MemorySaver
    checkpointer = MemorySaver()
    app = workflow.compile(checkpointer=checkpointer)
    return app
