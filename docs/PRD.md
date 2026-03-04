# Product Requirements Document (PRD)
**Project**: Agente Telegram Eleitoral (Cartório Virtual)
**Author**: @analyst (Industrial Squad)
**Status**: Draft

## 1. Problem Statement
Os servidores dos cartórios eleitorais precisam consultar frequentemente o **Manual de Práticas Cartorárias** para tirar dúvidas sobre procedimentos específicos (ex: alistamento, transferência, revisão, etc.). A consulta ao PDF é lenta e a busca por palavras-chave muitas vezes é imprecisa.

## 2. Solution Overview
Um **Agente de IA no Telegram** que atua como um especialista no Manual. O usuário faz uma pergunta em linguagem natural e o agente responde com base estritamente no conteúdo do manual, citando a fonte.

## 3. User Stories
*   **US.1**: Como servidor, quero perguntar "Quais os documentos para transferência de título?" e receber a lista exata do manual.
*   **US.2**: Como servidor, quero saber a página ou capítulo de onde a informação foi tirada para conferência.
*   **US.3**: Como administrador, quero poder atualizar o manual (PDF) e o agente aprender as novas regras automaticamente.

## 4. Functional Requirements
*   **Interface**: Telegram Bot.
*   **Input**: Texto (perguntas sobre processos eleitorais).
*   **Processing**: RAG (Retrieval-Augmented Generation) sobre o Manual de Práticas Cartorárias.
*   **Output**: Resposta textual + Citação (Página/Capítulo).
*   **Context**: O bot deve manter o contexto da conversa (ex: "E para alistamento?" deve entender que estamos falando de documentos, se essa foi a pergunta anterior).

## 5. Non-Functional Requirements
*   **Accuracy**: Alucinação zero. Se a resposta não estiver no manual, o bot deve dizer "Não encontrei essa informação no manual".
*   **Speed**: Resposta em < 5 segundos.
*   **Security**: Logs de conversas não devem expor dados sensíveis (embora a consulta seja sobre procedimentos públicos).

## 6. Constraints
*   Uso exclusivo do "Manual de Práticas Cartorárias 2022.pdf" como fonte de verdade.
