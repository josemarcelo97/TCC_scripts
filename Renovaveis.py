import os
import shutil
import pandas as pd
from datetime import datetime, timedelta, time
import matplotlib.pyplot as plt
from openpyxl import load_workbook
from openpyxl.drawing.image import Image
from io import BytesIO
import openpyxl


data_variavel = input("Entre com a data (DDMMAAAA): ")

caminho = #Caminho dos arquivos
geracao_UFV = #Nome da planilha de restrições UFVs
geracao_EOL = #Nome da planilha de restrições EOL


os.chdir(caminho)

# Ler os arquivos em excel e guardar em dataframe
df_geracao_UFV = pd.read_excel(geracao_UFV)
#df_geracao_EOL = pd.read_excel(geracao_EOL)
df_geracao_EOL = pd.read_csv(geracao_EOL, delimiter=";", encoding="utf-8")

rateio_file_path_UFV = caminho + "/Conjunto Usina Barra Rateio UFV.txt"
rateio_file_path_EOL = caminho + "/Conjunto Usina Barra Rateio.txt"

Conjunto_rateio_EOL = pd.read_csv(rateio_file_path_EOL, delimiter=';', encoding='latin1')  # Ajuste o delimitador e encoding se necessário
Conjunto_rateio_UFV = pd.read_csv(rateio_file_path_UFV, delimiter=';', encoding='latin1')

# Faz a cópia do arquivo
caminho_renovaveis = caminho + '/renovaveis.dat'
caminho_copia = caminho + '/renovaveis_backup.dat'
shutil.copy(caminho_renovaveis, caminho_copia)
print(f'Arquivo renováveis backup copiado')

# Inicializando listas para armazenar os dados
dados_renovaveis_list = []
dados_renovaveis_barra_list = []
dados_renovaveis_subm_list = []
dados_renovaveis_geracao_list = []

# Lê o arquivo renovaveis.dat
with open(caminho_renovaveis, 'r') as file:
    for linha_num, linha in enumerate(file, start=1):
        if linha.startswith("EOLICA "):
            partes_linha = linha.strip().split(';')
            dados_renovaveis_list.append(partes_linha)

        elif linha.startswith("EOLICABARRA"):
            partes_linha = linha.strip().split(';')
            dados_renovaveis_barra_list.append(partes_linha)

        elif linha.startswith("EOLICASUBM "):
            partes_linha = linha.strip().split(';')
            dados_renovaveis_subm_list.append(partes_linha)

        elif linha.startswith("EOLICA-GERACAO "):
            partes_linha = linha.strip().split(';')
            dados_renovaveis_geracao_list.append(partes_linha)

# Cria os DataFrames a partir das listas
dados_renovaveis_geracao = pd.DataFrame(
    dados_renovaveis_geracao_list,
    columns=['&', 'CODIGO', 'Dia', 'hi', 'mhi', 'diaf', 'hf', 'mhf', 'Geração', 'Vazio']
)

# Cria os DataFrames a partir das listas
dados_renovaveis = pd.DataFrame(
    dados_renovaveis_list,
    columns=['&', 'CODIGO', 'NOME: Usina, Barra', 'PMAX', 'FCAP', 'C', 'Vazio']
)

# Mantém somente as colunas desejadas
dados_renovaveis = dados_renovaveis[['CODIGO', 'NOME: Usina, Barra', 'C']]
dados_renovaveis_barra = pd.DataFrame(dados_renovaveis_barra_list, columns=['&', 'CODIGO', 'BARRA', 'Vazio'])
dados_renovaveis_subm = pd.DataFrame(dados_renovaveis_subm_list, columns=['&', 'CODIGO', 'SBM', 'Vazio'])
dados_renovaveis_geracao = pd.DataFrame(dados_renovaveis_geracao_list,
                                        columns=['&', 'CODIGO', 'di', 'hri', 'mi', 'df', 'hrf',
                                                 'mf', 'GERACAO', 'Vazio'])

