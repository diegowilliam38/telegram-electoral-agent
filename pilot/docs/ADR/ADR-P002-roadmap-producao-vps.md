# ADR-P002: Roadmap para Piloto em Produção VPS (Docker & pgvector)

- **Status:** ACEITO
- **Data:** 2026-07-23
- **Autor:** @architect & @devops
- **Contexto:** 
  Com as 6 Cognitive Skills validadas e o cérebro do agente atualizado com a legislação de 2026, o objetivo é colocar o `telegram-electoral-agent` em ambiente de produção (Piloto com usuários reais de zonas eleitorais) em VPS (Hostinger / DigitalOcean).

---

## Decisão

Adotar o seguinte roadmap de implantação em produção:

1. **Isolamento de Sessões via Telegram `chat_id`**: Garantir no `bot.py` e `api.py` que o estado do LangGraph seja gerenciado por `thread_id` único baseado no `chat_id`.
2. **Containerização Completa com Docker Compose**:
   - `FastAPI Adapter` (Porta 8123) com auto-restart `unless-stopped`.
   - `Telegram Bot Worker` (Polling/Webhook com Hermes Gateway upstream).
3. **Persistência & Logs de Observabilidade**:
   - Mapear volumes Docker para `data/query_logs.jsonl` e `data/faiss_index`.
   - Suporte para migração opcional para `pgvector`/Supabase via variável de ambiente.
4. **Deploy & Automação via VPS (systemd/docker-compose)**:
   - Configuração de script de deploy `deploy_vps.sh`.

---

## Consequências

- **Alta Disponibilidade:** Bot operando 24/7 com reinicialização automática em caso de queda.
- **Segurança de Sessão:** Zero vazamento de contexto entre conversas de diferentes eleitores ou servidores.
