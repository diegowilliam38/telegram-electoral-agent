#!/bin/bash

# Script de Deploy Automatizado para VPS (Hostinger / Ubuntu)
# Projeto: telegram-electoral-agent

set -e

echo "🚀 Iniciando Deploy do Agente Eleitoral na VPS..."

# 1. Pull das últimas alterações do repositório
echo "📥 Atualizando código fonte via Git..."
git pull origin main || echo "⚠️ Alerta: Git pull falhou ou não é um repositório git ativo."

# 2. Verificar se o arquivo .env existe
if [ ! -f .env ]; then
    echo "❌ Erro: Arquivo .env não encontrado! Crie o .env com as chaves antes de continuar."
    exit 1
fi

# 3. Build dos containers Docker
echo "🔨 Construindo containers Docker (API + Bot)..."
docker-compose build

# 4. Subir os serviços em background
echo "⚡ Subindo serviços com docker-compose..."
docker-compose up -d

# 5. Status dos containers
echo "✅ Deploy concluído com sucesso! Status dos serviços:"
docker-compose ps

echo "📋 Exibindo os últimos logs:"
docker-compose logs --tail=20
