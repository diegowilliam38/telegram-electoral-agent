# LangGraph Migration Plan

## Goal Description
Refactor the Telegram Electoral Agent to use **LangGraph** instead of raw LangChain chains.
**Why?**
1.  **State Management**: LangGraph handles conversation history natively (`messages` state).
2.  **Async/Sync Control**: Better control over execution steps, preventing the "hangs" seen with the previous bot.
3.  **Debugging**: Steps are discrete and easier to trace than a monolithic chain.
4.  **Scalability**: Easier to add "Human-in-the-loop" or new tools later.

## User Review Required
- [ ] Approval to install `langgraph` dependency.
- [ ] Understanding that conversation history will be managed by the graph state.

## Proposed Changes

### 1. New Dependencies
- `langgraph`
- `langchain-openai` (likely upgrade if needed)

### 2. Architecture: State Graph
We will implement a `StateGraph` with the following structure:
- **State**: `TypedDict` with `messages: Annotated[list[AnyMessage], add_messages]`.
- **Nodes**:
    - `agent`: The LLM that decides to answer or route.
    - `retrieve`: The RAG retrieval step (if explicitly separated) OR as a tool.
- **Edges**:
    - `start` -> `agent`
    - `agent` -> `end`

### 3. Code Modifications

#### [NEW] `src/graph.py`
Defines the LangGraph workflow.
- Imports `StateGraph`, `END`.
- Defines `agent_node` and `tool_node`.
- Compiles the graph into a `Runnable`.

#### [MODIFY] `src/bot.py`
- Replaces `rag_chain` with `graph_app`.
- Updates `handle_message` to use `await graph_app.ainvoke(...)`.
- Passes persistent `thread_id` (Telegram Chat ID) to maintain history.

#### [MODIFY] `src/rag/retrieval.py`
- Refactor `get_rag_chain` to expose the `Retriever` as a **Tool** (`@tool`) for the agent to use.

## Verification Plan
### Automated Tests
- Run `tests/test_graph.py` (new test) to verify the graph responds to inputs.
- Inspect graph visualization (ascii or png) to confirm logic flow.

### Manual Verification
- Deploy bot and test conversation continuity (e.g., "Oi", then "Qual meu nome?" if context was saved, or just RAG specific queries).
