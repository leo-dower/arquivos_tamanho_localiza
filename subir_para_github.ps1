# Script PowerShell para subir arquivos para o GitHub
# Caminho: f:\OneDrive\scripts\arquivos tamanho localiza
# Repositório: https://github.com/leo-dower/arquivos_tamanho_localiza

# Inicializa o repositório git (caso ainda não exista)
git init

# Adiciona todos os arquivos da pasta
git add .

# Faz o commit dos arquivos
git commit -m "Primeiro commit dos arquivos de comparação"

# Define o branch principal como main
git branch -M main

# Adiciona o repositório remoto
git remote add origin https://github.com/leo-dower/arquivos_tamanho_localiza

# Envia os arquivos para o GitHub
git push -u origin main
