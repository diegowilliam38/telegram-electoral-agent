import re

async def node_validator(state):
    messages = state["messages"]
    context_docs = state.get("context_docs", "")
    
    if not messages:
        return {"validation_passed": True}
        
    last_msg = messages[-1].content.lower()
    
    if "inconclusivo" in last_msg:
        # No citations to validate
        return {"validation_passed": True}
    
    # Skill de Validação: Evita alucinação de artigos ou páginas que não estão no texto recuperado.
    # Ex: se o modelo afirma "art. 15", verificamos se "15" existe no contexto recuperado.
    citations_mentioned = set(re.findall(r"(?:artigo|art\.|página|pag\.|pág\.)\s*(\d+[a-z]?)", last_msg))
    
    if not citations_mentioned:
        return {"validation_passed": True}
        
    context_lower = context_docs.lower()
    
    for cit in citations_mentioned:
        # Se um número de artigo mencionado não estiver no contexto bruto, detectamos hallucination.
        if cit not in context_lower:
            return {"validation_passed": False}
            
    return {"validation_passed": True}
