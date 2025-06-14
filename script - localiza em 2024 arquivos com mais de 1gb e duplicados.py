import os
import csv
import datetime

def get_onedrive_path():
    """
    Retorna o caminho padrão do OneDrive para o usuário logado no Windows.
    """
    return os.path.join(os.path.expanduser("~"), "OneDrive")

def get_all_files(base_path):
    """
    Retorna uma lista de tuplas (caminho_completo, tamanho_em_bytes, data_criacao)
    de todos os arquivos contidos em base_path (percorrendo recursivamente).
    """
    file_list = []
    for root, dirs, files in os.walk(base_path):
        for f in files:
            full_path = os.path.join(root, f)
            try:
                size = os.path.getsize(full_path)
                # Data de criação no Windows
                ctime = os.path.getctime(full_path)
                creation_date = datetime.datetime.fromtimestamp(ctime)
                file_list.append((full_path, size, creation_date))
            except Exception as e:
                # Em caso de erro de permissão ou outro problema,
                # pode-se optar por um tratamento adicional
                print(f"Não foi possível obter informações de {full_path}: {e}")
    return file_list

def find_large_files_in_2024(file_list, min_size_bytes=1_000_000_000):
    """
    Retorna os arquivos cujo tamanho seja maior ou igual a min_size_bytes
    E cuja data de criação seja no ano de 2024.
    """
    filtered = []
    for (fp, sz, creation_date) in file_list:
        # Verifica se o ano de criação é 2024
        if creation_date.year == 2024 and sz >= min_size_bytes:
            filtered.append((fp, sz, creation_date))
    return filtered

def get_substrings_of_length_9_or_more(string_name):
    """
    Gera todas as substrings consecutivas de length >= 9 do nome do arquivo
    (sem pasta, mas com extensão).
    """
    substrings = set()
    n = len(string_name)
    for length in range(9, n + 1):
        for start in range(0, n - length + 1):
            substrings.add(string_name[start:start+length])
    return substrings

def check_common_substring_9_or_more(target_name, all_file_names):
    """
    Verifica se o arquivo `target_name` contém alguma sequência de
    9 ou mais caracteres que apareça em outros nomes de arquivo.
    
    Retorna:
    - Booleano (True/False) indicando se há coincidência
    - Lista de arquivos onde a coincidência foi encontrada
    """
    substrings_9_plus = get_substrings_of_length_9_or_more(target_name)
    matching_files = []

    for other_name in all_file_names:
        # Se for o mesmo nome, pula
        if other_name == target_name:
            continue
        
        # Verifica se alguma substring de 9+ caracteres está em other_name
        if any(sub in other_name for sub in substrings_9_plus):
            matching_files.append(other_name)
    
    return (len(matching_files) > 0, matching_files)

def main():
    onedrive_path = get_onedrive_path()
    
    # 1. Obter lista de todos os arquivos, tamanhos e datas de criação
    all_files = get_all_files(onedrive_path)
    
    # 2. Filtrar para arquivos criados em 2024 e com tamanho >= 1GB
    large_files_2024 = find_large_files_in_2024(all_files, 1_000_000_000)
    
    # 3. Precisamos apenas do nome do arquivo para ver semelhança de 9+ caracteres,
    #    mas também manteremos caminho completo (e a data de criação, se necessário).
    #    Então, estruturaremos em dicionário: { caminho_completo: (nome_arquivo, tamanho, data_criacao) }
    large_files_info = {}
    for fp, sz, creation_date in large_files_2024:
        file_name = os.path.basename(fp)  # nome do arquivo, com extensão
        large_files_info[fp] = (file_name, sz, creation_date)
    
    # 4. Montamos lista de todos os nomes de arquivo (de TODO o OneDrive),
    #    para comparação das substrings.
    all_file_names = [os.path.basename(fp) for fp, _, _ in all_files]
    
    # 5. Montar a tabela com as colunas desejadas
    #    a) Nome completo (com extensão)
    #    b) Tamanho (bytes)
    #    c) Localização
    #    d) Se há substring 9+ em comum
    #    e) Quantidade e quais arquivos contêm essas substrings
    #    f) Opcional: Data de criação
    results = []
    for fp, (file_name, size, creation_date) in large_files_info.items():
        has_9plus, matching_list = check_common_substring_9_or_more(file_name, all_file_names)
        
        # Monta o texto de resultado sobre substring de 9+ caracteres
        if has_9plus:
            matching_count = len(matching_list)
            matching_files_str = "; ".join(matching_list)
            substring_info = "Sim"
            matching_info = f"{matching_count} arquivo(s): {matching_files_str}"
        else:
            substring_info = "Não"
            matching_info = "N/A"
        
        results.append([
            file_name,           # Nome completo (com extensão)
            size,                # Tamanho em bytes
            fp,                  # Localização exata (caminho absoluto)
            creation_date,       # Data de criação
            substring_info,      # Se há substring 9+ em comum
            matching_info        # Quantidade e lista de arquivos correspondentes
        ])
    
    # 6. Exportar resultado para um arquivo CSV (ou imprimir na tela)
    output_csv = os.path.join(onedrive_path, "arquivos_acima_1GB_2024.csv")
    with open(output_csv, mode="w", encoding="utf-8", newline="") as csvfile:
        writer = csv.writer(csvfile, delimiter=";")
        # Cabeçalho
        writer.writerow([
            "Nome do Arquivo (c/ extensão)",
            "Tamanho (bytes)",
            "Localização",
            "Data de Criação",
            "Sequência 9+ em outros arquivos?",
            "Quantidade e Lista de Arquivos Correspondentes"
        ])
        # Linhas
        for row in results:
            writer.writerow(row)
    
    print(f"Processo concluído. Arquivo de resultado gerado em: {output_csv}")

if __name__ == "__main__":
    main()
