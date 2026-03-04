# Story: Fase 1 — Migração do Banco Vetorial (ChromaDB para pgvector)

## Objetivo

Mudar o armazenamento dos embeddings do manual cartorário do disco local (ChromaDB) para um banco em nuvem (Supabase + pgvector) para permitir escala e deploy serverless/VPS.

## Critérios de Aceite

- [ ] Conexão com Supabase PostgreSQL estabelecida.
- [ ] Dependências `langchain-postgres` e drivers (psycopg) instalados.
- [ ] Script de ingestão de PDF modificado para gravar os chunks no Supabase.
- [ ] `src/rag/retrieval.py` modificado para usar o retriever do Supabase.
- [ ] Teste unitário independente capaz de buscar um termo no banco em nuvem e retornar resultados relevantes.

## Dependências

Nenhuma.
