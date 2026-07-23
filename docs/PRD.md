# PRD - Agente Virtual do Cartório Eleitoral (TRE-MA)

## 1. Visão Geral do Produto
O **Agente Virtual do Cartório Eleitoral** é uma solução de inteligência artificial de alta fidelidade baseada em RAG (Retrieval-Augmented Generation) e orquestração agêntica via **LangGraph**, voltada ao atendimento de duas personas: **Servidores da Justiça Eleitoral (TRE-MA)** e **Cidadãos/Eleitores**.

## 2. Requisitos de Negócio e ROI
- **Redução de Atendimento Presencial/Telefônico:** Resolver 80%+ das dúvidas recorrentes de eleitores (local de votação, alistamento, transferência e biometria) de forma automatizada via Telegram/WhatsApp.
- **Produtividade Cartorária:** Fornecer suporte operacional imediato ao servidor com indicação direta de **códigos ASE**, telas do sistema Elo, procedimentos de balcão e fundamentação jurídica/doutrinária.

---

## 3. Arquitetura de Cognitive Skills Aprimorada (V2.0)

O "cérebro" do agente é expandido com 6 Cognitive Skills fundamentais baseadas nos padrões do `_CORE_SKILLS` (`gatilhos-wiki` e `antigravity-kit`):

| Skill | Papel & Padrão de Origem (`_CORE_SKILLS`) | Função no Agente Eleitoral |
| :--- | :--- | :--- |
| **`electoral-calendar-calculator`** | `gatilhos-decisao` / `gatilhos-estrategia` | Calcula prazos eleitorais das Eleições 2026 (ex: fechamento de cadastro, desincompatibilização). |
| **`ase-code-resolver`** | `gatilhos-raciocinio-critico` | Resolve problemas cadastrais sugerindo a combinação exata de Código ASE + Motivo + Documentos + Ação no Elo. |
| **`lgpd-privacy-shield`** | `gatilhos-privacidade-seguranca` | Mascara e sanitiza CPFs, RGs, Títulos e dados sensíveis antes de registrar logs ou responder ao usuário. |
| **`legal-citation-checker`** | `gatilhos-raciocinio-critico` (Steelman/Red Team) | Aplica a hierarquia de normas (Resolução TSE > Manual TRE > Doutrina) e previne alucinações de artigos de lei. |
| **`plain-language-translator`** | `gatilhos-comunicacao` (ELI5 / BLUF / Minto) | Converte o "juridiquês" em linguagem simples para o cidadão, agrupando em no máximo 3 etapas sem Markdown. |
| **`query-expander-electoral`** | `gatilhos-llm-prompt` | Expande os termos populares do eleitor (ex: "mudei de cidade") em sinônimos jurídicos para otimizar o RAG. |

---

## 4. Requisitos Não-Funcionais e Observabilidade
- **Tempo de Resposta RAG:** < 3.0s para recuperação vetorial FAISS + síntese LLM.
- **Privacidade & Conformidade:** Sanitização total nos logs `data/query_logs.jsonl` (LGPD).
- **Auto-Ingestion Watcher:** Thread assíncrona monitorando `docs/references/` para atualização da base vetorial sem downtime.
- **Saída Sanitizada:** Resposta em Texto Puro (Plain Text) para a persona `eleitor` no celular.
