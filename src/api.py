import os
import re
import uuid
import time
import logging
import asyncio
from typing import List, Dict, Any, Optional
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from langchain_core.messages import HumanMessage
from src.graph import build_graph
from src.rag.ingestion import ingest_manual
from src.rag.researcher import reload_retriever

# Setup logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger("electoral_api")

app = FastAPI(title="Telegram Electoral Agent API Adapter", version="1.0.0")

# LangGraph application singleton
graph_app = None

def get_directory_state(directory: str) -> str:
    import glob
    files = glob.glob(os.path.join(directory, "*.pdf"))
    state = []
    for f in sorted(files):
        try:
            mtime = os.path.getmtime(f)
            size = os.path.getsize(f)
            state.append(f"{f}:{mtime}:{size}")
        except OSError:
            pass
    return "|".join(state)

async def directory_watcher_loop():
    logger.info("👀 Starting references directory watcher loop...")
    state_file = os.path.join("data", "last_ingest_state.txt")
    os.makedirs("data", exist_ok=True)
    
    # Delay initial check slightly to let server start smoothly
    await asyncio.sleep(5)
    
    while True:
        try:
            current_state = get_directory_state(os.path.join("docs", "references"))
            
            # Read last state
            last_state = ""
            if os.path.exists(state_file):
                with open(state_file, "r", encoding="utf-8") as f:
                    last_state = f.read().strip()
            
            # If state file is empty, write current state and skip first ingestion to prevent running it unnecessarily on boot
            if not last_state:
                with open(state_file, "w", encoding="utf-8") as f:
                    f.write(current_state)
                last_state = current_state
                
            if current_state != last_state:
                logger.info("🔄 Detected changes in docs/references! Re-running ingestion in background thread...")
                
                # Run ingestion in a separate thread to prevent blocking the async loop
                await asyncio.to_thread(ingest_manual)
                
                # Reload FAISS retriever in memory
                reload_retriever()
                logger.info("✅ Re-ingestion completed and vector store reloaded successfully!")
                
                # Write new state
                with open(state_file, "w", encoding="utf-8") as f:
                    f.write(current_state)
                    
        except Exception as e:
            logger.error(f"Error in directory watcher loop: {e}", exc_info=True)
            
        await asyncio.sleep(10)

def log_interaction(query: str, response_text: str, persona: str, elapsed_time: float, thread_id: str):
    import json
    from datetime import datetime
    
    # Detecção simples de respostas sem conteúdo / inconclusivas baseada nos fallbacks
    lower_resp = response_text.lower()
    is_inconclusive = (
        "inconclusivo" in lower_resp or 
        "não localizei a resposta" in lower_resp or 
        "não encontrou a resposta" in lower_resp or 
        "não consegui encontrar" in lower_resp
    )
    
    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "thread_id": thread_id,
        "query": query,
        "response": response_text,
        "persona": persona,
        "elapsed_seconds": round(elapsed_time, 3),
        "status": "INCONCLUSIVO" if is_inconclusive else "SUCESSO"
    }
    
    log_file = os.path.join("data", "query_logs.jsonl")
    os.makedirs("data", exist_ok=True)
    try:
        with open(log_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(log_entry, ensure_ascii=False) + "\n")
        logger.info(f"💾 Interaction logged to {log_file} with status {log_entry['status']}")
    except Exception as e:
        logger.error(f"Failed to write interaction log: {e}")

@app.on_event("startup")
async def startup_event():
    global graph_app
    logger.info("⏳ Initializing LangGraph Application...")
    try:
        graph_app = build_graph()
        logger.info("✅ LangGraph ready.")
        
        # Start background watcher task
        asyncio.create_task(directory_watcher_loop())
    except Exception as e:
        logger.critical(f"❌ Failed to initialize LangGraph: {e}", exc_info=True)

class ChatMessage(BaseModel):
    role: str
    content: str

class ChatCompletionRequest(BaseModel):
    model: str
    messages: List[ChatMessage]
    temperature: Optional[float] = 0.7
    max_tokens: Optional[int] = None
    stream: Optional[bool] = False

class ChoiceMessage(BaseModel):
    role: str = "assistant"
    content: str

class Choice(BaseModel):
    index: int = 0
    message: ChoiceMessage
    finish_reason: str = "stop"

class Usage(BaseModel):
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0

class ChatCompletionResponse(BaseModel):
    id: str = Field(default_factory=lambda: f"chatcmpl-{uuid.uuid4().hex[:12]}")
    object: str = "chat.completion"
    created: int = Field(default_factory=lambda: int(time.time()))
    model: str
    choices: List[Choice]
    usage: Usage = Field(default_factory=Usage)

