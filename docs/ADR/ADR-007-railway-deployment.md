# ADR-007: Deploy em Plataforma PaaS (Railway) e Sanitização Extrema de Variáveis

**Date:** 2026-03-04
**Status:** Accepted

## Context

Durante a tentativa de deploy de produção do `telegram-electoral-agent` na nuvem pública (Railway PaaS) usando Docker, dois problemas severos de runtime geraram *crash loops* infinitos no container:

1. **Problema de Healthcheck de PaaS (Missing Port Bind):** Plataformas como Railway e Heroku matam automaticamente aplicações web que não sobem um servidor escutando na porta mapeada pela variável de ambiente `$PORT` (Timeouts de Healthcheck). Como o `python-telegram-bot` utilizava a estratégia de Long Polling, nenhuma porta TCP era aberta. A PaaS deduzia que o aplicativo estava travado no boot.

2. **Parsing de Strings Inválidas em Chaves da API (InvalidURL):** O bot "crashava" estourando uma exceção de formatação `httpx.InvalidURL` porque a interface visual HTML do painel da PaaS (Railway) transportou formatações invisíveis, como `\r`, `\n` e caracteres de retorno literal colados acidentalmente via transferência de área de transferência (Copy/Paste) do usuário.

## Decision

Para neutralizar ambos os ataques à estabilidade:

1. **Dummy HTTP Server:** Em vez de trocar a estratégia inteligente do Telegram (Polling) por Webhooks complexos apenas para satisfazer o provedor, optamos por instanciar um pseudo-servidor (Dummy HTTP Server) através da biblioteca nativa `http.server`. O servidor roda silenciosamente no background através do módulo nativo `threading` ouvindo a variável `$PORT`.

2. **Expressões Regulares sobre API Keys:** O uso de substituições fracas via `.strip()` ou `.replace()` mostrou-se insuficiente em alguns fluxos com interfaces de nuvem. Mudamos e adotamos Expressões Regulares Atômicas no `src/config.py` para todas as Keys baseadas em URL:
`re.sub(r'\s+', '', token)`: Essa técnica de funil extermina impiedosamente qualquer whitespace, barra invertida duplicada, quebras de linhas ou tabs antes da SDK formatar a requisição final, estancando a síndrome de crash de dependências (Httpx).

## Alternatives Considered

- **Substituir o Bot por Async Webhook Mode**: Usar frameworks como FastAPI e rodar a integração por Webhook com o Telegram. Rejeitado para o MVP a fim de manter foco na simplicidade da aplicação inicial. Polling foi considerado suficiente pela biblioteca oficial no cenário de carga atual.
- **Configurar Healthcheck via Railway CLI ou Railway.toml**: Substituir a detecção por comandos bash/customizados. Rejeitamos por diminuir a portabilidade. O *Dummy Server* assegura implantação em provedores terceiros estritos (como o Heroku antigo e DigitalOcean Apps) sem vendor lock-in e mantém a aplicação Docker agnóstica de cloud.

## Consequences

- **Pros:** Deploy universal (any-PaaS) estabelecido perfeitamente; Erros bobos de operação (copy/paste no Dashboard) resolvidos de forma assintomática (sistema à prova de bala na camada config).
- **Cons:** Há o acréscimo de uma Thread separada (overhead trivial) e de um import na interface do bot, mesmo rodando um `getUpdates` local que não demanda server em portas externas.

## Rule for Future Projects

Sempre injetar pseudo-servidores caso o robô rode processos assíncronos não-TCP em PaaS gerenciadas, e NUNCA confiar na integridade de colagem de chaves em painéis de provedores de nuvem (usar regex preventivo para variáveis de ambiente vitais e críticas).
