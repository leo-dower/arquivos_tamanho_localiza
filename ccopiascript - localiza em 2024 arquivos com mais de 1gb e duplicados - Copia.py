import os
import csv
import datetime
import logging

def setup_logging():
    """Configura o sistema de logging com timestamp e formato personalizado"""
    onedrive_path = get_onedrive_path()
    log_file = os.path.join(
        onedrive_path,
        f"large_files_log_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
    )
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()
        ]
    )
    return log_file

def get_onedrive_path():
    """Retorna o caminho padrão do OneDrive para o usuário logado no Windows."""
    path = os.path.join(os.path.expanduser("~"), "OneDrive")
    logging.info(f"OneDrive path determinado: {path}")
    return path

def get_all_files(base_path):
    """Retorna lista de arquivos com metadados, registrando progresso."""
    logging.info(f"Iniciando varredura recursiva em: {base_path}")
    file_list = []
    
    try:
        for root, dirs, files in os.walk(base_path):
            logging.debug(f"Varrendo diretório: {root} ({len(files)} arquivos)")
            for f in files:
                full_path = os.path.join(root, f)
                try:
                    size = os.path.getsize(full_path)
                    ctime = os.path.getctime(full_path)
                    creation_date = datetime.datetime.fromtimestamp(ctime)
                    file_list.append((full_path, size, creation_date))
                except Exception as e:
                    logging.error(f"Erro ao processar {full_path}: {str(e)}", exc_info=True)
    
    except Exception as e:
        logging.critical(f"Erro fatal durante varredura de arquivos: {str(e)}", exc_info=True)
        raise
    
    logging.info(f"Varredura concluída. Total de arquivos encontrados: {len(file_list)}")
    return file_list

def find_large_files_in_2024(file_list, min_size_bytes=1_000_000_000):
    """Filtra arquivos grandes de 2024 com registro detalhado."""
    logging.info(f"Iniciando filtragem de arquivos (>= {min_size_bytes} bytes em 2024)")
    
    filtered = []
    for fp, sz, creation_date in file_list:
        if creation_date.year == 2024 and sz >= min_size_bytes:
            logging.debug(f"Arquivo grande encontrado: {fp} ({sz} bytes, {creation_date})")
            filtered.append((fp, sz, creation_date))
    
    logging.info(f"Filtragem concluída. Arquivos grandes em 2024: {len(filtered)}")
    return filtered

# **Função adicionada para corrigir o erro**
def check_common_substring_9_or_more(file_name, file_name_list):
    """Verifica se um nome de arquivo contém uma substring de 9 ou mais caracteres presente em outros arquivos"""
    substrings = set()
    length = len(file_name)

    # Gera todas as substrings com 9 ou mais caracteres
    for i in range(length):
        for j in range(i + 9, length + 1):
            substrings.add(file_name[i:j])
    
    matching_files = [f for f in file_name_list if any(sub in f for sub in substrings)]
    
    return len(matching_files) > 1, matching_files

def main():
    try:
        log_file = setup_logging()
        logging.info("Iniciando processo de análise de arquivos")
        
        onedrive_path = get_onedrive_path()
        
        # 1. Obter lista de todos os arquivos
        all_files = get_all_files(onedrive_path)
        
        # 2. Filtrar arquivos grandes de 2024
        large_files_2024 = find_large_files_in_2024(all_files)
        
        # 3. Processar resultados
        logging.info("Processando resultados e verificando substrings")
        large_files_info = {fp: (os.path.basename(fp), sz, creation_date) 
                          for fp, sz, creation_date in large_files_2024}
        
        all_file_names = [os.path.basename(fp) for fp, _, _ in all_files]
        
        results = []
        for fp, (file_name, size, creation_date) in large_files_info.items():
            has_9plus, matching_list = check_common_substring_9_or_more(file_name, all_file_names)
            
            # Log de detecção de substring
            if has_9plus:
                logging.warning(f"Substring detectada em: {file_name} ({len(matching_list)} correspondências)")
            else:
                logging.debug(f"Nenhuma substring encontrada para: {file_name}")
            
            results.append((fp, size, creation_date, has_9plus, len(matching_list)))

        # 4. Exportar para CSV
        output_csv = os.path.join(onedrive_path, "arquivos_acima_1GB_2024.csv")
        logging.info(f"Gerando arquivo de relatório: {output_csv}")
        
        with open(output_csv, mode="w", encoding="utf-8", newline="") as csvfile:
            writer = csv.writer(csvfile, delimiter=";")
            writer.writerow(["Caminho do Arquivo", "Tamanho (bytes)", "Data de Criação", "Tem Substring >=9?", "Qtd. de Correspondências"])
            for row in results:
                writer.writerow(row)
        
        logging.info(f"Processo concluído com sucesso. Resultados em {output_csv}")
        logging.info(f"Log completo disponível em: {log_file}")

    except Exception as e:
        logging.error(f"Erro não tratado durante a execução: {str(e)}", exc_info=True)
        raise

if __name__ == "__main__":
    main()
