import asyncio
from tenacity import retry, stop_after_attempt, wait_exponential
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import AIMessage, HumanMessage
from src.config import DB_DIR, OPENAI_API_KEY, MODEL_NAME, EMBEDDING_MODEL, COLLECTION_NAME, OPENAI_API_BASE

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
def call_llm_with_retry(llm, prompt_val):
    return llm.invoke(prompt_val)

_embeddings = None
_vector_store = None
_retriever = None

def get_retriever():
    global _embeddings, _vector_store, _retriever
    if _retriever is None:
        _embeddings = OpenAIEmbeddings(model=EMBEDDING_MODEL, api_key=OPENAI_API_KEY, base_url=OPENAI_API_BASE)
        _vector_store = FAISS.load_local(
            folder_path=DB_DIR,
            embeddings=_embeddings,
            allow_dangerous_deserialization=True
        )
        _retriever = _vector_store.as_retriever(search_kwargs={"k": 20})
    return _retriever

def reload_retriever():
    global _embeddings, _vector_store, _retriever
    _embeddings = None
    _vector_store = None
    _retriever = None
    get_retriever()

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
        return get_retriever().invoke(q)
        
    docs = await asyncio.to_thread(fetch_docs, query)
    context_text = format_docs(docs)

    persona = state.get("user_persona", "eleitor")
    
    if persona == "servidor":
        system_prompt = (
            "Você é um Pesquisador Técnico do Tribunal Regional Eleitoral, focado em subsidiar um Assistente de Cartório Eleitoral.\n"
            "Sua função é ler o contexto e extrair os fatos com precisão cirúrgica.\n"
            "FONTES DISPONÍVEIS NO CONTEXTO:\n"
            "1. Manual de Práticas Cartorárias do TRE-MA (e anexos de ASE/Cadastro): Rotinas operacionais, códigos ASE (ex: suspensão, restabelecimento), procedimentos de balcão e de sistemas (Elo).\n"
            "2. Resolução TSE nº 23.659/2021: Gestão de Cadastro Eleitoral, alistamento, transferência, revisão, biometria.\n"
            "3. Código Eleitoral (Lei nº 4.737/1965) e Lei das Eleições (Lei nº 9.504/1997): Legislação federal, prazos processuais e partidários, crimes.\n"
            "4. Doutrina de Direito Eleitoral (José Jairo Gomes / Esquematizado): Conceitos doutrinários, interpretações teóricas, elegibilidade, direitos políticos.\n\n"
            "REGRAS DE OURO:\n"
            "1. PRIORIDADE MÁXIMA: Para assuntos de 'Gestão de Cadastro', alistamento, transferência, revisão ou eleitor suspenso, a norma soberana é a 'Resolução TSE nº 23.659/2021'. Ela anula qualquer conflito com apostilas antigas.\n"
            "2. ATENÇÃO CRÍTICA: NUNCA confunda 'Suspensão de Direitos Políticos' com 'Cancelamento' ou 'Perda'. A suspensão (Art. 11, § 1º) NÃO IMPEDE operações de cadastro (alistamento, transferência, revisão). Já o Cancelamento/Perda tem regras restritivas severas.\n"
            "3. Citação obrigatória: Você DEVE citar explicitamente a fonte (ex: 'Manual de Práticas Cartorárias', 'Art. X da Resolução TSE nº 23.659/2021', 'Doutrina de José Jairo Gomes') de onde tirou cada informação.\n"
            "4. Apenas extraia a resposta literal da base de conhecimento fornecida. Não invente nem presuma nada.\n"
            "5. Não seja cordial, não use saudações. Seja direto e focado nos fatos e fundamentos.\n"
            "6. Se a resposta não estiver clara no Contexto fornecido, responda APENAS: INCONCLUSIVO.\n"
            "7. SEGURANÇA (LGPD): Se a pergunta do usuário contiver dados reais expostos (como CPF, título de eleitor ou RG), insira no topo do relatório: '[SENSITIVE_DATA_DETECTED]'.\n"
            "\n\nContexto fornecido:\n{context_text}"
        )
    else:
        system_prompt = (
            "Você é um Pesquisador Técnico do Tribunal Regional Eleitoral atuando na triagem para Cidadãos/Eleitores.\n"
            "Sua função é extrair do contexto as orientações práticas de forma objetiva, priorizando o que interessa ao eleitor comum.\n"
            "FONTES DE INTERESSE:\n"
            "- Resolução TSE nº 23.659/2021 (Cadastro, biometria, transferência)\n"
            "- Manual de Práticas Cartorárias (Procedimentos básicos de atendimento)\n\n"
            "REGRAS DE OURO:\n"
            "1. FOCO EXCLUSIVO: Ao tratar de dúvidas do cidadão (Local de Votação, Título, Biometria, Transferência, Multas), baseie-se na 'Resolução TSE nº 23.659/2021' ou nos procedimentos do 'Manual de Práticas'.\n"
            "2. ATENÇÃO CRÍTICA: NUNCA confunda 'Suspensão de Direitos Políticos' com 'Cancelamento' ou 'Perda'. A suspensão (Art. 11, § 1º) NÃO IMPEDE operações de cadastro (alistamento, transferência, revisão).\n"
            "3. Simplificação de dados: Ignore jargões processuais avançados (Códigos ASE complexos, termos em latim, discussões acadêmicas de doutrina) no contexto. Foque apenas em extrair as regras e requisitos do cidadão.\n"
            "4. Extraia a resposta literal do Contexto e cite o artigo ou regra correspondente de forma discreta.\n"
            "5. Não seja cordial, não use saudações.\n"
            "6. Se a resposta não estiver clara no Contexto fornecido, responda APENAS: INCONCLUSIVO.\n"
            "7. SEGURANÇA (LGPD): Se a pergunta do usuário contiver dados reais expostos (como CPF, título de eleitor ou RG), insira no topo do relatório: '[SENSITIVE_DATA_DETECTED]'.\n"
            "\n\nContexto fornecido:\n{context_text}"
        )
    
    prompt = ChatPromptTemplate.from_template(system_prompt + "\n\nPergunta do usuário: {query}")
    llm = ChatOpenAI(model=MODEL_NAME, api_key=OPENAI_API_KEY, base_url=OPENAI_API_BASE, temperature=0.0)
    
    # Using resilience (retry) to prevent micro drops
    prompt_val = prompt.invoke({"context_text": context_text, "query": query})
    response_msg = await asyncio.to_thread(call_llm_with_retry, llm, prompt_val)
    
    ai_message = AIMessage(content=response_msg.content, name="Researcher")
    
    return {
        "messages": [ai_message],
        "context_docs": context_text
    }