def parse_session_from_system_prompt(system_prompt: str) -> str:
    """
    Extracts the session / user identifier from the system prompt injected by Hermes.
    Fallback to a default session key if none found.
    """
    if not system_prompt:
        return "default_session"
        
    # 1. Search for "**User:** user_name" or "**User ID:** user_id"
    user_match = re.search(r"\*\*User\*\*:\s*([^\n\r]+)", system_prompt)
    if user_match:
        val = user_match.group(1).strip()
        # Sanitize spaces for thread_id safety
        return re.sub(r"\s+", "_", val)
        
    user_id_match = re.search(r"\*\*User ID\*\*:\s*([^\n\r]+)", system_prompt)
    if user_id_match:
        val = user_id_match.group(1).strip()
        return re.sub(r"\s+", "_", val)

    # 2. Search for DM with ... or group name in Source
    source_match = re.search(r"\*\*Source\*\*:\s*Telegram\s*\(([^)]+)\)", system_prompt)
    if source_match:
        desc = source_match.group(1).strip()
        # Extract name from "DM with username"
        dm_match = re.search(r"DM with\s+([^\n\r]+)", desc)
        if dm_match:
            return re.sub(r"\s+", "_", dm_match.group(1).strip())
        # Fallback to description
        return re.sub(r"\s+", "_", desc)

    return "default_session"

@app.post("/v1/chat/completions", response_model=ChatCompletionResponse)
async def chat_completions(request: ChatCompletionRequest):
    global graph_app
    if graph_app is None:
        raise HTTPException(status_code=500, detail="LangGraph application not initialized.")

    logger.info(f"Incoming request body JSON: {request.model_dump_json()}")

    # 1. Extract the system prompt and the latest user message
    system_prompt = ""
    user_message = ""
    
    for msg in request.messages:
        if msg.role == "system":
            system_prompt = msg.content
        elif msg.role == "user":
            user_message = msg.content

    if not user_message:
        raise HTTPException(status_code=400, detail="User message is empty.")

    # 2. Determine thread_id
    thread_id = parse_session_from_system_prompt(system_prompt)
    logger.info(f"incoming_request for session thread_id: '{thread_id}'")

    try:
        # 3. Call sovereign LangGraph
        inputs = {"messages": [HumanMessage(content=user_message)]}
        config = {"configurable": {"thread_id": thread_id}}
        
        # Invoke Graph and track duration
        start_time = time.time()
        response = await graph_app.ainvoke(inputs, config=config)
        elapsed_time = time.time() - start_time
        
        # 4. Extract last assistant response and persona
        last_message = response["messages"][-1]
        answer = last_message.content
        persona = response.get("user_persona", "eleitor")

        logger.info(f"query_processed successfully for thread_id: '{thread_id}'. Answer: '{answer}'")
        
        # Log query metadata to file
        log_interaction(user_message, answer, persona, elapsed_time, thread_id)
        
        # 5. Format and return OpenAI completion
        if request.stream:
            import json
            from fastapi.responses import StreamingResponse

            async def event_generator():
                chunk_id = f"chatcmpl-{uuid.uuid4().hex[:12]}"
                created_time = int(time.time())
                
                chunk_data = {
                    "id": chunk_id,
                    "object": "chat.completion.chunk",
                    "created": created_time,
                    "model": request.model,
                    "choices": [
                        {
                            "index": 0,
                            "delta": {
                                "role": "assistant",
                                "content": answer
                            },
                            "finish_reason": None
                        }
                    ]
                }
                yield f"data: {json.dumps(chunk_data, ensure_ascii=False)}\n\n"
                
                stop_chunk = {
                    "id": chunk_id,
                    "object": "chat.completion.chunk",
                    "created": created_time,
                    "model": request.model,
                    "choices": [
                        {
                            "index": 0,
                            "delta": {},
                            "finish_reason": "stop"
                        }
                    ]
                }
                yield f"data: {json.dumps(stop_chunk, ensure_ascii=False)}\n\n"
                yield "data: [DONE]\n\n"
                
            logger.info("Returning StreamingResponse (text/event-stream) for streaming request.")
            return StreamingResponse(event_generator(), media_type="text/event-stream")

        resp_data = ChatCompletionResponse(
            model=request.model,
            choices=[
                Choice(
                    index=0,
                    message=ChoiceMessage(content=answer)
                )
            ]
        )
        logger.info(f"Returning response JSON: {resp_data.model_dump_json()}")
        return resp_data

    except Exception as e:
        logger.error(f"query_processed error for thread_id '{thread_id}': {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health():
    return {"status": "ok", "langgraph_initialized": graph_app is not None}
