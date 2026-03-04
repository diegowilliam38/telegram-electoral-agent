# ADR-005: Protocolo de Criação de ADRs pelo Squad

**Date:** 2026-02-20
**Status:** Accepted

## Context

Decisões arquiteturais críticas estavam sendo tomadas e corrigidas durante o desenvolvimento sem registro formal. O conhecimento ficava na memória do Tech Lead e não era transferido para projetos futuros, forçando as mesmas descobertas a serem refeitas do zero.

## Decision

O @dev e o @architect devem propor um ADR sempre que:

- Uma biblioteca foi substituída por outra durante o desenvolvimento
- Um padrão de código foi corrigido por problema de runtime
- Uma alternativa foi considerada e rejeitada com motivo técnico
- Um erro de arquitetura foi identificado e corrigido
- Um comportamento inesperado de integração foi resolvido

O ADR proposto fica em draft até aprovação explícita do Tech Lead. Apenas ADRs aprovados entram na pasta `docs/ADR/`.

### Format

Usar sempre a estrutura:

- **Context:** Por que essa decisão foi necessária
- **Decision:** O que foi decidido
- **Alternatives Considered:** O que foi descartado e por quê
- **Consequences:** Pros e Cons da decisão
- **Rule for Future Projects:** Regra que o @architect deve aplicar em projetos similares

## Consequences

- **Pros:** Memória institucional do squad cresce com cada projeto. Próximos projetos similares nascem com decisões críticas já tomadas. Reduz intervenção do Tech Lead progressivamente.
- **Cons:** Adiciona um passo ao fluxo de desenvolvimento. Aceitável dado o ganho de qualidade em projetos futuros.

## Scope

ADRs com *Rule for Future Projects* devem ser copiados também para `_CORE_SKILLS/docs/ADR/` para valer como padrão global do squad, não apenas deste projeto.
