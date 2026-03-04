# ADR-006: Estrutura Multiagente e Resiliência em Ambiente Doméstico

**Date:** 2026-02-25
**Status:** Accepted

## Context

O assistente `telegram-electoral-agent` atua como suporte para servidores cartorários do TRE-MA. A estrutura atual baseia-se em uma cadeia simples onde o resultado da busca (RAG) é processado diretamente pelo modelo em um único nó. Isso gera desafios:

1. Mistura de responsabilidades: O modelo deve ao mesmo tempo consolidar fatos técnicos (extração literal) e formatar uma linguagem cordial (Assistente Virtual).
2. Perda de rastreabilidade: A citação da fonte pode se perder ou ser omitida durante a geração da resposta.
3. Instabilidade ambiental: Em ambiente doméstico/local, ocorrem microquedas de conexão com a API da OpenAI.
4. Falha silenciosa: Às vezes as fontes citadas não correspondem aos documentos reais recuperados.

## Decision

Evoluir a arquitetura do LangGraph para um modelo Multiagente com as seguintes definições:

1. **Separação de Papéis (Nós do Grafo):**
   - **Nó Researcher:** Focado exclusivamente em RAG técnico e extração literal do manual usando o banco vetorial ChromaDB. Seu papel não é ser educado, mas sim preciso e estrito.
   - **Nó Legal-Writer (Persona):** Recebe o contexto bruto do Researcher e reescreve a resposta usando o System Prompt oficial: "Você é o Assistente Virtual do TRE-MA...". Garante a cordialidade, simplifica a linguagem (sem juridiquês excessivo) e *obrigatoriamente* insere a fonte (Artigo/Página).

2. **Skill de Resiliência e Validação:**
   - **Validador de Citação:** Um passo/nó condicional ou verificação no próprio Legal-Writer que garanta que a fonte (Artigo/Página) mencionada existe nos metadados extraídos pelo Researcher.
   - **Mecanismos de Retry/Timeout:** Utilizar Tenacity (ou similar) nas chamadas do LLM para lidar com microquedas e latências elevadas, respeitando a Seção 4.1 das regras globais.

## Alternatives Considered

- **Chain of Density ou Prompt Complexo Único:** Tentar forçar um único nó a ser estrito e amigável simultaneamente. Rejeitado porque modelos tendem a alucinar mais fontes quando tentam "conversar" no mesmo turno da pesquisa.
- **RAG puro sem persona:** Retornar os recortes secos. Rejeitado pois a experiência do usuário exige cordialidade.

## Consequences

- **Pros:** Modularidade total. O Researcher garante a segurança jurídica; o Legal-Writer foca na UX do servidor do TRE-MA. As chamadas ganham robustez contra timeouts locais. Citações tornam-se 100% confiáveis (se não validar, aciona a Corregedoria).
- **Cons:** O tempo de resposta pode aumentar marginalmente por ter dois ciclos de LLM em vez de um, e o design do estado do LangGraph (AgentState) precisa ser ampliado para reter as fontes intermediárias.

## Rule for Future Projects

Sempre separar a "Pesquisa Rigorosa" da "Expressão Conversacional" em assistentes não-triviais e incorporar patterns de retry em chamadas de API feitas em infraestruturas não garantidas (local/doméstica).
