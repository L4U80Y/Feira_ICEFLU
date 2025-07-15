# Use uma imagem oficial do Python como base
FROM python:3.12-slim

# Defina variáveis de ambiente
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Defina o diretório de trabalho dentro do contêiner
WORKDIR /app

# Instale dependências
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copie o script de entrypoint para o contêiner
COPY entrypoint.sh .
# Torne o script executável dentro do contêiner
RUN chmod +x ./entrypoint.sh

# Copie o resto do código do projeto para o diretório de trabalho
COPY . .

# Comando ENTRYPOINT para rodar a aplicação quando o contêiner iniciar
# Este é o padrão recomendado que substitui o CMD anterior.
ENTRYPOINT ["./entrypoint.sh"]