# Spec Técnica: Expansão do Cérebro Agêntico (6 Cognitive Skills)

**ID:** `STORY-002`
**Autor:** `@architect` / `@prompt-engineer`
**Status:** `READY_FOR_DEV`

---

## 1. Escopo Técnico

Implementar e integrar as 6 Cognitive Skills nos nós do LangGraph (`src/rag/`):

1. `src/rag/intent.py`: Adicionar detecção avançada de intenção, urgência e flag preventiva de LGPD.
2. `src/rag/researcher.py`: Incorporar expansão de queries (`query-expander-electoral`), regras de códigos ASE (`ase-code-resolver`) e prazos das Eleições 2026 (`electoral-calendar-calculator`).
3. `src/rag/validator_skill.py`: Evoluir o validador para checar hierarquia de normas e prazos/siglas (`legal-citation-checker`).
4. `src/rag/legal_writer.py`: Implementar tradução didática ELI5 e sanitizador determinístico de Texto Puro (`plain-language-translator` & `lgpd-privacy-shield`).

---

## 2. Critérios BINÁRIOS de Aceite (Passa / Falha)

- [ ] **Passa/Falha 1:** `tests/test_persona.py` roda com 100% de sucesso.
- [ ] **Passa/Falha 2:** A resposta da persona `eleitor` contém ZERO marcações de Markdown (sem `**`, sem `*`, sem `#`) — Plain Text verificado por Regex.
- [ ] **Passa/Falha 3:** Perguntas com termos leigos (ex: "mudei de casa") acionam a busca expandida por "transferência de domicílio eleitoral".
- [ ] **Passa/Falha 4:** Dados pessoais fictícios (CPF/Título) acionam o aviso LGPD em 100% das chamadas.
