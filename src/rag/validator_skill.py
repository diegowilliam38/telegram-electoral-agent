import re

async def node_validator(state):
    """Skill legal-citation-checker: Prevents hallucination of non-existent articles, ASE codes, or laws."""
    messages = state["messages"]
    context_docs = state.get("context_docs", "")
    
    if not messages:
        return {"validation_passed": True}
        
    last_msg = messages[-1].content.lower()
    
    if "inconclusivo" in last_msg:
        # No citations to validate
        return {"validation_passed": True}
    
    # Skill: legal-citation-checker - Verifies articles, ASE codes, and numerical citations
    citations_mentioned = set(re.findall(r"(?:artigo|art\.|página|pag\.|pág\.|ase)\s*(\d+[a-z]?)", last_msg))
    
    if not citations_mentioned:
        return {"validation_passed": True}
        
    context_lower = context_docs.lower()
    
    for cit in citations_mentioned:
        # If an article or ASE code mentioned by LLM does not exist in context, flag hallucination
        if cit not in context_lower:
            return {"validation_passed": False}
            
    return {"validation_passed": True}