# Remove a última coluna de todos os DataFrames
dados_renovaveis_barra.drop(columns=dados_renovaveis_barra.columns[-1], inplace=True)
dados_renovaveis_subm.drop(columns=dados_renovaveis_subm.columns[-1], inplace=True)
dados_renovaveis_geracao.drop(columns=dados_renovaveis_geracao.columns[-1], inplace=True)

colunas_divididas = dados_renovaveis['NOME: Usina, Barra'].str.split('_', expand=True)

# Verificar se a divisão gerou exatamente 4 colunas
if colunas_divididas.shape[1] == 4:
    dados_renovaveis[['ID', 'Nome', 'Barra', 'Tipo']] = colunas_divididas
else:
    # Caso tenha mais de 4 colunas, alocar as 3 primeiras partes em 'ID', 'Nome' e 'Barra'
    dados_renovaveis[['ID', 'Nome', 'Barra']] = colunas_divididas.iloc[:, :3]

    # Caso tenha mais de 4 partes, juntar o restante na coluna 'Tipo'
    dados_renovaveis['Tipo'] = colunas_divididas.iloc[:, 3:].apply(lambda x: '_'.join(x.dropna()),
                                                                   axis=1)

    # Caso tenha menos de 4 colunas, preencher as faltantes com NaN
    dados_renovaveis[['ID', 'Nome', 'Barra', 'Tipo']] = dados_renovaveis[
        ['ID', 'Nome', 'Barra', 'Tipo']].fillna(value=pd.NA)

# Remover a coluna 'C' do DataFrame
coluna_C = dados_renovaveis.pop('C')

# Adicionar a coluna 'C' ao final
dados_renovaveis['C'] = coluna_C

# Criando o DataFrame de backup
dados_mmgd = pd.DataFrame()

# Filtrando os dados que começam com "5G" na coluna "NOME: Usina, Barra"
dados_mmgd = dados_renovaveis[dados_renovaveis['ID'].str.startswith('5G')]

# Excluindo os registros de 'dados_renovaveis' que começam com "5G"
dados_renovaveis = dados_renovaveis[~dados_renovaveis['ID'].str.startswith('5G')]

dados_renovaveis["CODIGO"] = dados_renovaveis["CODIGO"].astype(int)
dados_renovaveis["ID"] = dados_renovaveis["ID"].str.strip()


# Atualizar as colunas "Nome" e "Barra" conforme o valor da coluna "CODIGO"
dados_renovaveis.loc[dados_renovaveis["CODIGO"] == 1219, "Nome"] = "CTV_ACARAU_I"
dados_renovaveis.loc[dados_renovaveis["CODIGO"] == 1219, "Barra"] = "05320"

dados_renovaveis.loc[dados_renovaveis["CODIGO"] == 1291, "Nome"] = "ASS_ASSU V"
dados_renovaveis.loc[dados_renovaveis["CODIGO"] == 1291, "Barra"] = "05805"

# Tentar converter as colunas para inteiros
dados_renovaveis["Barra"] = dados_renovaveis["Barra"].astype(int)

# Primeiro merge entre dados_renovaveis e Conjunto_rateio_EOL
dados_renovaveis = dados_renovaveis.merge(
    Conjunto_rateio_EOL[['BARRA', 'CODIGODAUSINA', 'PERCENTUAL RATEIO', 'CODIGO DO CONJUNTO']],
    left_on=['Barra', 'ID'],
    right_on=['BARRA', 'CODIGO DO CONJUNTO'],
    how='left'
)

# Renomeando as colunas para ter nomes consistentes
dados_renovaveis.rename(columns={'CODIGODAUSINA': 'CODIGODAUSINA', 'PERCENTUAL RATEIO': 'PERCENTUAL RATEIO'}, inplace=True)

# Segundo merge entre dados_renovaveis e Conjunto_rateio_UFV
dados_renovaveis = dados_renovaveis.merge(
    Conjunto_rateio_UFV[['BARRA', 'CODIGODAUSINA', 'PERCENTUAL RATEIO', 'CODIGO DO CONJUNTO']],
    left_on=['Barra', 'ID'],
    right_on=['BARRA', 'CODIGO DO CONJUNTO'],
    how='left'  # 'left' mantém todos os dados do dados_renovaveis e adiciona as colunas do Conjunto_rateio_UFV
)

