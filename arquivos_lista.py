import os
import datetime

def listar_arquivos_recentes(caminho, limite=10):
    hoje = datetime.datetime.today().date()
    arquivos = []

    # Percorre os arquivos e diretórios recursivamente
    for root, _, files in os.walk(caminho):
        for file in files:
            caminho_completo = os.path.join(root, file)
            try:
                # Obtém a data de criação do arquivo
                data_criacao = datetime.datetime.fromtimestamp(os.path.getctime(caminho_completo)).date()
                if data_criacao == hoje:
                    arquivos.append((caminho_completo, os.path.getctime(caminho_completo)))
            except Exception as e:
                continue  # Ignora arquivos com erro de permissão

    # Ordena os arquivos pela data de criação (do mais recente para o mais antigo)
    arquivos.sort(key=lambda x: x[1], reverse=True)

    # Exibe os 10 mais recentes
    for arquivo in arquivos[:limite]:
        print(arquivo[0])

# Define o diretório C:\
listar_arquivos_recentes("C:\\")
