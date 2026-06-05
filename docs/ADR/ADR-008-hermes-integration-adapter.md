# ADR-008: Integração Local do Hermes Agent como Gateway Multi-Canal Upstream

**Date:** 2026-05-22  
**Status:** Accepted  
**Deciders:** Diego William (Tech Lead), Antigravity (Squad)

## Context
O projeto `telegram-electoral-agent` utiliza o **LangGraph** como motor de estado para RAG sobre o Manual de Práticas Cartorárias e para o raciocínio soberano do squad. Para simplificar a implantação em múltiplos canais de comunicação (Telegram, Discord, Slack, WhatsApp) sem reescrever conectores ou pollers no core, decidimos adotar o **NousResearch/hermes-agent** como gateway multi-canal upstream, conforme estabelecido no global [ADR-008](../../../_CORE_SKILLS/docs/ADR/agents-ia/ADR-008-hermes-gateway-multicanal.md).

No entanto, para manter a soberania e o isolamento de sessões do LangGraph, precisamos de uma ponte leve de comunicação que integre o Hermes (rodando em WSL2) com o LangGraph (rodando no Windows Host).

## Decision
Fica decidida a criação de um **FastAPI Adapter** local (`src/api.py`) expondo uma API compatível com o padrão OpenAI ChatCompletions (`/v1/chat/completions`) no Windows Host (porta `8123`).

As diretrizes detalhadas da integração são:

### 1. Roteamento de Requisições
* O Hermes Gateway gerencia a sessão externa e faz a requisição de ChatCompletion para o FastAPI local.
* O FastAPI extrai a última mensagem do usuário e o `system_prompt` que contém metadados dinâmicos da plataforma injetados pelo Hermes.

### 2. Isolamento de Sessões via Regex Parser
* Para evitar colisões de memória ou estados entre diferentes usuários do Telegram, o adaptador analisa o `system_prompt` e extrai dinamicamente marcas como `**User:** [username]` ou `**User ID:** [user_id]`.
* Esse valor extraído é usado diretamente como a `thread_id` na chamada ao LangGraph (`MemorySaver`), preservando o histórico e isolamento completo por usuário de forma segura.

### 3. Comunicação WSL2 ➔ Windows Host
* O FastAPI no Windows Host escuta no host `0.0.0.0` para permitir conexões externas da rede virtual do WSL2.
* O Hermes no WSL2 é configurado com a `CUSTOM_BASE_URL` apontando para o IP do gateway WSL (ex: `http://172.x.x.x:8123/v1`), garantindo perfeita bridge de rede virtual.

## Consequences
* **Positivas ✅**:
  * Desacoplamento absoluto entre canais externos (Hermes) e motor de estado (LangGraph).
  * Manutenção soberana das regras de conformidade LGPD e RAG no LangGraph.
  * Compatibilidade transparente com qualquer plataforma futura de chat agregada pelo Hermes.
* **Negativas ❌**:
  * Necessidade de manter dois processos rodando localmente durante o desenvolvimento (FastAPI no Windows + Hermes Gateway no WSL2).
