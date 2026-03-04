# ADR-P001: Arquitetura para Piloto com Usuários Reais

**Date:** 2026-02-20
**Status:** Accepted

## Context

O projeto entrará em fase piloto com servidores externos. A infraestrutura local baseada em execução `.bat` e banco vetorial ChromaDB gravado em disco não suporta operação 24/7, nem a concorrência inerente a múltiplos usuários simultâneos no Telegram.

## Decision

Para viabilizar o piloto, implementaremos as seguintes mudanças arquiteturais isoladas neste subprojeto:

1. **Migração do Banco Vetorial:**
   - ChromaDB local será substituído por **pgvector no Supabase**.
   - *Motivo:* Supabase já é validado no ecossistema (ex: EduconnectAI), suporta conexões escaláveis, resolve a limitação do sistema de arquivos de servidores cloud, e já havia sido documentado como alternativa superior no ADR-001 do projeto base.

2. **Gestão de Sessões por Usuário:**
   - Implementar uso rigoroso do `thread_id` mapeado para o `chat_id` do Telegram no controlador do LangGraph.
   - *Motivo:* Respostas e histórico (MemorySaver ou equivalente em DB) não podem vazar entre servidores eleitorais diferentes consultando o mesmo bot.

3. **Deploy em VPS Real:**
   - Uso de `systemd` para daemonize do processo e gerenciar auto-restart.
   - Definição clara de configuração baseada no pacote `python-dotenv`.
   - *Motivo:* Garante o uptime exigido pela métrica de sucesso sem necessidade de PC local.

4. **Monitoramento do Piloto:**
   - Criação de loggers que gravem em arquivos com rotatividade (rotating file logs).
   - Logar queries recebidas (protegendo dados PII se houver) e registrar stack traces completos de falhas.

## Plano de Migração em Fases

- **Fase 1:** Migração do banco vetorial (ChromaDB → pgvector)
- **Fase 2:** Adaptação do código para VPS (systemd, logs, .env)
- **Fase 3:** Deploy e testes internos antes de abrir para colegas
- **Fase 4:** Piloto real com usuários + coleta de feedback

## Rule for Future Projects

Estas decisões são herdadas do cenário de "Passagem de MVP local para Nuvem". O @architect deve utilizar este blueprint para todos os agentes do ecossistema que saírem da fase de experimentação local para teste real.
