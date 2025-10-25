import json
import os
import shutil
import pandas as pd
import matplotlib.pyplot as plt
from openpyxl import load_workbook
from openpyxl.drawing.image import Image
from datetime import datetime

caminho = #Caminho da pasta com o arquivo entdados.dat e os arquivos JSON

os.chdir(caminho)

data = input("Entre com a data(AAAAMMDD): ")

caminho_entdados = caminho + '/entdados.dat'
caminho_copia = caminho + '/entdados_backup.dat'
shutil.copy(caminho_entdados, caminho_copia)

# Caminho para o arquivo JSON
SECO_json = caminho + "/SECO.json"

# Ler o arquivo JSON
with open(SECO_json, 'r') as arquivo:
    dados = json.load(arquivo)

# Criar DataFrame
SECO_carga = pd.DataFrame(dados)

data_formatada = datetime.strptime(data, "%Y%m%d").strftime("%Y-%m-%d")

data_grafico = datetime.strptime(data, "%Y%m%d").strftime("%d/%m/%Y")

# Converter para datetime e subtrair 3h30min
SECO_carga["din_referenciautc"] = pd.to_datetime(SECO_carga["din_referenciautc"]) - pd.Timedelta(hours=3, minutes=30)

# Converter de volta para string no formato original
SECO_carga["din_referenciautc"] = SECO_carga["din_referenciautc"].dt.strftime("%Y-%m-%dT%H:%M:%S.000Z")

# Extrair a hora da coluna 'din_referenciautc'
SECO_carga['horario_referencia'] = SECO_carga['din_referenciautc'].str.split('T').str[1].str.split(':').str[:2].str.join(':')

# Extraindo a data no formato AAAA-MM-DD
SECO_carga['data_formatada'] = pd.to_datetime(SECO_carga['din_referenciautc']).dt.strftime('%Y%m%d')

SECO_carga = SECO_carga[SECO_carga['dat_referencia'] == data_formatada]

SECO_carga['val_cargaglobal'] = SECO_carga['val_cargaglobal'].round(2).astype(int)

SECO_carga.drop(columns=[
    'din_atualizacao', 'dat_referencia', 'din_referenciautc',
    'val_cargaglobalcons', 'val_cargaglobalsmmgd', 'val_cargasupervisionada',
    'val_carganaosupervisionada', 'val_cargammgd', 'val_consistencia'
], inplace=True)# para armazenar os valores
SECO_carga['carga_estimada'] = pd.NA

# Caminho para o arquivo JSON
S_json = caminho + "/S.json"

# Ler o arquivo JSON
with open(S_json, 'r') as arquivo:
    dados = json.load(arquivo)

# Criar DataFrame
S_carga = pd.DataFrame(dados)

data_formatada = datetime.strptime(data, "%Y%m%d").strftime("%Y-%m-%d")

# Converter para datetime e subtrair 3h30min
S_carga["din_referenciautc"] = pd.to_datetime(S_carga["din_referenciautc"]) - pd.Timedelta(hours=3, minutes=30)

# Converter de volta para string no formato original
S_carga["din_referenciautc"] = S_carga["din_referenciautc"].dt.strftime("%Y-%m-%dT%H:%M:%S.000Z")

# Extrair a hora da coluna 'din_referenciautc'
S_carga['horario_referencia'] = S_carga['din_referenciautc'].str.split('T').str[1].str.split(':').str[:2].str.join(':')

# Extraindo a data no formato AAAA-MM-DD
S_carga['data_formatada'] = pd.to_datetime(S_carga['din_referenciautc']).dt.strftime('%Y%m%d')

S_carga = S_carga[S_carga['dat_referencia'] == data_formatada]

S_carga['val_cargaglobal'] = S_carga['val_cargaglobal'].round(2).astype(int)

S_carga.drop(columns=[
    'din_atualizacao', 'dat_referencia', 'din_referenciautc',
    'val_cargaglobalcons', 'val_cargaglobalsmmgd', 'val_cargasupervisionada',
    'val_carganaosupervisionada', 'val_cargammgd', 'val_consistencia'
], inplace=True)# para armazenar os valores
S_carga['carga_estimada'] = pd.NA

# Caminho para o arquivo JSON
N_json = caminho + "/N.json"

# Ler o arquivo JSON
with open(N_json, 'r') as arquivo:
    dados = json.load(arquivo)

# Criar DataFrame
N_carga = pd.DataFrame(dados)

data_formatada = datetime.strptime(data, "%Y%m%d").strftime("%Y-%m-%d")

# Converter para datetime e subtrair 3h30min
N_carga["din_referenciautc"] = pd.to_datetime(N_carga["din_referenciautc"]) - pd.Timedelta(hours=3, minutes=30)

