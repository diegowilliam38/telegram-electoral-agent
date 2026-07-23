# Spec Técnica: Preparação de Produção & Docker Compose para VPS

**ID:** `STORY-PILOT-001`
**Autor:** `@devops` / `@architect`
**Status:** `READY_FOR_DEV`

---

## 1. Escopo Técnico

1. **Ajuste de Conteinerização (`docker-compose.yml` & `Dockerfile`)**:
   - Atualizar `docker-compose.yml` para expor o serviço FastAPI (porta `8123`) e o bot do Telegram como réplicas independentes com reinicialização automática (`restart: always`).
   - Mapear volumes persistentes para `data/` (logs e vetores).

2. **Isolamento de Sessão por Chat ID**:
   - Garantir em `src/bot.py` e `src/api.py` a passagem do `chat_id` como `thread_id` único no LangGraph `state`.

3. **Script de Deploy Automatizado (`deploy_vps.sh`)**:
   - Script shell para automação do build e subida na VPS via SSH.

---

## 2. Critérios BINÁRIOS de Aceite (Passa / Falha)

- [ ] **Passa/Falha 1:** `docker-compose config` valida sem erros de sintaxe.
- [ ] **Passa/Falha 2:** Múltiplas chamadas simultâneas com `chat_id` diferentes mantêm isolamento absoluto de mensagens.
- [ ] **Passa/Falha 3:** `deploy_vps.sh` criado com permissões de execução.
