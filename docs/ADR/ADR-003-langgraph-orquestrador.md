# ADR-003: LangGraph como Orquestrador de Agentes Complexos

**Date:** 2026-02-20
**Status:** Accepted

## Context

O projeto foi iniciado com LangChain. A integração com Telegram apresentou instabilidade persistente porque LangChain assume fluxo linear (chains). Integrações com canais externos exigem controle explícito de estado entre turnos, lógica condicional, retry e memória de sessão por usuário — padrões incompatíveis com arquitetura de cadeia linear.

## Decision

Usar LangGraph como orquestrador de agentes em qualquer projeto com integração de canal externo. LangChain fica restrito a pipelines simples sem estado persistente entre turnos de conversa.

## Alternatives Considered

- **LangChain puro:** Tentado. Falhou em integração com Telegram por ausência de controle de estado entre mensagens.
- **n8n para lógica do agente:** Adequado para automação de workflows lineares, não para lógica de agente com estados cíclicos e memória contextual.

## Consequences

- **Pros:** Controle explícito de estado via grafos. Suporte nativo a fluxos cíclicos. Compatível com asyncio. Permite nós especializados (intent, RAG, resposta, erro).
- **Cons:** Curva de aprendizado maior que LangChain. Menos exemplos públicos disponíveis.

## Rule for Future Projects

O @architect deve propor LangGraph por padrão em qualquer projeto com: canal externo + agente conversacional + memória de sessão.
