import asyncio
from tenacity import retry, stop_after_attempt, wait_exponential
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import AIMessage, HumanMessage
from src.config import DB_DIR, OPENAI_API_KEY, MODEL_NAME, EMBEDDING_MODEL, COLLECTION_NAME

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
def call_llm_with_retry(llm, prompt_val):
    return llm.invoke(prompt_val)

_embeddings = OpenAIEmbeddings(model=EMBEDDING_MODEL, api_key=OPENAI_API_KEY)
_vector_store = FAISS.load_local(
    folder_path=DB_DIR,
    embeddings=_embeddings,
    allow_dangerous_deserialization=True
)
_retriever = _vector_store.as_retriever(search_kwargs={"k": 8})

def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)

async def node_researcher(state):
    messages = state["messages"]
    last_message = messages[-1]
    if not isinstance(last_message, HumanMessage):
        return {"messages": []}
    
    query = last_message.content
    
    # RAG Retrieval - Reverting to synchronous thread because httpx async drops connections
    def fetch_docs(q):
        return _retriever.invoke(q)
        
    docs = await asyncio.to_thread(fetch_docs, query)
    context_text = format_docs(docs)

    persona = state.get("user_persona", "eleitor")
    
    if persona == "servidor":
        system_prompt = (
            "Você é um Pesquisador Técnico do Tribunal Regional Eleitoral.\n"
            "REGRAS DE OURO:\n"
            "1. PRIORIDADE MÁXIMA: Para assuntos de 'Gestão de Cadastro', alistamento, transferência, revisão ou eleitor suspenso, a norma soberana é a 'Resolução TSE nº 23.659/2021'. Ela anula qualquer conflito com apostilas antigas.\n"
            "2. Atenção Crítica: NUNCA confunda 'Suspensão de Direitos Políticos' com 'Cancelamento' ou 'Perda'. A suspensão (Art. 11, § 1º) NÃO IMPEDE operações de cadastro (alistamento, transferência, revisão). Já o Cancelamento/Perda tem regras restritivas severas.\n"
            "3. Apenas extraia a resposta literal da base de conhecimento fornecida.\n"
            "4. Você DEVE citar explicitamente a Norma, Artigo, Página ou Seção de onde tirou a informação.\n"
            "5. Nunca invente, presuma ou una artigos diferentes se contradizendo. Responda apenas com base no Contexto.\n"
            "6. Não seja cordial, não use saudações.\n"
            "7. Se a resposta não estiver clara no Contexto fornecido, responda APENAS: INCONCLUSIVO.\n"
            "\n\nContexto fornecido:\n{context_text}"
        )
    else:
        # Eleitor mode: Hyper-focus on 23.659/2021 (Gestão de Cadastro) as requested by the user
        system_prompt = (
            "Você é um Pesquisador Técnico do Tribunal Regional Eleitoral atuando na triagem para Cidadãos.\n"
            "REGRAS DE OURO OBRIGATÓRIAS:\n"
            "1. FOCO EXCLUSIVO: Ao tratar de dúvidas do cidadão (Local de Votação, Título, Biometria, Transferência, Multas), baseie-se QUASE QUE EXCLUSIVAMENTE na 'Resolução TSE nº 23.659/2021' (Gestão de Cadastro) contida no Contexto. Ela é a regra definitiva para o Eleitor.\n"
            "2. Atenção Crítica: NUNCA confunda 'Suspensão de Direitos Políticos' com 'Cancelamento' ou 'Perda'. A suspensão (Art. 11, § 1º) NÃO IMPEDE operações de cadastro (alistamento, transferência, revisão). Já o Cancelamento/Perda tem regras restritivas severas.\n"
            "3. Ignore jargões processuais avançados (Códigos ASE complexos, prazos de recursos de partidos) se eles aparecerem no Contexto. Foque apenas na resposta processual que resolve a dor do eleitor.\n"
            "4. Extraia a resposta literal do Contexto e cite o Artigo, mas sem formalismos exagerados.\n"
            "5. Não seja cordial, não use saudações. Você é uma máquina de extração.\n"
            "6. Se a resposta não estiver clara no Contexto fornecido, responda APENAS: INCONCLUSIVO.\n"
            "\n\nContexto fornecido:\n{context_text}"
        )
    
    prompt = ChatPromptTemplate.from_template(system_prompt + "\n\nPergunta do usuário: {query}")
    llm = ChatOpenAI(model=MODEL_NAME, api_key=OPENAI_API_KEY, temperature=0.0)
    
    # Using resilience (retry) to prevent micro drops
    prompt_val = prompt.invoke({"context_text": context_text, "query": query})
    response_msg = await asyncio.to_thread(call_llm_with_retry, llm, prompt_val)
    
    ai_message = AIMessage(content=response_msg.content, name="Researcher")
    
    return {
        "messages": [ai_message],
        "context_docs": context_text
    }
