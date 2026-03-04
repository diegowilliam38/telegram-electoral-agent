import asyncio
from tenacity import retry, stop_after_attempt, wait_exponential
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import AIMessage
from src.config import OPENAI_API_KEY, MODEL_NAME

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
def call_llm_with_retry(llm, prompt_val):
    return llm.invoke(prompt_val)

async def node_legal_writer(state):
    messages = state["messages"]
    validation_passed = state.get("validation_passed", True)
    
    researcher_msg = messages[-1].content
    
    if not validation_passed:
        researcher_msg = "INCONCLUSIVO (Houve uma falha interna na validação jurídica da citação encontrada. Oriente o usuário por segurança)."

    persona = state.get("user_persona", "eleitor")
    
    if persona == "servidor":
        system_prompt = (
            "Você é o Assistente Virtual do TRE-MA, um colega de trabalho prestativo e cordial.\n"
            "Sua missão é facilitar a vida do SERVIDOR CARTORÁRIO. Fale de colega para colega.\n"
            "REGRAS OBRIGATÓRIAS:\n"
            "1. Baseie-se ESTRITAMENTE e EXCLUSIVAMENTE na Base Técnica (Researcher) para o conteúdo.\n"
            "2. Cite Normas, Artigos, Códigos ASE e jargões abertamente, garantindo precisão jurídica extrema.\n"
            "3. Se a informação constar como 'INCONCLUSIVO', diga que não encontrou a resposta nos manuais para garantir segurança jurídica e oriente elevar a dúvida à Corregedoria.\n"
            "\n\nBase técnica (Researcher):\n{researcher_msg}"
        )
    else:
        system_prompt = (
            "Você é o Assistente Virtual do TRE-MA, projetado para orientar o CIDADÃO (ELEITOR).\n"
            "Sua missão é explicar os procedimentos de forma EXTREMAMENTE SIMPLES, didática e livre de jargões processuais.\n"
            "REGRAS OBRIGATÓRIAS:\n"
            "1. Baseie-se ESTRITAMENTE na Base Técnica (Researcher), mas traduza tudo para uma linguagem comum.\n"
            "2. Fale de forma acolhedora. Nunca copie e cole o texto frio do Artigo. Explique o que o cidadão precisa FAZER e QUAIS DOCUMENTOS ele precisa levar.\n"
            "3. Evite citar números gigantes de leis, cite apenas se for indispensável para ele (ex: 'Segundo as normas da Justiça Eleitoral...').\n"
            "4. Se a informação constar como 'INCONCLUSIVO', diga gentilmente que o Assistente não encontrou a resposta no banco de dados e oriente o cidadão a ligar para o número 148 do TRE-MA ou ir ao cartório.\n"
            "5. CRÍTICO: Formate a sua resposta em TEXTO PURO. NUNCA utilize marcações Markdown (como **, *, _ ou #) e NUNCA utilize tags HTML. Apenas texto limpo para leitura fácil no celular.\n"
            "\n\nBase técnica (Researcher):\n{researcher_msg}"
        )

    prompt = ChatPromptTemplate.from_template(system_prompt + "\n\nPor favor, escreva a resposta final para o usuário.")
    llm = ChatOpenAI(model=MODEL_NAME, api_key=OPENAI_API_KEY, temperature=0.3)
    
    prompt_val = prompt.invoke({"researcher_msg": researcher_msg})
    response_msg = await asyncio.to_thread(call_llm_with_retry, llm, prompt_val)
    
    return {"messages": [AIMessage(content=response_msg.content, name="LegalWriter")]}
