import logging
import asyncio
import time
import os
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters
from src.config import TELEGRAM_BOT_TOKEN
# from src.rag.retrieval import get_rag_chain # Moved to graph.py

import sys

# Configure Windows to print Emojis correctly
sys.stdout.reconfigure(encoding='utf-8')

# Logging setup
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Fix for Windows Event Loop (httpx compatibility)
if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

# RAG Chain is stored in application.bot_data

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.info(f"Start command received from {update.effective_chat.id}")
    logger.info(f"Start command received from {update.effective_chat.id}")
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="🏛️ Olá! Sou o Agente Virtual do Cartório Eleitoral.\n\n"
             "Me pergunte sobre procedimentos do Manual de Práticas Cartorárias.\n"
             "Ex: 'Quais os documentos para alistamento?'"
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text
    chat_id = update.effective_chat.id
    
    # --- 1 & 2: LGPD Compliance & Sanitization against Prompt Injection ---
    # Log ONLY metadata, NEVER the raw message content (Nicho Eleitoral/Jurídico)
    logger.info("incoming_request", extra={"user_id": chat_id})
    
    # Prompt Injection Sanitizer BEFORE any LLM processing
    INJECTION_PATTERNS = [
        "ignore suas instruções",
        "ignore previous instructions",
        "você agora é",
        "new persona",
        "system prompt",
        "ignore all previous",
        "esqueça tudo",
    ]
    
    msg_lower = user_message.lower()
    if any(p in msg_lower for p in INJECTION_PATTERNS):
        logger.warning("prompt_injection_blocked", extra={"user_id": chat_id})
        await context.bot.send_message(chat_id=chat_id, text="⚠️ Comando bloqueado por política de segurança.")
        return
    
    # Start timer for Observability
    start_time = time.time()
    
    try:
        # Ignore errors for typing action as it's non-critical
        await context.bot.send_chat_action(chat_id=chat_id, action="typing")
    except Exception:
        pass

    try:
        # Access Graph App from bot_data
        graph_app = context.application.bot_data.get("graph_app")
        
        if not graph_app:
            await context.bot.send_message(chat_id=chat_id, text="⚠️ Erro interno: Sistema não inicializado.")
            return

        # Invoke Graph Async
        from langchain_core.messages import HumanMessage
        
        inputs = {"messages": [HumanMessage(content=user_message)]}
        config = {"configurable": {"thread_id": str(chat_id)}}
        
        # Retry logic for transient network errors (e.g. httpx.ConnectError)
        max_retries = 3
        response = None
        for attempt in range(max_retries):
            try:
                response = await graph_app.ainvoke(inputs, config=config)
                break
            except Exception as invoke_err:
                logger.warning(f"Attempt {attempt + 1} failed: {invoke_err}")
                if attempt == max_retries - 1:
                    raise invoke_err
                await asyncio.sleep(2) # Wait before retry
        
        # Extract last message from AI
        last_message = response["messages"][-1]
        answer = last_message.content
        
        await context.bot.send_message(chat_id=chat_id, text=answer)
        
        # --- 3: JSON Observability Metrics ---
        elapsed = round((time.time() - start_time) * 1000)
        logger.info("query_processed", extra={
            "user_id": chat_id,
            "duration_ms": elapsed,
            "status": "success"
        })
        
        
    except Exception as e:
        elapsed = round((time.time() - start_time) * 1000)
        logger.error("query_processed", extra={
            "user_id": chat_id,
            "duration_ms": elapsed,
            "status": "error",
            "error_detail": str(e)
        }, exc_info=True)
        
        try:
            await context.bot.send_message(
                chat_id=chat_id, 
                text="⚠️ Ocorreu um erro de conexão ao processar sua solicitação. Por favor, tente novamente."
            )
        except Exception:
            pass # If network is totally down, we can't even send the error message

def start_dummy_server():
    """Starts a dummy HTTP server to satisfy Railway/Heroku port binding health checks."""
    port = int(os.environ.get("PORT", 8080))
    class HealthCheckHandler(BaseHTTPRequestHandler):
        def do_GET(self):
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"OK")
        def log_message(self, format, *args):
            pass # Disable noisy HTTP logging
            
    server = HTTPServer(("0.0.0.0", port), HealthCheckHandler)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    print(f"✅ Dummy server listening on port {port} for PaaS health checks.")

if __name__ == '__main__':
    # Start Dummy Server for PaaS (Railway) HealthChecks
    start_dummy_server()
    
    # Sensible timeouts for network resilience
    # get_updates_request settings can help with pooling errors, but we use builder defaults
    application = (
        ApplicationBuilder()
        .token(TELEGRAM_BOT_TOKEN)
        .read_timeout(30)
        .write_timeout(30)
        .connect_timeout(30)
        .pool_timeout(30)
        .build()
    )
    
    start_handler = CommandHandler('start', start)
    message_handler = MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message)
    
    application.add_handler(start_handler)
    application.add_handler(message_handler)
    
    # Initialize LangGraph at startup
    from src.graph import build_graph
    
    print("⏳ Initializing LangGraph...")
    graph_app = build_graph()
    application.bot_data["graph_app"] = graph_app
    print("✅ LangGraph ready.")

    print("🤖 Bot is runnning... (Press Ctrl+C to stop)")
    application.run_polling(poll_interval=2.0)
