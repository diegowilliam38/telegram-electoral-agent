# Agente Telegram: Cartório Eleitoral 🗳️

**Objetivo**: Consultas sobre procedimentos cartorários eleitorais via Telegram.
**Base de Conhecimento**: Manual de Práticas Cartorárias (TSE).

## Estrutura do Projeto
- `docs/references/`: Coloque o PDF do manual aqui.
- `docs/PRD.md`: Requisitos do Produto (A ser preenchido pelo @analyst).
- `src/`: Código do bot (Python/Telethon ou python-telegram-bot).

## Como Rodar
1. Instale dependências: `pip install -r requirements.txt`
2. Configure `.env` com `TELEGRAM_TOKEN`.
3. Execute: `python src/main.py`.
