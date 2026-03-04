import asyncio
from tenacity import retry, stop_after_attempt, wait_exponential
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import HumanMessage
from src.config import OPENAI_API_KEY, MODEL_NAME

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
def call_llm_with_retry(llm, prompt_val):
    return llm.invoke(prompt_val)

async def node_intent(state):
    messages = state["messages"]
    last_message = messages[-1]
    
    if not isinstance(last_message, HumanMessage):
        return {"user_persona": "eleitor"} # Default fallback
    
    query = last_message.content
    
    # Prompt the LLM to classify the user's intent/persona
    system_prompt = (
        "Você é um classificador de intenção. Avalie a seguinte mensagem e classifique o perfil do usuário em UMA ÚNICA PALAVRA.\n"
        "RESPONDA APENAS 'servidor' OU 'eleitor'.\n\n"
        "Regras:\n"
        "- 'servidor': Perguntas técnicas sobre jargões de cartório, códigos ASE, prazos de recursos jurídicos, Resoluções específicas, manuais de prática. (ex: 'como lanço ASE 540?', 'qual prazo do recurso inominado?').\n"
        "- 'eleitor': Perguntas comuns sobre título de eleitor, biometria, local de votação, multas eleitorais. (ex: 'como tiro 2ª via?', 'preciso fazer biometria?', 'documentos para alistamento')."
    )
    
    prompt = ChatPromptTemplate.from_template(system_prompt + "\n\nUsuário: {query}\n\nPerfi:")
    llm = ChatOpenAI(model=MODEL_NAME, api_key=OPENAI_API_KEY, temperature=0.0)
    
    prompt_val = prompt.invoke({"query": query})
    response_msg = await asyncio.to_thread(call_llm_with_retry, llm, prompt_val)
    
    classification = response_msg.content.strip().lower()
    if "servidor" in classification:
         persona = "servidor"
    else:
         persona = "eleitor"
         
    return {"user_persona": persona}
