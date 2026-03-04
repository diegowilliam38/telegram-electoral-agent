# Project Rules: Telegram Agent & RAG

## 1. Environment & Dependencies
- **Always use Virtual Environments (`.venv`)**: Prevents "module not found" and global conflicts.
- **Dependency Pinning**: Use exact versions for `langchain`, `pydantic`, `httpx` to avoid breaking changes (like LangChain 0.2 vs 0.3).
- **Avoid Meta-Packages**: Prefer `langchain-core` + `langchain-community` over the huge `langchain` package if possible.

## 2. Windows Compatibility
- **Async Event Loop**: On Windows, ALWAYS set `asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())` if using `httpx` or `python-telegram-bot`.
- **File Paths**: Use `os.path.join()` or `pathlib`. Never hardcode `/` or `\`.

## 3. Bot Architecture
- **No Global Variables**: Use `context.bot_data` or `context.user_data` to store state (DB connections, RAG chains).
- **Async RAG**: Use `await chain.ainvoke()` instead of `chain.invoke()` inside async handlers to prevent blocking the heartbeat.
- **Timeouts**: Increase `read_timeout` and `connect_timeout` in `ApplicationBuilder` to >30s for LLM-based bots.

## 4. Security
- **API Keys**: Never commit keys. Use `.env`.
- **Logging**: Do not log full message content in production (privacy).