# Converter de volta para string no formato original
N_carga["din_referenciautc"] = N_carga["din_referenciautc"].dt.strftime("%Y-%m-%dT%H:%M:%S.000Z")

# Extrair a hora da coluna 'din_referenciautc'
N_carga['horario_referencia'] = N_carga['din_referenciautc'].str.split('T').str[1].str.split(':').str[:2].str.join(':')

# Extraindo a data no formato AAAA-MM-DD
N_carga['data_formatada'] = pd.to_datetime(N_carga['din_referenciautc']).dt.strftime('%Y%m%d')

N_carga = N_carga[N_carga['dat_referencia'] == data_formatada]

N_carga['val_cargaglobal'] = N_carga['val_cargaglobal'].round(2).astype(int)

N_carga.drop(columns=[
    'din_atualizacao', 'dat_referencia', 'din_referenciautc',
    'val_cargaglobalcons', 'val_cargaglobalsmmgd', 'val_cargasupervisionada',
    'val_carganaosupervisionada', 'val_cargammgd', 'val_consistencia'
], inplace=True)# para armazenar os valores
N_carga['carga_estimada'] = pd.NA

# Caminho para o arquivo JSON
NE_json = caminho + "/NE.json"

# Ler o arquivo JSON
with open(NE_json, 'r') as arquivo:
    dados = json.load(arquivo)

# Criar DataFrame
NE_carga = pd.DataFrame(dados)

data_formatada = datetime.strptime(data, "%Y%m%d").strftime("%Y-%m-%d")

# Converter para datetime e subtrair 3h30min
NE_carga["din_referenciautc"] = pd.to_datetime(NE_carga["din_referenciautc"]) - pd.Timedelta(hours=3, minutes=30)

# Converter de volta para string no formato original
NE_carga["din_referenciautc"] = NE_carga["din_referenciautc"].dt.strftime("%Y-%m-%dT%H:%M:%S.000Z")

# Extrair a hora da coluna 'din_referenciautc'
NE_carga['horario_referencia'] = NE_carga['din_referenciautc'].str.split('T').str[1].str.split(':').str[:2].str.join(':')

# Extraindo a data no formato AAAA-MM-DD
NE_carga['data_formatada'] = pd.to_datetime(NE_carga['din_referenciautc']).dt.strftime('%Y%m%d')

NE_carga = NE_carga[NE_carga['dat_referencia'] == data_formatada]

NE_carga['val_cargaglobal'] = NE_carga['val_cargaglobal'].round(2).astype(int)

NE_carga.drop(columns=[
    'din_atualizacao', 'dat_referencia', 'din_referenciautc',
    'val_cargaglobalcons', 'val_cargaglobalsmmgd', 'val_cargasupervisionada',
    'val_carganaosupervisionada', 'val_cargammgd', 'val_consistencia'
], inplace=True)# para armazenar os valores
NE_carga['carga_estimada'] = pd.NA

# Abrir o arquivo e ler as linhas
with open('entdados.dat', 'r') as f:
    lines = f.readlines()

# Inicializa o contador
contador = 0

# Encontra a primeira linha com valor 'NaN' ou vazio na coluna 'carga_estimada'
primeira_linha_disponivel_SECO = SECO_carga[SECO_carga['carga_estimada'].isna()].index[0] if SECO_carga['carga_estimada'].isna().any() else len(SECO_carga)

# Encontra a primeira linha com valor 'NaN' ou vazio na coluna 'carga_estimada'
primeira_linha_disponivel_S = S_carga[S_carga['carga_estimada'].isna()].index[0] if S_carga['carga_estimada'].isna().any() else len(S_carga)

# Encontra a primeira linha com valor 'NaN' ou vazio na coluna 'carga_estimada'
primeira_linha_disponivel_NE = NE_carga[NE_carga['carga_estimada'].isna()].index[0] if NE_carga['carga_estimada'].isna().any() else len(NE_carga)

# Encontra a primeira linha com valor 'NaN' ou vazio na coluna 'carga_estimada'
primeira_linha_disponivel_N = N_carga[N_carga['carga_estimada'].isna()].index[0] if N_carga['carga_estimada'].isna().any() else len(N_carga)

# Encontra a primeira linha com valor 'NaN' ou vazio na coluna 'carga_estimada'
primeira_linha_disponivel_SECO_2 = SECO_carga[SECO_carga['carga_estimada'].isna()].index[0] if SECO_carga['carga_estimada'].isna().any() else len(SECO_carga)

# Encontra a primeira linha com valor 'NaN' ou vazio na coluna 'carga_estimada'
primeira_linha_disponivel_S_2 = S_carga[S_carga['carga_estimada'].isna()].index[0] if S_carga['carga_estimada'].isna().any() else len(S_carga)

