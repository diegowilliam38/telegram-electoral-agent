# Briefing do Piloto: Agente Eleitoral Telegram

## Objetivo do Piloto

Validar o agente jurídico eleitoral com usuários reais de outras zonas eleitorais. Coletar feedback sobre qualidade das respostas, estabilidade e usabilidade.

## Perfil dos Usuários

- Servidores de zonas eleitorais.
- Consultam o manual de práticas cartorárias eleitorais frequentemente.
- Múltiplos usuários simultâneos de locais diferentes.

## Restrições Identificadas

- **ChromaDB local não funciona em ambiente de servidor:** O sistema de arquivos pode ser efêmero, e o SQLite concorrente não é ideal para nuvem escalável.
- **Uptime contínuo:** Bot precisa operar 24/7 sem intervenção manual.
- **Isolamento de sessão:** Múltiplas sessões simultâneas de usuários diferentes requerem que o estado do LangGraph seja isolado por `chat_id`.
- **Observabilidade:** Necessidade de logs centralizados para debug remoto sem acesso local à máquina física.

## Métricas de Sucesso do Piloto

1. Bot responde corretamente perguntas do manual.
2. Uptime > 95% durante o período de teste.
3. Tempo de resposta < 30 segundos por query.
4. Zero vazamento de dados entre sessões de usuários diferentes.

## Infraestrutura Alvo

**VPS Real (Hostinger ou equivalente) com controle total**
*Razão:* Necessidade de persistência de disco, acesso SSH para gestão, uso de `systemd` para restart automático em falhas, e armazenamento de logs centralizados.