# Verificar se o valor na coluna 'y' não é NaN antes de copiar para a coluna 'x'
dados_renovaveis['BARRA_x'] = dados_renovaveis['BARRA_y'].where(pd.notna(dados_renovaveis['BARRA_y']), dados_renovaveis['BARRA_x'])
dados_renovaveis['CODIGODAUSINA_x'] = dados_renovaveis['CODIGODAUSINA_y'].where(pd.notna(dados_renovaveis['CODIGODAUSINA_y']), dados_renovaveis['CODIGODAUSINA_x'])
dados_renovaveis['PERCENTUAL RATEIO_x'] = dados_renovaveis['PERCENTUAL RATEIO_y'].where(pd.notna(dados_renovaveis['PERCENTUAL RATEIO_y']), dados_renovaveis['PERCENTUAL RATEIO_x'])

# Excluir as colunas y
dados_renovaveis = dados_renovaveis.drop(columns=['BARRA_y', 'CODIGODAUSINA_y', 'PERCENTUAL RATEIO_y'])

# Renomear as colunas x para o nome final desejado
dados_renovaveis = dados_renovaveis.rename(columns={
    'BARRA_x': 'BARRA',
    'CODIGODAUSINA_x': 'CODIGODAUSINA',
    'PERCENTUAL RATEIO_x': 'PERCENTUAL RATEIO'
})

usinas_sem_link_Conjunto_renovaveis = dados_renovaveis[
    ((dados_renovaveis["Tipo"].str.strip() == "UEE") |
     (dados_renovaveis["Tipo"].str.strip() == "UFV")) &
    pd.isna(dados_renovaveis["BARRA"])
].copy()

# Salvar a cópia filtrada em um arquivo Excel
usinas_sem_link_Conjunto_renovaveis.to_excel("Usinas sem link renovaveis e Conjuntos.xlsx", index=False)

# Aplicar os filtros no dataframe original
dados_renovaveis = dados_renovaveis[
    ((dados_renovaveis["Tipo"].str.strip() == "UEE") |
     (dados_renovaveis["Tipo"].str.strip() == "UFV"))  # Filtrar apenas "UEE" e "UFV" na coluna "Tipo"
].dropna(subset=["BARRA"])  # Remover valores nulos na coluna "BARRA"

# Remove duplicatas com base nas colunas "CODIGO" e "CODIGODAUSINA"
dados_renovaveis = dados_renovaveis.drop_duplicates(subset=["CODIGO", "CODIGODAUSINA"])

def gerar_horas(data):
    # Converter o formato DDMMAAAA para DD/MM/YYYY
    data_str = datetime.strptime(data, "%d%m%Y").strftime("%d/%m/%Y")

    # Criar uma lista de horários de 30 em 30 minutos
    horarios = []
    hora_atual = datetime.strptime(data_str + " 00:00", "%d/%m/%Y %H:%M")

    for i in range(48):  # 48 intervalos de 30 minutos (24 horas)
        horarios.append(hora_atual.strftime("%d/%m/%Y %H:%M"))
        hora_atual += timedelta(minutes=30)

    return horarios


# Gerar os horários para a data externa
horarios_gerados = gerar_horas(data_variavel)

# Agora, vamos expandir cada linha do DataFrame para ter 48 horários (uma vez para cada intervalo de 30 minutos)
# Isso irá repetir os 48 horários para cada linha do DataFrame
dados_renovaveis['dia_hora'] = [horarios_gerados] * len(dados_renovaveis)

# Explodir a lista de horários em múltiplas linhas (48 horários por linha)
dados_renovaveis = dados_renovaveis.explode('dia_hora').reset_index(drop=True)

# Adicionar a coluna 'dia' com o valor do dia (no formato DD)
dados_renovaveis['dia'] = int(datetime.strptime(data_variavel, "%d%m%Y").strftime("%d"))

