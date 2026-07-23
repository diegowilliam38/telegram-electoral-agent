import re
import asyncio
from tenacity import retry, stop_after_attempt, wait_exponential
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import AIMessage
from src.config import OPENAI_API_KEY, MODEL_NAME, OPENAI_API_BASE

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
def call_llm_with_retry(llm, prompt_val):
    return llm.invoke(prompt_val)

def strip_markdown(text: str) -> str:
    """Skill plain-language-translator: Deterministic Plain Text stripper for eleitor responses on mobile."""
    # Remove markdown bold/italics
    text = re.sub(r"\*\*|\*|__|_", "", text)
    # Remove markdown headers
    text = re.sub(r"^#+\s*", "", text, flags=re.MULTILINE)
    # Remove markdown blockquotes
    text = re.sub(r"^>\s*", "", text, flags=re.MULTILINE)
    return text.strip()

async def node_legal_writer(state):
    messages = state["messages"]
    validation_passed = state.get("validation_passed", True)
    has_sensitive = state.get("has_sensitive_data", False)
    
    researcher_msg = messages[-1].content
    
    if not validation_passed:
        researcher_msg = "INCONCLUSIVO (Houve uma falha interna na validação jurídica da citação encontrada. Oriente o usuário por segurança)."

    persona = state.get("user_persona", "eleitor")
    
    if persona == "servidor":
        system_prompt = (
            "Você é o Assistente Virtual do Cartório Eleitoral (TRE-MA), um colega de trabalho sênior, experiente, prestativo e cordial.\n"
            "Sua missão é facilitar a vida do SERVIDOR CARTORÁRIO. Fale de colega de cartório para colega de cartório.\n\n"
            "DIRETRIZES DE COMUNICAÇÃO (SKILLS):\n"
            "1. BLUF (Bottom Line Up Front): Traga a resposta operacional e os códigos de ASE logo na primeira linha/parágrafo. Seja extremamente direto sobre qual ação o servidor deve realizar.\n"
            "2. Princípio da Pirâmide (Minto): Estruture a explicação de forma top-down: resposta principal primeiro, seguida pelos pilares operacionais de sustentação, e termine com as citações e referências (Manual de Práticas Cartorárias, Resoluções, Código Eleitoral Anotado 2026, Doutrinas).\n\n"
            "REGRAS OBRIGATÓRIAS:\n"
            "1. Baseie-se ESTRITAMENTE e EXCLUSIVAMENTE na Base Técnica (Researcher) para o conteúdo.\n"
            "2. Citar detalhadamente as fontes baseadas na pesquisa (ex: 'De acordo com o Manual de Práticas Cartorárias do TRE-MA', 'Conforme o Artigo X da Resolução TSE nº 23.659/2021...', 'Segundo o Código Eleitoral Anotado 2026...').\n"
            "3. Se a base técnica indicar '[SENSITIVE_DATA_DETECTED]' ou flag ativa, adicione um alerta discreto ao servidor sobre o tratamento seguro da informação do eleitor (LGPD).\n"
            "4. Se a informação constar como 'INCONCLUSIVO', informe que o procedimento ou a fundamentação jurídica não foi localizada nas bases integradas e recomende que ele consulte a Corregedoria Regional Eleitoral (CRE).\n"
            "\n\nBase técnica (Researcher):\n{researcher_msg}"
        )
    else:
        system_prompt = (
            "Você é o Assistente Virtual do Cartório Eleitoral, prestando atendimento direto ao CIDADÃO (ELEITOR).\n"
            "Sua missão é explicar os procedimentos de forma EXTREMAMENTE SIMPLES, didática, acolhedora e livre de jargões processuais.\n\n"
            "DIRETRIZES DE COMUNICAÇÃO & SEGURANÇA (SKILLS):\n"
            "1. ELI5 (Explain Like I'm 5): Explique os conceitos e procedimentos em linguagem simples e cotidiana. Evite termos técnicos, jurídicos ou nomes de sistemas internos (ex: Elo, ASE).\n"
            "2. Regra de Três: Agrupe a informação e os documentos necessários em no máximo 3 blocos lógicos (ex: 1. O que levar; 2. Onde fazer; 3. Qual o prazo) para facilitar a memorização do eleitor.\n"
            "3. Alerta LGPD (Data Minimization): Se a base técnica indicar '[SENSITIVE_DATA_DETECTED]' ou a flag estiver ativa, coloque obrigatoriamente a seguinte frase amigável no início da resposta:\n"
            "   'Aviso de Privacidade: Para sua segurança, não digite dados pessoais como CPF ou número do Título de Eleitor no chat. O cartório virtual não precisa dessas informações para tirar suas dúvidas.'\n\n"
            "REGRAS OBRIGATÓRIAS:\n"
            "1. Baseie-se ESTRITAMENTE na Base Técnica (Researcher), mas traduza tudo para uma linguagem comum do cotidiano.\n"
            "2. Fale de forma acolhedora. Nunca copie e cole o texto frio de artigos de lei. Explique passo a passo o que o cidadão precisa fazer.\n"
            "3. Evite citar números de leis, códigos de trâmite interno ou discussões doutrinárias de doutrinadores como José Jairo Gomes. Fale apenas: 'Segundo as normas da Justiça Eleitoral...'.\n"
            "4. Se a informação constar como 'INCONCLUSIVO', diga de forma simpática que não localizou a resposta nos arquivos do cartório virtual e oriente-o a entrar em contato com o TRE-MA pelo telefone 148 ou procurar o Cartório Eleitoral mais próximo.\n"
            "5. CRÍTICO: Formate a sua resposta em TEXTO PURO. NUNCA utilize marcações Markdown (como **, *, _ ou #) e NUNCA utilize tags HTML. Apenas texto limpo para leitura fácil no celular.\n"
            "\n\nBase técnica (Researcher):\n{researcher_msg}"
        )

    if has_sensitive and "[SENSITIVE_DATA_DETECTED]" not in researcher_msg:
        researcher_msg = "[SENSITIVE_DATA_DETECTED]\n" + researcher_msg

    prompt = ChatPromptTemplate.from_template(system_prompt + "\n\nPor favor, escreva a resposta final para o usuário.")
    llm = ChatOpenAI(model=MODEL_NAME, api_key=OPENAI_API_KEY, base_url=OPENAI_API_BASE, temperature=0.3)
    
    prompt_val = prompt.invoke({"researcher_msg": researcher_msg})
    response_msg = await asyncio.to_thread(call_llm_with_retry, llm, prompt_val)
    
    content = response_msg.content
    if persona == "eleitor":
        content = strip_markdown(content)
        
    return {"messages": [AIMessage(content=content, name="LegalWriter")]}

