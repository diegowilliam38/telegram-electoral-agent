import os
import sys
import shutil
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings
import tiktoken
from src.config import DOCS_DIR, DB_DIR, OPENAI_API_KEY, EMBEDDING_MODEL, COLLECTION_NAME

sys.stdout.reconfigure(encoding='utf-8')

def ingest_manual():
    print(f"🚀 Starting Ingestion Process...")
    
    pdf_files = [f for f in os.listdir(DOCS_DIR) if f.endswith('.pdf')]
    if not pdf_files:
        print(f"❌ Error: No PDFs found in {DOCS_DIR}")
        return

    documents = []
    for pdf_file in pdf_files:
        pdf_path = os.path.join(DOCS_DIR, pdf_file)
        print(f"📖 Loading PDF: {pdf_path}...")
        loader = PyPDFLoader(pdf_path)
        documents.extend(loader.load())
        
    print(f"✅ Loaded {len(documents)} pages in total.")

    # 2. Split Text (Refatorado conforme ADR-004 para Documentos Jurídicos)
    print("✂️ Splitting text into chunks based on semantic hierarchy...")
    separators = ["\nArt.", "\nCapítulo", "\nSeção", "\nTítulo", "\n\n", "\n"]
    text_splitter = RecursiveCharacterTextSplitter(
        separators=separators,
        chunk_size=600,
        chunk_overlap=100,
        length_function=len,
        is_separator_regex=False,
    )
    chunks = text_splitter.split_documents(documents)
    print(f"✅ Created {len(chunks)} semantic chunks.")

    # 3. Create Vector Store
    print(f"💾 Creating Vector Store in {DB_DIR}...")
    
    # We will NOT use shutil.rmtree() because ChromaDB SQLite locks the file on Windows and causes WinError 5.
    # Instead, we define the Client and Reset it if allowed, or just trust Chroma to ingest over it.
    
    # Filter out abnormally large chunks that exceed the embedding model context limit
    # The limit is 8192 tokens. We'll use 8000 tokens as the exact heuristic using tiktoken.
    try:
        encoding = tiktoken.encoding_for_model(EMBEDDING_MODEL)
    except KeyError:
        encoding = tiktoken.get_encoding("cl100k_base")
        
    safe_chunks = []
    for chunk in chunks:
        if len(encoding.encode(chunk.page_content)) < 8000:
            safe_chunks.append(chunk)
            
    filtered_count = len(chunks) - len(safe_chunks)
    print(f"🧹 Filtered {filtered_count} chunks that were too large for embeddings.")
    
    embeddings = OpenAIEmbeddings(model=EMBEDDING_MODEL, api_key=OPENAI_API_KEY)
    
    vector_store = FAISS.from_documents(
        documents=safe_chunks,
        embedding=embeddings
    )
    
    os.makedirs(DB_DIR, exist_ok=True)
    vector_store.save_local(DB_DIR)
    
    print(f"🎉 Ingestion Complete! Vector DB is ready.")

if __name__ == "__main__":
    ingest_manual()
