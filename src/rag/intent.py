import asyncio
import re
from tenacity import retry, stop_after_attempt, wait_exponential
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import HumanMessage
from src.config import OPENAI_API_KEY, MODEL_NAME, OPENAI_API_BASE

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
def call_llm_with_retry(llm, prompt_val):
    return llm.invoke(prompt_val)

def check_sensitive_data(text: str) -> bool:
    """Skill lgpd-privacy-shield: Detects CPF, RG, or Electoral Title numbers."""
    cpf_pattern = r"\b\d{3}\.?\d{3}\.?\d{3}-?\d{2}\b"
    title_pattern = r"\b\d{12}\b"
    rg_pattern = r"\b\d{7,9}\b"
    return bool(re.search(cpf_pattern, text) or re.search(title_pattern, text) or re.search(rg_pattern, text))

async def node_intent(state):
    messages = state["messages"]
    last_message = messages[-1]
    
    if not isinstance(last_message, HumanMessage):
        return {"user_persona": "eleitor", "has_sensitive_data": False}
    
    query = last_message.content
    has_sensitive = check_sensitive_data(query)
    
    # Prompt the LLM to classify the user's intent/persona
    system_prompt = (
        "Você é um classificador de intenção da Justiça Eleitoral.\n"
        "Avalie a mensagem do usuário e classifique o perfil em UMA ÚNICA PALAVRA.\n"
        "RESPONDA APENAS 'servidor' OU 'eleitor'.\n\n"
        "Regras:\n"
        "- 'servidor': Perguntas técnicas sobre jargões de cartório, códigos ASE (ex: 337, 540, 370), prazos de recursos jurídicos, Resoluções especificas, sistemas (Elo, PJe), doutrina (José Jairo Gomes). (ex: 'como lanço ASE 540?', 'qual o prazo para recurso inominado?').\n"
        "- 'eleitor': Perguntas comuns sobre título de eleitor, biometria, local de votação, multas, justificativa, mudei de cidade. (ex: 'como tiro 2ª via?', 'mudei de casa como transfiro?', 'documentos para alistamento')."
    )
    
    prompt = ChatPromptTemplate.from_template(system_prompt + "\n\nUsuário: {query}\n\nPerfil:")
    llm = ChatOpenAI(model=MODEL_NAME, api_key=OPENAI_API_KEY, base_url=OPENAI_API_BASE, temperature=0.0)
    
    prompt_val = prompt.invoke({"query": query})
    response_msg = await asyncio.to_thread(call_llm_with_retry, llm, prompt_val)
    
    classification = response_msg.content.strip().lower()
    persona = "servidor" if "servidor" in classification else "eleitor"
         
    return {
        "user_persona": persona,
        "has_sensitive_data": has_sensitive
    }

