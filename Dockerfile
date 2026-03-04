# Usar uma imagem oficial e leve do Python (Alpine pode dar problema com FAISS C++, então usamos slim)
FROM python:3.11-slim

# Definir fuso horário para bater com o horário de Brasília (para logs)
ENV TZ=America/Sao_Paulo
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

# Atualizar pacotes de sistema e instalar dependências essenciais de build
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Definir o diretório de trabalho no container
WORKDIR /app

# Copiar os requirements primeiro para aproveitar o cache do Docker
COPY requirements.txt .

# Instalar dependências Python
RUN pip install --no-cache-dir -r requirements.txt

# Copiar os dados sensíveis e o código
# OBS: O Banco FAISS (data/) será copiado junto para não ter que fazer ingestão na VPS
COPY data/ data/
COPY src/ src/

# Setar a variável de ambiente PYTHONPATH para reconhecer o diretório src/
ENV PYTHONPATH=/app

# Comando de execução do Bot
CMD ["python", "src/bot.py"]