# Adicionar a coluna 'hora' com a hora correspondente de 1 a 24
dados_renovaveis['hora'] = dados_renovaveis['dia_hora'].apply(lambda x: int(x.split()[1].split(":")[0]))

# Adicionar a coluna 'mh' (0 para hora cheia, 1 para 30 minutos)
dados_renovaveis['mh'] = dados_renovaveis['dia_hora'].apply(lambda x: 1 if x.split()[1].split(":")[1] == "30" else 0)

# Inserir a coluna 'Geração_rateada' com valores nulos
dados_renovaveis.insert(9, 'Geração', pd.NA)

# Inserir a coluna 'Geração_rateada' com valores nulos
dados_renovaveis.insert(10, 'Geração_rateada', pd.NA)

# Criando o dicionário de mapeamento das usinas que não obteve dados
mapeamento = {
    "BAECAU": "BAEACU",
    "RNAWD1": "RNEAW1",
    "RNAWD2": "RNEAW2",
    "SCUBJD": "SCUBJS",
    "RNCA01": "RNST1",
    "RNCA02": "RNST2",
    "RNCA03": "RNST3",
    "RNCA04": "RNST5",
    "RNCA5": "RNST10",
    "RNCA06": "RNST13",
    "RNCA07": "RNST14",
    "RNCB11": "RNST7",
    "RNCB12": "RNST4",
    "BAEURW": "BAEU23",
    "BAEURC": "BAEU03",
    "BAEURE": "BAEU05",
    "BAEURF": "BAEU06",
    "BAEUR8": "BAEU08",
    "RNUEV1": "RNUE01",
    "RNUEVX": "RNUE10",
    "RNUEV2": "RNUE02",
    "RNUEV3": "RNUE03",
    "RNUEV4": "RNUE04",
    "RNUEV5": "RNUE05",
    "RNUEV6": "RNUE06",
    "RNUEV7": "RNUE07",
    "RNUEV8": "RNUE08",
    "RNUEV9": "RNUE09",
    "PIVSA1": "PISA01",
    "PIEES1": "PEEES1",
    "PIEES2": "PEEES2",
    "PIEES3": "PEEES3",
    "PIEES4": "PEEES4",
    "PIEES5": "PEEES5",
    "PIVSR1": "PISR01",
    "PIVSR2": "PISR02",
    "PIVSR3": "PISR04",
    "PIVSR4": "PISR08",
    "PIVSR5": "PISR11",
    "PIVSR6": "PISR16",
    "PIVSR7": "PISR17",
    "PIVSR8": "PISR18",
    "CEEVIT": "CEEVTI",
    "BAEURI": "BAEU09",
    "BAEURY": "BAEU25",
    "RNUER3": "RNUER1",
    "RNUES3": "RNUES3",
    "PIESAT": "PICG01",
    "PIESVA": "PICG02",
    "PIESAP": "PICG03",
    "PIESMO": "PICG04",
    "PIESVR": "PICG05",
    "PIESFE": "PICG06",
    "PIESBL": "PICG07",
    "PEFBR1": "PEFBRI",
    "SPUD41": "SPUFD4",
    "SPAGV4": "SPUFA4",
    "SPAGV5": "SPUFA5",
    "SPAGV6": "SPUFA6",
    "SPCS01": "SPUFC1",
    "PEBE15": "PEBE11",
    "BAECLA": "BAEC01",
    "BAECLB": "BAEC02",
    "BAECLC": "BAEC03",
    "BAECLD": "BAEC04",
    "BAECLE": "BAEC05",
    "BAECLF": "BAEC06",
    "BAECLG": "BAEC07",
    "BAECLO": "BAEC15",
    "BAECLP": "BAEC16",
    "BAECLR": "BAEC18",
    "BAECLU": "BAEC21",
    "BAEURA": "BAEU01",
    "BAEURB": "BAEU02",
    "BAEURJ": "BAEU10",
    "BAEURK": "BAEU11",
    "BAEURM": "BAEU13",
    "BAEURO": "BAEU15",
    "BAEURP": "BAEU16",
    "BAEURQ": "BAEU17",
    "BAEURR": "BAEU18",
    "BAEURS": "BAEU19",
    "BAEURU": "BAEU21",
    "CEJAI": "CEEJAU",
    "CEJAN": "CEEJAI",
    "CENSF": "CEENSF",
    "CESCL": "CEESCL",
    "CESJN": "CEESJN",
    "MAEDS3": "MAEDC2",
    "MAEDT9": "MAEDC1",
    "PEESV6": "PEESV7",
    "RNAWD3": "RNEAW3",
    "RNB13": "RNSR10",
    "RNB16": "RNST8",
    "RNCB09": "RNSR11",
    "RNCB14": "RNSR3",
    "RNCB15": "RNSR4",
    "RSEVS2": "RSESG2",
    "RSEVS3": "RSESG3",
    "RSREB1": "RSUECU",
    "RSREB2": "RSUECD",
    "RSREB3": "RSUECT",
    "BAAR01": "BAPP01",
    "BAAR02": "BAPP02",
    "BAAR03": "BAPP03",
    "BAAR04": "BAPP04",
    "BAAR05": "BAAR07",
    "BAAR06": "BAAR08",
    "BAEDF7": "BAEDF8",
    "BAEJCE": "BAEFDS",
    "BAUESJ": "BAUEPR",
    "BAEIM2": "BAEACU",
    "BAACA1": "BAATN1",
    "BAACA2": "BAATN2",
    "BAACA3": "BAATN3"
}

