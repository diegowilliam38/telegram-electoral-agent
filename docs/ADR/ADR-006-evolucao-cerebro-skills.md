# ADR-006: Evolução do Cérebro Agêntico — Integração das 6 Cognitive Skills Eleitorais

- **Status:** ACEITO
- **Data:** 2026-07-23
- **Autor:** @architect & @prompt-engineer
- **Contexto:** 
  O projeto `telegram-electoral-agent` opera com RAG no LangGraph. Para responder com alta precisão técnica a servidores e em linguagem simples a cidadãos, o agente necessita de habilidades cognitivas especializadas em Direito Eleitoral, cálculo de prazos e minimização de dados LGPD.

---

## Decisão

Adotar e acoplar **6 Cognitive Skills Específicas** diretamente na topologia do LangGraph, aproveitando os vocabulários e padrões operacionais do `_CORE_SKILLS/gatilhos-wiki`:

1. **`lgpd-privacy-shield`**: Sanitização e aviso preventivo ao detectar dados sensíveis (CPF, RG, Título) em `src/rag/intent.py` e `src/rag/legal_writer.py`.
2. **`query-expander-electoral`**: Expansão de sinônimos populares para termos técnicos eleitorais antes do RAG em `src/rag/researcher.py`.
3. **`legal-citation-checker`**: Validação de hierarquia de normas e prevenção de alucinação de artigos em `src/rag/validator_skill.py`.
4. **`ase-code-resolver`**: Resolução orientada a códigos ASE/Elo para servidores cartorários em `src/rag/researcher.py`.
5. **`plain-language-translator`**: Sanitizador determinístico de Texto Puro (sem Markdown) e tradutor ELI5 em `src/rag/legal_writer.py`.
6. **`electoral-calendar-calculator`**: Injeção de conhecimento sobre prazos das Eleições 2026 nos nós do LangGraph.

---

## Consequências

### Positivas
- **Aumento na Relevância do RAG:** A expansão de queries melhora a taxa de busca para eleitores leigos.
- **Segurança Jurídica:** O validador garante que artigos não citados no contexto sejam bloqueados.
- **Conformidade LGPD:** Garantia de zero vazamento de dados sensíveis nos logs do sistema.
- **Formatação Impecável:** Garantia de Plain Text absoluto para dispositivos móveis via Telegram.

### Mitigações
- Manter o tempo de resposta total do RAG abaixo de 3 segundos utilizando retries assíncronos e cache.
