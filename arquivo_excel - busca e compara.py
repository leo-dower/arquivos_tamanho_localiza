import re
import pandas as pd

# 1. Expressão regular para validar o formato CNJ:
#    XXXXXXX-XX.XXXX.X.XX.XXXX
#    Exemplo: 0000180-56.2012.8.11.0020
padrao_cnj = re.compile(r'^\d{7}-\d{2}\.\d{4}\.\d\.\d{2}\.\d{4}$')

def validar_formato_cnj(numero_processo: str) -> bool:
    """Retorna True se o número de processo estiver no padrão CNJ, False caso contrário."""
    return bool(padrao_cnj.match(numero_processo))

# 2. Caminho para o arquivo Excel com as 4 planilhas
arquivo_excel = r'C:\Users\leuxi\OneDrive\Advocacia\ano 2025\arquivo_excel.xlsx'

# 3. Carrega as planilhas do arquivo Excel
xls = pd.ExcelFile(arquivo_excel)

# 4. Leitura das planilhas (ajuste conforme os nomes corretos das abas no seu arquivo)
leonardo_1 = pd.read_excel(xls, 'Leonardo_1')
leonardo_2 = pd.read_excel(xls, 'Leonardo_2')
paulo_1    = pd.read_excel(xls, 'Paulo_1')
paulo_2    = pd.read_excel(xls, 'Paulo_2')

# 5. Extrair os números de processo e filtrar apenas aqueles no formato CNJ

# Função auxiliar para extrair e filtrar os processos de uma planilha
def extrair_processos_no_formato_cnj(df, nome_coluna='Processo'):
    """
    Extrai os valores da coluna 'nome_coluna' de um DataFrame,
    remove valores ausentes ou espaços e filtra apenas aqueles
    que estiverem no formato CNJ.
    """
    # Garante que todos os valores sejam strings e remove espaços extras
    processos_series = df[nome_coluna].dropna().astype(str).str.strip()
    # Aplica a função de validação para filtrar apenas processos no formato CNJ
    processos_filtrados = set(processos_series[processos_series.apply(validar_formato_cnj)])
    return processos_filtrados

# Extrai e filtra os processos de cada planilha
processos_leonardo_1 = extrair_processos_no_formato_cnj(leonardo_1)
processos_leonardo_2 = extrair_processos_no_formato_cnj(leonardo_2)
processos_paulo_1    = extrair_processos_no_formato_cnj(paulo_1)
processos_paulo_2    = extrair_processos_no_formato_cnj(paulo_2)

# 6. Une os processos do Leonardo e os do Paulo
processos_leonardo = processos_leonardo_1.union(processos_leonardo_2)
processos_paulo    = processos_paulo_1.union(processos_paulo_2)

# 7. Identifica a interseção, ou seja, os processos que estão em ambos os conjuntos
processos_em_comum = processos_leonardo.intersection(processos_paulo)

# 8. Exibe o resultado
print("Processos em que ambos os advogados atuam (no formato CNJ):")
for proc in sorted(processos_em_comum):
    print(proc)