# Substituindo os valores na coluna "CODIGODAUSINA"
dados_renovaveis["CODIGODAUSINA"] = dados_renovaveis["CODIGODAUSINA"].replace(mapeamento)

# Exportar para um arquivo Excel
#dados_renovaveis.to_excel("dados_renovaveis antes.xlsx", index=False)

df_geracao_EOL['din_instante'] = pd.to_datetime(df_geracao_EOL['din_instante'])

# Formatar a coluna 'din_instante' no formato desejado
df_geracao_EOL['din_instante'] = df_geracao_EOL['din_instante'].dt.strftime('%d/%m/%Y %H:%M')

# Realizar o merge entre os DataFrames após a conversão dos tipos de dados
merged_df = pd.merge(dados_renovaveis, df_geracao_EOL, left_on=['CODIGODAUSINA', 'dia_hora'], right_on=['id_ons', 'din_instante'], how='left')

# Atualizar a coluna 'CÓDIGO RENOVÁVEIS' no df Conjunto_rateio com o valor da coluna 'CODIGO' do df dados_renovaveis
dados_renovaveis['Geração'] = merged_df['val_geracaoverificada']

# Exportar para um arquivo Excel
#dados_renovaveis.to_excel("dados_renovaveis depois.xlsx", index=False)

df_geracao_UFV['din_instante'] = pd.to_datetime(df_geracao_UFV['din_instante'])

# Formatar a coluna 'din_instante' no formato desejado
df_geracao_UFV['din_instante'] = df_geracao_UFV['din_instante'].dt.strftime('%d/%m/%Y %H:%M')

# Realizar o merge entre os DataFrames após a conversão dos tipos de dados
merged_df = pd.merge(dados_renovaveis, df_geracao_UFV, left_on=['CODIGODAUSINA', 'dia_hora'], right_on=['id_ons', 'din_instante'], how='left')

# Substituir apenas os valores vazios na coluna 'Geração'
dados_renovaveis['Geração'] = dados_renovaveis['Geração'].fillna(merged_df['val_geracaoverificada'])

# Exportar para um arquivo Excel
dados_renovaveis.to_excel("dados_renovaveis depois_UFV.xlsx", index=False)

dados_renovaveis["Geração_rateada"] = dados_renovaveis["Geração"] * (dados_renovaveis["PERCENTUAL RATEIO"] / 100).round(2)

