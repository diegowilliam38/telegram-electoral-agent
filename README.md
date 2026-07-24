# Agente Virtual do Cartório Eleitoral (TRE-MA) 🗳️🤖

O **Agente Virtual do Cartório Eleitoral** é uma solução de inteligência artificial de alta fidelidade baseada em **RAG (Retrieval-Augmented Generation)** e **LangGraph**, projetada para prestar suporte a servidores da Justiça Eleitoral do Maranhão (TRE-MA) e cidadãos (eleitores). O agente atua como um especialista no *Manual de Práticas Cartorárias*, *Resolução TSE nº 23.659/2021*, *Código Eleitoral Anotado 2026*, *Lei das Eleições* e doutrinas correlatas.

Atualmente implantado em produção na plataforma **Railway PaaS** com suporte a conteinerização Docker, resiliência 24/7 e observabilidade LGPD.

---

## 🏗️ Arquitetura do Sistema

O fluxo agêntico opera em topologia declarativa via LangGraph com suporte a múltiplos canais e deploy na Railway:

```mermaid
graph TD
    User([👤 Eleitor ou Servidor]) -->|Mensagem via Telegram| Telegram[📱 Telegram Bot - Railway]
    Telegram -->|Thread ID & Message| LangGraph [🧠 LangGraph Engine - Docker Container]
    
    subgraph LangGraph [🧠 Motor Agêntico LangGraph com 6 Cognitive Skills]
        Intent[🚦 Intent & LGPD Node] -->|Classifica Persona + Shield| Researcher[🔍 Researcher Node - RAG]
        Researcher -->|Busca Semântica & Expansão FAISS k=20| DB[(💾 FAISS Vector DB)]
        Researcher -->|Contexto Enriquecido| Validator[🛡️ Legal Citation Validator]
        Validator -->|Check Alucinações & Citações| Writer[✍️ Legal Writer Node]
    end
    
    Writer -->|Resposta Formatada / Plain Text| Telegram
    Telegram -->|Exibição no Celular| User
```

---

## 🚀 Status da Implantação (Railway PaaS)

| Componente | Ambiente | Uptime | Status |
| :--- | :--- | :---: | :--- |
| **Railway Container** | Production (`adorable-passion`) | 24/7 | 🟢 **ACTIVE / ONLINE** |
| **Cérebro Vetorial** | FAISS + OpenAI Embeddings | Instantâneo | 🟢 **11 PDFs (4.247 págs / 23.161 Chunks)** |
| **Auto-Ingestion** | Startup Pipeline | On Boot | 🟢 **Automático** |
| **Saúde HTTP** | Dummy Healthcheck (`:8080`) | 100% Uptime | 🟢 **PASSED** |

---

## ✨ As 6 Cognitive Skills Integradas (V2.0)

O agente conta com habilidades cognitivas especializadas baseadas nos padrões do `_CORE_SKILLS/gatilhos-wiki`:

1. **`query-expander-electoral`**: Expande automaticamente os termos do cidadão (ex: *"mudei de casa"* ➔ *"transferência de domicílio eleitoral requisitos documentos"*), otimizando a recuperação vetorial no FAISS.
2. **`ase-code-resolver`**: Mapeia diretamente no primeiro parágrafo (**BLUF**) os códigos de operação cadastral (*ex: ASE 337 motivo 2*), prazos, comprovantes e ações no sistema Elo para o servidor.
3. **`legal-citation-checker`**: Valida a presença de leis, resoluções (*Res. TSE 23.659/2021*) e citações do *Código Eleitoral Anotado 2026* prevenindo alucinações.
4. **`plain-language-translator`**: Traduz para **ELI5**, agrupa na **Regra dos 3 passos** e aplica **sanitização determinística de Plain Text (0% Markdown)** para o eleitor.
5. **`lgpd-privacy-shield`**: Detecta CPFs, RGs ou Títulos de Eleitor e injeta o aviso de privacidade no topo da conversa.
6. **`electoral-calendar-calculator`**: Orienta sobre prazos decadenciais das Eleições 2026 (151 dias antes do pleito, 100 dias transferência).

---

## 📂 Estrutura do Repositório

```
telegram-electoral-agent/
├── .agent/                  # Governança de planejamento e specs agênticas
│   ├── memory/              # Memory storage e context-loaded.yaml (Gate Duplo)
│   └── stories/             # Spec técnica STORY-002-spec.md (Zero Trust SDD)
├── data/                    # [Ignorado no Git / Gerado no Startup] Base FAISS e logs
├── docs/
│   ├── ADR/                 # Decisões de Arquitetura (ADR-001 até ADR-006)
│   ├── references/          # 11 PDFs Oficiais (Código Eleitoral 2026, Resoluções, Manuais)
│   └── PRD.md               # Product Requirements Document V2.0
├── pilot/                   # Artefatos da fase de expansão e deploy VPS
│   ├── .agent/stories/      # Spec STORY-PILOT-001-spec.md
│   └── docs/ADR/            # ADR-P001 e ADR-P002 (Roadmap Produção)
├── src/
│   ├── rag/
│   │   ├── ingestion.py     # Ingestão com CacheBackedEmbeddings e auto-startup
│   │   ├── intent.py        # Intent classifier + LGPD privacy shield
│   │   ├── researcher.py    # Researcher com Query Expansion e Cognitive Skills
│   │   ├── validator_skill.py # Legal Citation Checker anti-alucinação
│   │   └── legal_writer.py  # Formatação Dual Persona + Plain Text Stripper
│   ├── api.py               # FastAPI Adapter com SSE Streaming e Watcher
│   ├── bot.py               # Bot do Telegram com Dummy Server PaaS (:8080)
│   ├── config.py            # Variáveis e configurações globais
│   └── graph.py             # Compilação do Grafo LangGraph
├── tests/
│   ├── test_persona.py      # Testes de integração das 6 Cognitive Skills
│   ├── test_observability.py # Testes de logging e streaming E2E
│   └── test_retrieval.py    # Diagnóstico de recuperação FAISS
├── deploy_vps.sh            # Script de automação para deploy em servidores Linux/VPS
├── Dockerfile               # Container de produção para Railway / Cloud
├── docker-compose.yml       # Orquestração multi-container local / VPS
└── project-status.yaml      # Metadata do projeto no workspace
```

---

## 🛠️ Como Executar e Fazer Deploy

### Execução Local
```bash
# 1. Instalar dependências
pip install -r requirements.txt

# 2. Ingerir a base de conhecimento
python -m src.rag.ingestion

# 3. Executar o bot localmente
python src/bot.py
```

### Deploy em Nuvem (Railway PaaS)
O repositório já está pré-configurado para o **Railway**:
- O `Dockerfile` cria a estrutura e o `bot.py` roda a auto-ingestão dos PDFs no startup se o vetor não existir.
- O Railway injeta a porta `$PORT` para o `start_dummy_server()` validar o Healthcheck.

---

## 🧪 Testes Automatizados

Para rodar a suíte completa de verificação de personas e skills:
```bash
python -m tests.test_persona
```