# Encontra a primeira linha com valor 'NaN' ou vazio na coluna 'carga_estimada'
primeira_linha_disponivel_NE_2 = NE_carga[NE_carga['carga_estimada'].isna()].index[0] if NE_carga['carga_estimada'].isna().any() else len(NE_carga)

# Encontra a primeira linha com valor 'NaN' ou vazio na coluna 'carga_estimada'
primeira_linha_disponivel_N_2 = N_carga[N_carga['carga_estimada'].isna()].index[0] if N_carga['carga_estimada'].isna().any() else len(N_carga)

# Loop sobre as linhas do arquivo para buscar os valores de carga
for line in lines:
    if line.startswith("DP   1"):

        carga = line[26:34].strip()

        # Converte para número (caso precise)
        carga = float(carga)

        # Aloca o valor na primeira linha disponível da coluna 'carga_estimada'
        SECO_carga.loc[primeira_linha_disponivel_SECO, 'carga_estimada'] = carga

        # Incrementa o contador e vai para a próxima linha disponível
        primeira_linha_disponivel_SECO += 1
        contador += 1

    elif line.startswith("DP   2"):

        carga = line[26:34].strip()

        # Converte para número (caso precise)
        carga = float(carga)

        # Aloca o valor na primeira linha disponível da coluna 'carga_estimada'
        S_carga.loc[primeira_linha_disponivel_S, 'carga_estimada'] = carga

        # Incrementa o contador e vai para a próxima linha disponível
        primeira_linha_disponivel_S += 1
        contador += 1

    elif line.startswith("DP   3"):

        carga = line[26:34].strip()

        # Converte para número (caso precise)
        carga = float(carga)

        # Aloca o valor na primeira linha disponível da coluna 'carga_estimada'
        NE_carga.loc[primeira_linha_disponivel_NE, 'carga_estimada'] = carga

        # Incrementa o contador e vai para a próxima linha disponível
        primeira_linha_disponivel_NE += 1
        contador += 1

    elif line.startswith("DP   4"):

        carga = line[26:34].strip()

        # Converte para número (caso precise)
        carga = float(carga)

        # Aloca o valor na primeira linha disponível da coluna 'carga_estimada'
        N_carga.loc[primeira_linha_disponivel_N, 'carga_estimada'] = carga

        # Incrementa o contador e vai para a próxima linha disponível
        primeira_linha_disponivel_N += 1
        contador += 1

    # Se já tiver alocado 48 valores, pare
    if contador == 192:
        break

# Concatenando os DataFrames linha por linha
SIN_carga = pd.concat([SECO_carga, S_carga, NE_carga, N_carga], ignore_index=True)

contador = 0
with open('entdados.dat', 'r+') as f:
    lines = f.readlines()  # Lê todas as linhas do arquivo
    contador = 0  # Variável para controle de contagem

    # Encontrar a linha que começa com 'EOLICA-GERACAO'
    for i, line in enumerate(lines):
        if contador < 192:
            if line.startswith("DP   1"):
                # Substituir a parte da linha, ajustando a posição de escrita
                new_value = str(SECO_carga.loc[primeira_linha_disponivel_SECO_2, 'val_cargaglobal']).rjust(10)  # Ajustando para 10 caracteres, por exemplo
                lines[i] = line[:24] + new_value + line[34:]
                primeira_linha_disponivel_SECO_2 += 1
                contador += 1

            elif line.startswith("DP   2"):
                # Substituir a parte da linha, ajustando a posição de escrita
                new_value = str(S_carga.loc[primeira_linha_disponivel_S_2, 'val_cargaglobal']).rjust(10)  # Ajustando para 10 caracteres
                lines[i] = line[:24] + new_value + line[34:]
                primeira_linha_disponivel_S_2 += 1
                contador += 1

            elif line.startswith("DP   3"):
                # Substituir a parte da linha, ajustando a posição de escrita
                new_value = str(NE_carga.loc[primeira_linha_disponivel_NE_2, 'val_cargaglobal']).rjust(10)  # Ajustando para 10 caracteres
                lines[i] = line[:24] + new_value + line[34:]
                primeira_linha_disponivel_NE_2 += 1
                contador += 1

            elif line.startswith("DP   4"):
                # Substituir a parte da linha, ajustando a posição de escrita
                new_value = str(N_carga.loc[primeira_linha_disponivel_N_2, 'val_cargaglobal']).rjust(10)  # Ajustando para 10 caracteres
                lines[i] = line[:24] + new_value + line[34:]
                primeira_linha_disponivel_N_2 += 1
                contador += 1

    # Voltar ao início do arquivo e sobrescrever com as novas linhas
    f.seek(0)
    f.truncate()  # Apaga o conteúdo do arquivo antes de reescrever
    f.writelines(lines)  # Escreve as linhas modificadas de volta no arquivo