# Converter para float e arredondar para duas casas decimais
dados_renovaveis["Geração_rateada"] = dados_renovaveis["Geração_rateada"].astype(float).round(2)

# Exportar para um arquivo Excel
#dados_renovaveis.to_excel("dados_renovaveis rateado.xlsx", index=False)

# Filtrar valores nulos na coluna "Geração" e "hora" e "mh" iguais a zero
usinas_sem_link_renovaveis_geracao = dados_renovaveis[
    (dados_renovaveis["Geração"].isna()) &
    (dados_renovaveis["hora"] == 0) &
    (dados_renovaveis["mh"] == 0)
].copy()  # Copia o DataFrame para evitar alterações no original

# Verificar se há mais de 10 linhas
if len(usinas_sem_link_renovaveis_geracao) > 10:
    print("⚠️ Alerta: Possui mais de 10 usinas sem link com o dados abertos!")

# Exportar para um arquivo Excel
usinas_sem_link_renovaveis_geracao.to_excel("Usinas sem_link renovaveis geracao.xlsx", index=False)

# 1. Identificar os códigos que possuem pelo menos uma linha nula
codigos_com_nulos = dados_renovaveis.loc[
    dados_renovaveis["Geração_rateada"].isna(), "CODIGO"
].unique()

# 2. Filtrar linhas válidas **somente** desses códigos
dados_filtrados = dados_renovaveis[
    dados_renovaveis["CODIGO"].isin(codigos_com_nulos) &
    dados_renovaveis["Geração_rateada"].notna()
]

# 3. Calcular médias por CODIGO, hora, mh
medias = (
    dados_filtrados
    .groupby(["CODIGO", "hora", "mh"])["Geração_rateada"]
    .mean()
    .reset_index()
    .rename(columns={"Geração_rateada": "media_rateada"})
)

# 4. Selecionar linhas nulas para preenchimento
linhas_nulas = dados_renovaveis[
    dados_renovaveis["Geração_rateada"].isna() &
    dados_renovaveis["CODIGO"].isin(codigos_com_nulos)
]

# 5. Preencher nulos com as médias correspondentes
linhas_corrigidas = linhas_nulas.merge(
    medias,
    on=["CODIGO", "hora", "mh"],
    how="left"
)

linhas_corrigidas["Geração_rateada"] = linhas_corrigidas["media_rateada"]

# 6. Atualizar DataFrame original
dados_renovaveis_atualizado = pd.concat([
    dados_renovaveis[~dados_renovaveis.index.isin(linhas_nulas.index)],
    linhas_corrigidas.drop(columns=["media_rateada"])
]).sort_index()


# Exportar para um arquivo Excel
#dados_renovaveis.to_excel("dados_renovaveis rateado com médias.xlsx", index=False)


#remover as linhas onde a geração é nula
dados_renovaveis = dados_renovaveis.dropna(subset=["Geração_rateada"])


# Função personalizada para concatenar as strings separadas por "/"
def concat_strings(series):
    return '/'.join(series)

# Agrupar pelos campos "CODIGO" e "dia_hora", somar "Geração_rateada" e concatenar as strings
Bloco_geracao = dados_renovaveis.groupby(['CODIGO', 'dia_hora'], as_index=False).agg(
    Nome=('Nome', concat_strings),
    CODIGODAUSINA=('CODIGODAUSINA', concat_strings),
    Modalidade=('Tipo', 'first'),
    Geração_rateada_sum=('Geração_rateada', 'sum'),
    dia_hora=('dia_hora','first'),
    dia = ('dia', 'first'),
    hora=('hora', 'first'),
    mh=('mh', 'first')
)

# Garantir que a coluna 'dia_hora' esteja no formato datetime
Bloco_geracao['dia_hora'] = pd.to_datetime(Bloco_geracao['dia_hora'], format='%d/%m/%Y %H:%M')

# Criar a coluna 'dia_hora_fim' com o valor de 'dia_hora' + 30 minutos
Bloco_geracao['dia_hora_fim'] = Bloco_geracao['dia_hora'] + pd.Timedelta(minutes=30)

