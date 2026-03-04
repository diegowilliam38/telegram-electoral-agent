# ADR 001: RAG com ChromaDB Local

**Date**: 2026-02-16
**Status**: Accepted

## Context

Precisamos de um sistema de busca semântica para o manual cartorário. O volume de dados é pequeno (um único PDF de ~200-500 páginas). Precisamos de uma solução que seja fácil de rodar localmente e não exija infraestrutura complexa (como Pinecone ou Weaviate cloud) nesta fase inicial.

## Decision

Utilizaremos **ChromaDB** rodando em modo persistente local (arquivo em disco).

## Alternatives Considered

* **Pinecone**: Bom, mas exige conexão externa e gestão de chaves/tier free.
* **FAISS**: Muito rápido, mas a persistência de metadados é mais manual.
* **Postgres (pgvector)**: Ótimo, mas exige levantar um container Docker adicional com Postgres.

## Consequences

* **Pros**: Zero infraestrutura (apenas arquivos locais), instalação via pip simples.
* **Cons**: Não escala para milhões de documentos (não é o caso aqui).

## Rule for Future Projects

O @architect deve priorizar bancos vetoriais locais embarcados (como ChromaDB) para projetos com volumetria de dados baixa a média onde simplicidade de deploy seja prioritária, reservando soluções Cloud (Pinecone, Supabase) para alta volumetria ou ambientes multi-usuário estritos.
