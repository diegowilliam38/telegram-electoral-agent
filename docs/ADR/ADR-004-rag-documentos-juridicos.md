# ADR-004: Estratégia de RAG para Documentos Jurídicos

**Date:** 2026-02-20
**Status:** Accepted

## Context

O agente não encontrava conceitos como "inelegibilidade" mesmo estando no manual. O chunking padrão (1000 tokens com overlap fixo) quebrava conceitos jurídicos no meio — o título da seção ficava em um chunk e o conteúdo em outro. Adicionalmente, saudações como "ola" eram processadas pelo pipeline RAG, gerando "Não encontrei essa informação no manual" como resposta.

## Decision

1. **Intent Classification obrigatório antes do RAG:**
Todo input passa por um nó de classificação de intenção antes de acionar o pipeline de busca semântica.

```python
def classify_intent(state):
    greetings = ["ola", "oi", "bom dia", "boa tarde", "olá", "tudo bem"]
    msg = state["message"].lower()
    if any(g in msg for g in greetings):
        return {"intent": "greeting"}
    return {"intent": "query"}
```

2. **Chunking semântico respeitando estrutura jurídica:**

```python
separators = ["\nArt.", "\nCapítulo", "\nSeção", "\nTítulo", "\n\n", "\n"]
chunk_size = 600      # menor = mais preciso para termos jurídicos
chunk_overlap = 100
```

3. **Retrieval expandido com reranking:**
Recuperar top-8 chunks (não top-3) e filtrar por relevância semântica antes de passar ao modelo.

## Alternatives Considered

- **Pinecone / Qdrant:** Desnecessário nesta escala. ChromaDB local suporta 300 páginas sem degradação de performance quando o problema real é qualidade do chunking, não escala do banco.
- **Chunk size 1000 tokens (padrão):** Testado. Fragmenta conceitos jurídicos compostos (ex: "suspensão condicional do processo") entre chunks, degradando recall.

## Consequences

- **Pros:** Recall correto para termos jurídicos compostos. Elimina erros em saudações. Pipeline mais robusto e explicável.
- **Cons:** Requer reprocessamento do índice vetorial existente com nova estratégia de chunking.

## Rule for Future Projects

Documentos jurídicos, técnicos ou acadêmicos com estrutura hierárquica (capítulos, artigos, seções) NUNCA devem usar chunking por tamanho fixo. O @architect deve definir separadores semânticos específicos do domínio antes de indexar.