# Adicionar a coluna 'dia' com o valor do dia (no formato DD)
Bloco_geracao['diaf'] = Bloco_geracao['dia_hora_fim'].apply(lambda x: x.day)

# Adicionar a coluna 'hora' com a hora correspondente de 1 a 24
Bloco_geracao['horaf'] = Bloco_geracao['dia_hora_fim'].apply(lambda x: x.hour)

# Adicionar a coluna 'mh' (0 para hora cheia, 1 para 30 minutos)
Bloco_geracao['mhf'] = Bloco_geracao['dia_hora_fim'].apply(lambda x: 1 if x.minute == 30 else 0)

Bloco_geracao = Bloco_geracao.drop(columns=['dia_hora_fim'])

Bloco_geracao = Bloco_geracao.drop(columns=['dia_hora'])

# Exportar para um arquivo Excel
Bloco_geracao.to_excel("Bloco_geracao.xlsx", index=False)

dados_renovaveis_geracao["CODIGO"] = dados_renovaveis_geracao["CODIGO"].astype(int)
dados_renovaveis_geracao["di"] = dados_renovaveis_geracao["di"].astype(int)
dados_renovaveis_geracao["hri"] = dados_renovaveis_geracao["hri"].astype(int)
dados_renovaveis_geracao["mi"] = dados_renovaveis_geracao["mi"].astype(int)
dados_renovaveis_geracao["df"] = dados_renovaveis_geracao["df"].astype(int)
dados_renovaveis_geracao["hrf"] = dados_renovaveis_geracao["hrf"].astype(int)
dados_renovaveis_geracao["mf"] = dados_renovaveis_geracao["mf"].astype(int)

# Para a coluna "GERACAO", converta para float
dados_renovaveis_geracao["GERACAO"] = dados_renovaveis_geracao["GERACAO"].astype(float)

renovaveis_antes = dados_renovaveis_geracao.copy()

#renovaveis_antes.to_excel('renovaveis_antes.xlsx', index=False)

# Cria uma lista com os valores únicos da coluna 'CODIGO'
lista_codigos = Bloco_geracao['CODIGO'].unique().tolist()

dia_extraido = int(data_variavel[:2])  # Extrai o dia da data_variavel

# Criando uma lista para armazenar as novas linhas
novas_linhas = []

print("-----------------------------------------------")
print("Iniciando exportação de dados bloco geração")
print("-----------------------------------------------")

lista_usinas_zeradas = []

# Iterando por cada código
for codigo in lista_codigos:
    # Filtrando as linhas para o código específico
    df_codigo = dados_renovaveis_geracao[dados_renovaveis_geracao['CODIGO'] == codigo]

    # Verificando se existe uma linha com 'di' igual ao dia extraído, 'hri' igual a 23 e 'mi' igual a 0
    linha_condicao = df_codigo[(df_codigo['di'] == dia_extraido) & (df_codigo['hri'] == 23) & (df_codigo['mi'] == 0)]

    # Se não existir essa linha
    if linha_condicao.empty:
        # Procura a última linha com 'di' igual ao dia extraído de data_variavel
        ultima_linha = df_codigo[df_codigo['di'] == dia_extraido].iloc[-1]

        # Duplicando a linha, ajustando o valor de "di"
        nova_linha = ultima_linha.copy()
        nova_linha['di'] = ultima_linha['di'] + 1  # Adiciona 1 ao valor de di
        nova_linha['hri'] = 0  # Atualiza hri para 0
        nova_linha['mi'] = 0  # Atualiza mi para 0

        # Encontrando o índice da última linha com 'di' igual ao dia extraído
        index_ultima_linha = df_codigo[df_codigo['di'] == dia_extraido].index[-1]

        # Adiciona a nova linha logo após a última linha
        novas_linhas.append((index_ultima_linha, nova_linha))

        lista_usinas_zeradas.append(int(nova_linha['CODIGO']))

