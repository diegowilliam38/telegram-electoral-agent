# Story: Fase 2 — Adaptação do Código para VPS e Múltiplos Usuários

## Objetivo

Preparar o código fonte para as exigências de um servidor 24/7 sem interface de desenvolvimento e para o acesso simultâneo de vários servidores de cartório.

## Critérios de Aceite

- [ ] Modificar `bot.py` para garantir que o `thread_id` passado ao LangGraph seja firmemente restrito e atrelado ao `chat_id` do usuário.
- [ ] Implementar sistema de logs rotativos no disco (`logging.handlers.TimedRotatingFileHandler`) coletando erros, warnings e acessos básicos.
- [ ] Criar arquivo de instrução de serviço Systemd (`telegram-electoral-agent.service`).
- [ ] Garantir que o bot não trave ao receber 5 mensagens de 5 usuários ao mesmo tempo (comprovar paralelismo nativo na chamada do LangGraph).

## Dependências

- Conclusão da Fase 1 (banco na nuvem garante que o RAG não dará gargalo de file lock).
