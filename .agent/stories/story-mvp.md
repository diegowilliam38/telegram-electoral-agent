# Task: Telegram Electoral Agent Development
**Goal**: Build an MVP RAG agent for the TRE-MA manual.

## 1. Environment Setup
- [ ] Initialize Python venv and install dependencies (`langchain`, `chromadb`, `python-telegram-bot`, `openai`, `pypdf`, `python-dotenv`)
- [ ] Setup `.env` file with `OPENAI_API_KEY` and `TELEGRAM_BOT_TOKEN`.

## 2. Data Ingestion (The Brain)
- [ ] Create `src/rag/ingestion.py`.
- [ ] Implement PDF loading (`PyPDFLoader`).
- [ ] Implement Text Splitting (`RecursiveCharacterTextSplitter`).
- [ ] Implement Vector Store creation (`ChromaDB`).

## 3. RAG Logic (The Mind)
- [ ] Create `src/rag/retrieval.py`.
- [ ] Setup Retrieval Chain.
- [ ] Design System Prompt (Persona: Especialista Eleitoral).

## 4. Telegram Interface (The Mouth)
- [ ] Create `src/bot.py`.
- [ ] Implement `/start` handler.
- [ ] Implement message handler (connects to RAG chain).

## 5. Testing & Verification
- [ ] Verify if the bot answers correctly referencing the manual.
- [ ] Test edge cases ("How to make a cake?" -> "I only know about electoral procedures").