# Inserindo as novas linhas no DataFrame original
for index, nova_linha in novas_linhas:
    dados_renovaveis_geracao = pd.concat([dados_renovaveis_geracao.iloc[:index + 1], pd.DataFrame([nova_linha]),
                                          dados_renovaveis_geracao.iloc[index + 1:]]).reset_index(drop=True)

#dados_renovaveis_geracao.to_excel('renovaveis_meio.xlsx', index=False)

dados_renovaveis_geracao = dados_renovaveis_geracao[~((dados_renovaveis_geracao['di'] == dia_extraido) &
                                          (dados_renovaveis_geracao['CODIGO'].isin(lista_codigos)))]

# Lista para armazenar as novas linhas que serão adicionadas
novas_linhas = []

# Iterar sobre cada código na lista de códigos únicos
for codigo in lista_codigos:

    # Obter as 48 linhas do df_bloco_geracao para o código atual
    linhas_geracao = Bloco_geracao[Bloco_geracao['CODIGO'] == int(codigo)].head(48)

    # Para cada uma das 48 linhas, ajustar os valores conforme necessário
    for _, linha_bloco in linhas_geracao.iterrows():
        nova_linha = {
            'CODIGO': codigo,
            'GERACAO': linha_bloco['Geração_rateada_sum'],
            'di': linha_bloco['dia'],
            'hri': linha_bloco['hora'],
            'mi': linha_bloco['mh'],
            'df': linha_bloco['diaf'],
            'hrf': linha_bloco['horaf'],
            'mf': linha_bloco['mhf'],
            '&': 'EOLICA-GERACAO'  # Adicionando "EOLICA-GERACAO" na coluna "&"
        }
        novas_linhas.append(nova_linha)

# Converter a lista de novas linhas para um DataFrame
df_novas_linhas = pd.DataFrame(novas_linhas)

# Concatenar as novas linhas ao DataFrame original
dados_renovaveis_geracao = pd.concat([dados_renovaveis_geracao, df_novas_linhas], ignore_index=True)

#dados_renovaveis_geracao.to_excel('renovaveis_depois.xlsx', index=False)

print("-----------------------------------------------")
print("Iniciando processo de escrita do renovaveis")
print("-----------------------------------------------")


# Abrir o arquivo renovaveis.dat no modo leitura e escrita
with open('renovaveis.dat', 'r+') as f:
    lines = f.readlines()  # Lê todas as linhas do arquivo

    # Encontrar a linha que começa com 'EOLICA-GERACAO'
    for i, line in enumerate(lines):
        if line.startswith("EOLICA-GERACAO"):
            start_line_index = i
            break
    else:
        start_line_index = None  # Caso a linha não seja encontrada

    # Se a linha for encontrada, substituímos a partir dessa linha
    if start_line_index is not None:
        # Apagar a partir da linha EOLICA-GERACAO
        lines = lines[:start_line_index]

        # Escrever as novas linhas com base no df
        for _, row in dados_renovaveis_geracao.iterrows():
            geracao_value = row['GERACAO']

            # Verifica se GERACAO é um número float com casas decimais
            if isinstance(geracao_value, float) and geracao_value.is_integer():
                geracao_value = int(geracao_value)  # Converte para inteiro, se for o caso
            else:
                # Arredondar para 2 casas decimais
                geracao_value = round(geracao_value, 2)

            # Formatando a linha com o valor arredondado
            new_line = (
                    f"{row['&']:4}; "
                    + f"{row['CODIGO']:4} ;"
                    + f"{row['di']:2} ;"
                    + f"{row['hri']:2} ;"
                    + f"{row['mi']:1} ;"
                    + f"{row['df']:2} ;"
                    + f"{row['hrf']:2} ;"
                    + f"{row['mf']:1} ;"
                    + f"{geracao_value:10} ;\n"  # Formato adequado para GERACAO
            )
            lines.append(new_line)

        # Voltar ao início do arquivo e sobrescrever com as novas linhas
        f.seek(0)
        f.writelines(lines)
    else:
        print("Não foi encontrada a linha que começa com 'EOLICA-GERACAO'.")


