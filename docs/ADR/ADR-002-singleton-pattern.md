# ADR-002: Singleton para Recursos de IA em Bots de Canal

**Date:** 2026-02-20
**Status:** Accepted

## Context

O bot estava reconectando ao ChromaDB e recarregando todos os modelos
de IA do zero para CADA mensagem recebida. Como acessar disco é uma
operação bloqueante de I/O, isso travava o event loop assíncrono do
Telegram quando chegavam duas mensagens simultâneas ou o PC
engasgava minimamente.

## Decision

ChromaDB, modelos de embedding e LLMs locais SEMPRE inicializados
como Singleton no startup da aplicação (via run_bot.bat), nunca
dentro de handlers de mensagem.

## Alternatives Considered

- **Re-inicializar a cada mensagem:** Descartado. Bloqueia o asyncio e causa instabilidade total sob qualquer carga concorrente.
- **Connection pooling:** Overhead desnecessário para uso local single-user nesta fase.

## Consequences

- **Pros:** Respostas estáveis e rápidas. Event loop não bloqueado. Inicialização ocorre uma única vez no startup.
- **Cons:** Maior uso de RAM enquanto o bot está ativo (aceitável para uso local).

## Rule for Future Projects

O @architect deve verificar este padrão em TODO projeto com a combinação: canal externo (Telegram, WhatsApp, Slack) + modelo local + banco vetorial. É erro de arquitetura garantido se não aplicado.
