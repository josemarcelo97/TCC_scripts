import os
import shutil
import pandas as pd
from datetime import datetime, timedelta, time

#Caminho com os arquivos da rodada
caminho_rodada = #Caminho com os arquivos do deck

#Caminho para os arquivos excel necessários para os ajustes
caminho_arquivos = #Caminho com os excel com os dados das Hidraulicas

#Nome dos arquivos excel
hidri_mensal = #Nome da planilha com os dados mensais
hidri_horario = #Nome da planilha com os dados horário

# Nome do arquivo Excel
hidraulicos_path = "Hidraulicos.xlsx"

#Nome dos arquivos alterados na rodada
dadvaz = caminho_rodada + '/dadvaz.dat'
dadvaz_cop = caminho_rodada + '/dadvaz_backup.dat'

deflant = caminho_rodada + '/deflant.dat'
deflant_cop = caminho_rodada + '/deflant_backup.dat'

entdados = caminho_rodada + '/entdados.dat'
entdados_cop = caminho_rodada + '/entdados_backup.dat'

cotasr11 = caminho_rodada +'/cotasr11.dat'
cotasr11_cop = caminho_rodada +'/cotasr11_backup.dat'

curv = caminho_rodada + '/curvtviag.dat'

#Entrar com a data da rodada
data = input('Entre com a data (DDMMAAAA): ')

os.chdir(caminho_arquivos)

print("-----------------------------------------------")
print("Iniciando leitura dos dados")
print("-----------------------------------------------")

#Inicio ao processo referente ao Dadvaz
data_formatada = datetime.strptime(data, "%d%m%Y").strftime("%Y-%m-%d")
data_dia = datetime.strptime(data, "%d%m%Y").strftime("%d")

# Ler os arquivos em excel e guardar em dataframe
df_hidri_mensal = pd.read_excel(hidri_mensal)

# Inicio do DEFLANT e partidas no bloco UH
df_hidri_horario = pd.read_excel(hidri_horario)

df_hidri_mensal.drop(columns=[
    'val_nivelmontante', 'val_niveljusante', 'val_volumeutilcon',
    'val_vazaoafluente', 'val_vazaoturbinada', 'val_vazaovertida',
    'val_vazaooutrasestruturas', 'val_vazaodefluente', 'val_vazaotransferida',
    'val_vazaonatural', 'val_vazaoartificial', 'val_vazaoevaporacaoliquida',
    'val_vazaousoconsuntivo', 'val_vazaoincrementalbruta'
], inplace=True)# para armazenar os valores



df_hidri_mensal = df_hidri_mensal[df_hidri_mensal['din_instante'] == data_formatada]

os.chdir(caminho_rodada)
shutil.copy(dadvaz, dadvaz_cop)

# Criando uma lista para armazenar os dados antes de criar o DataFrame
dados_dadvaz = []

# Abrindo o arquivo e processando as linhas a partir da 16ª (índice 15)
with open("dadvaz.dat", "r", encoding="utf-8") as arquivo:
    for i, linha in enumerate(arquivo):
        if i >= 16 and linha[:3] != 'FIM':  # Ignora as primeiras 15 linhas
            num = int(linha[:3])  # Pegando os primeiros 3 caracteres como inteiro
            nome = linha[4:16].strip()  # Pegando do índice 4 ao 17 e removendo espaços
            itp = int(linha[19:20])  # Pegando o índice 20 e convertendo para inteiro
            di = linha[24:26]  # Pegando do índice 24 ao 26 como string
            vazao = int(linha[44:53])  # Pegando do índice 44 ao 53 como inteiro

            # Adicionando ao array de dados
            dados_dadvaz.append([num, nome, itp, di, vazao])

# Criando o DataFrame
df_dadvaz = pd.DataFrame(dados_dadvaz, columns=["NUM", "NOME", "ITP", "DI", "VAZAO"])

# Removendo os dados que não devem ser atualizados
df_dadvaz = df_dadvaz[df_dadvaz['DI'] == data_dia]

df_dadvaz = df_dadvaz.merge(
    df_hidri_mensal[["cod_usina", "val_vazaoincremental"]],
    left_on="NUM", right_on="cod_usina",
    how="left"
)

# Renomeando a coluna para "vazao_verificada"
df_dadvaz.rename(columns={"val_vazaoincremental": "vazao_verificada"}, inplace=True)

# Removendo a coluna auxiliar "cod_usina", caso não seja necessária
df_dadvaz.drop(columns=["cod_usina"], inplace=True)

df_dadvaz["vazao_verificada"] = df_dadvaz["vazao_verificada"].astype(float).round(2)

#Removendo a linha cujo está com valor vazio
df_dadvaz = df_dadvaz.dropna(subset=['vazao_verificada'])


df_dadvaz.to_excel('Hidraulicos.xlsx', sheet_name='dadvaz', index=False)


df_hidri_horario.drop(columns=[
    'val_niveljusante', 'val_vazaoafluente', 'val_vazaoturbinada', 'val_vazaovertida',
    'val_vazaooutrasestruturas', 'val_vazaovertidanaoturbinavel', 'val_vazaotransferida'
], inplace=True)# para armazenar os valores

# Converter a coluna para datetime
df_hidri_horario['din_instante'] = pd.to_datetime(df_hidri_horario['din_instante'])

# Criar as colunas 'data' e 'hora'
df_hidri_horario['data'] = df_hidri_horario['din_instante'].dt.date
df_hidri_horario['hora'] = df_hidri_horario['din_instante'].dt.time

# Converter data_formatada para datetime.date
data_formatada = datetime.strptime(data_formatada, "%Y-%m-%d").date()
data_formatada_menos_um = data_formatada - timedelta(days=1)
dia_menos_um = data_formatada_menos_um.strftime("%d")

# Remover a coluna original
df_hidri_horario.drop(columns=['din_instante'], inplace=True)

df_hidri_horario = df_hidri_horario[df_hidri_horario['data'] == data_formatada_menos_um]

# Função para subtrair 1 hora e formatar para HH:MM
def subtrair_uma_hora(hora_obj):
    # Converter a hora para datetime para manipulação
    hora = datetime.combine(datetime.today(), hora_obj)  # Combina com a data para manipulação

    # Se for "23:59:00", subtrai 59 minutos
    if hora_obj == datetime.strptime('23:59:00', '%H:%M:%S').time():
        hora -= timedelta(minutes=59)
    else:
        # Caso contrário, subtrai 1 hora
        hora -= timedelta(hours=1)

    # Retornar no formato HH:MM
    return hora.strftime('%H:%M')


# Aplicando a função à coluna 'hora'
df_hidri_horario['hora'] = df_hidri_horario['hora'].apply(subtrair_uma_hora)

os.chdir(caminho_rodada)
shutil.copy(deflant, deflant_cop)

# Criando uma lista para armazenar os dados antes de criar o DataFrame
dados_deflant = []

# Abrindo o arquivo e processando as linhas a partir da 16ª (índice 15)
with open("deflant.dat", "r", encoding="utf-8") as arquivo:
    for i, linha in enumerate(arquivo):
        if i >= 5:  # Ignora as primeiras 4 linhas
            X = linha[:6]
            num = int(linha[9:12])
            Jus = linha[14:17]
            TpJ = linha[19:20]
            di = linha[24:26]
            hi = int(linha[27:29])
            m = int(linha[30:31])
            df = linha[32:34]
            dat = None
            vazao = int(linha[44:54])

            # Adicionando ao array de dados
            dados_deflant.append([X, num, Jus, TpJ, di, hi, m, df, dat, vazao])

# Criando o DataFrame
df_deflant = pd.DataFrame(dados_deflant, columns=["X", "num", "Jus", "TpJ", "di", "hi", "m",
                                                  "df", "dat", "vazao"])

# Função para calcular a hora no formato HH:MM
def calcular_hora(row):
    hora = int(row['hi'])  # Garantindo que 'hi' seja inteiro
    if row['m'] == 0:
        return f"{hora:02d}:00"
    else:
        return f"{hora:02d}:30"

# Preenchendo a coluna 'dat' com o formato HH:MM
df_deflant['dat'] = df_deflant.apply(calcular_hora, axis=1)

df_deflant.loc[(df_deflant['di'] == dia_menos_um) & (df_deflant['dat'] == '00:00'), 'dat'] = '23:00'

# Remover as linhas onde é igual o SANTONIO CM estava causando duplicadas
df_hidri_horario = df_hidri_horario[df_hidri_horario['id_reservatorio'] != 'DCSACM']

# Realizando o merge entre df_hidri_horario e df_deflant, mantendo df_deflant como o DataFrame final
df_deflant = pd.merge(df_deflant, df_hidri_horario[['cod_usina', 'hora', 'val_vazaodefluente']],
                      left_on=['num', 'dat'], right_on=['cod_usina', 'hora'],
                      how='left')

df_deflant.drop(columns=[
    'hora', 'cod_usina',
], inplace=True)

# Apaga os valores da coluna 'val_vazaodefluente' onde 'di' é diferente de 'dia_menos_um'
df_deflant.loc[df_deflant['di'] != dia_menos_um, 'val_vazaodefluente'] = None

# Usando ExcelWriter para adicionar uma nova aba ao arquivo existente
with pd.ExcelWriter(hidraulicos_path, engine='openpyxl', mode='a') as writer:
    df_deflant.to_excel(writer, sheet_name='Deflant', index=False)

# Remover as linhas onde 'val_vazaodefluente' é NaN, 'num' é 66 ou 83, e 'm' é 1
df_deflant = df_deflant[~(
    df_deflant['val_vazaodefluente'].isna() &  # 'val_vazaodefluente' é NaN
    df_deflant['num'].isin([66, 83, 287]) &  # 'num' é 66 ou 83
    (df_deflant['m'] == 1)  # 'm' é igual a 1
)]

# Substitui os valores 'NaN' na coluna 'val_vazaodefluente' pelos valores correspondentes da coluna 'vazão'
df_deflant['val_vazaodefluente'] = df_deflant['val_vazaodefluente'].fillna(df_deflant['vazao'])


# Inicio do nível das usinas no entdados

# Verificar se o arquivo entdados_backup já existe
if not os.path.exists(entdados_cop):
    # Copiar o arquivo 'entdados.dat' para 'entdados_backup.dat'
    shutil.copy(entdados, entdados_cop)

df_hidri_horario = df_hidri_horario[df_hidri_horario['hora'] == '23:00']

dados_entdados = []

with open("entdados.dat", "r", encoding="utf-8") as arquivo:
    for linha in arquivo:
        # Verificar se a linha tem pelo menos 4 caracteres e se começa com 'UH  '
        if len(linha) >= 4 and linha[:4] == 'UH  ':  # pegando informações do bloco UH
            ind = int(linha[4:7])
            nome = str(linha[9:21]).strip()
            Vinic = linha[29:35]

            # Adicionando ao array de dados
            dados_entdados.append([ind, nome, Vinic])

# Criando o DataFrame
df_entdados = pd.DataFrame(dados_entdados, columns=["ind", "nome", "Vinic"])

# Realizando o merge entre os DataFrames
df_entdados = df_entdados.merge(df_hidri_horario[['cod_usina', 'val_volumeutil']],
                                left_on='ind',
                                right_on='cod_usina',
                                how='left')

# Renomeando a coluna 'val_volumeutil' para 'volume_util'
df_entdados.rename(columns={'val_volumeutil': 'volume_util'}, inplace=True)

df_entdados = df_entdados.drop(columns=['cod_usina'])  # Remove a coluna cod_usina

df_entdados.loc[df_entdados['ind'].isin([66, 46, 287]), 'volume_util'] = None

# Usando ExcelWriter para adicionar uma nova aba ao arquivo existente
with pd.ExcelWriter(hidraulicos_path, engine='openpyxl', mode='a') as writer:
    df_entdados.to_excel(writer, sheet_name='NP_entdados', index=False)

df_entdados = df_entdados.dropna(subset=['volume_util'])  # Remove as linhas com volume_util vazio
df_entdados = df_entdados[df_entdados["volume_util"] >= 0] # Remove as linhas com volume_util negativo
df_entdados = df_entdados[df_entdados["volume_util"] <= 100] # Remove as linhas com volume_util maiores que 100
df_entdados = df_entdados[~df_entdados['ind'].isin([66, 46, 287])]

data_formatada_menos_dois = data_formatada - timedelta(days=2)

os.chdir(caminho_arquivos)

# Inicio do DEFLANT e partidas no bloco UH
df_hidri_horario = pd.read_excel(hidri_horario)

df_hidri_horario.drop(columns=[
    'val_niveljusante', 'val_vazaoafluente', 'val_vazaoturbinada', 'val_vazaovertida',
    'val_vazaooutrasestruturas', 'val_vazaovertidanaoturbinavel', 'val_vazaotransferida'
], inplace=True)# para armazenar os valores

os.chdir(caminho_rodada)
shutil.copy(cotasr11, cotasr11_cop)

# Criando uma lista para armazenar os dados antes de criar o DataFrame
dados_cotas = []

# Abrindo o arquivo e processando as linhas a partir da 16ª (índice 15)
with open("cotasr11.dat", "r", encoding="utf-8") as arquivo:
    for i, linha in enumerate(arquivo):
        if i >= 2: # Ignora as primeiras 2 linhas
            d = int(linha[:3])  # Pegando os primeiros 2 caracteres como inteiro
            hh = int(linha[3:5])  # Pegando do índice 3 ao 5 e removendo espaços
            m = int(linha[6:7])  # Pegando o índice 7 e convertendo para inteiro
            cotR11 = float(linha[16:26])  # Pegando do índice 24 ao 26 como string

            # Adicionando ao array de dados
            dados_cotas.append([d, hh, m, cotR11])

# Criando o DataFrame
df_cotas = pd.DataFrame(dados_cotas, columns=["d", "hh", "m", "cotR11"])

# Criando uma lista para armazenar os dados antes de criar o DataFrame
dados_curv = []

# Abrindo o arquivo e processando as linhas a partir da 16ª (índice 15)
with open("curvtviag.dat", "r", encoding="utf-8") as arquivo:
    for i, linha in enumerate(arquivo):
        if i >= 2 and linha[:1] != '&':
            MONT = int(linha[9:12])
            hora = int(linha[32:34])
            acum = int(linha[41:44])

            # Adicionando ao array de dados
            dados_curv.append([MONT, hora, acum])

# Criando o DataFrame
df_curv = pd.DataFrame(dados_curv, columns=["MONT", "hora", "acum"])
# Converter a coluna "hora" do df_curv para numérico, tratando erros
df_curv['hora'] = pd.to_numeric(df_curv['hora'], errors='coerce')  # Transforma erros em NaN
df_curv = df_curv.dropna(subset=['hora'])  # Remove valores inválidos
df_curv['hora'] = df_curv['hora'].astype(int)  # Converte para inteiro

# Criar uma nova coluna para armazenar se o dia precisa ser incrementado
df_curv['incrementa_dia'] = df_curv['hora'] == 24  # Flag para indicar hora 24

# Substituir hora 24 por 0 para manter o formato válido
df_curv.loc[df_curv['hora'] == 24, 'hora'] = 0

# Converter a coluna "hora" para datetime.time
df_curv['hora'] = df_curv['hora'].apply(lambda x: time(x, 0, 0))

# Supondo que sua coluna 'din_instante' esteja no formato datetime
df_hidri_horario['din_instante'] = pd.to_datetime(df_hidri_horario['din_instante'])

# Criando novas colunas para data e hora
df_hidri_horario['data'] = df_hidri_horario['din_instante'].dt.date
df_hidri_horario['hora'] = df_hidri_horario['din_instante'].dt.time

df_hidri_horario = df_hidri_horario[(df_hidri_horario['data'] == data_formatada_menos_dois) | (df_hidri_horario['data'] == data_formatada_menos_um)]

# Filtrar apenas as linhas onde 'cod_usina' seja 66 ou 83
df_hidri_horario = df_hidri_horario[df_hidri_horario['cod_usina'].isin([66, 83])]

# Converter 'hora' para datetime para facilitar operações
df_hidri_horario['hora'] = pd.to_datetime(df_hidri_horario['hora'], format='%H:%M:%S')

# Abater 1 hora de todas as linhas
df_hidri_horario['hora'] = df_hidri_horario['hora'] - timedelta(hours=1)

# Ajustar a exibição da hora apenas (sem a data associada ao datetime)
df_hidri_horario['hora'] = df_hidri_horario['hora'].dt.time

# Substituir 22:59 por 23:00
df_hidri_horario.loc[df_hidri_horario['hora'] == pd.to_datetime('22:59', format='%H:%M').time(), 'hora'] = pd.to_datetime('23:00', format='%H:%M').time()

#df_hidri_horario.to_excel("df_hidri_horario.xlsx", index=False)

df_hidri_horario['cod_usina'] = df_hidri_horario['cod_usina'].fillna(0).astype(int)

# Criando o DataFrame deflu_acum vazio
deflu_acum = pd.DataFrame(columns=['cod', 'data', 'hora', 'deflu'])
# Lista para armazenar as novas linhas
linhas = []

def convert_to_time(x):
    if isinstance(x, str):  # Se for uma string no formato 'HH:MM:SS'
        return datetime.strptime(x, '%H:%M:%S').time()
    elif isinstance(x, time):  # Se já for um objeto datetime.time
        return x
    return x  # Retorna o valor original se não for nem string nem time

# Aplicar a conversão na coluna 'hora' de df_curv
df_curv['hora'] = df_curv['hora'].apply(convert_to_time)

# Lista para armazenar os novos valores
linhas = []

# Percorrer cada linha do df_hidri_horario
for _, row_hidri in df_hidri_horario.iterrows():
    # Zerar o fator acumulado a cada iteração do df_hidri_horario
    fator_acumulado_anterior = 0

    cod_usina = int(row_hidri['cod_usina'])
    data = row_hidri['data']
    hora_hidri = row_hidri['hora'].hour  # Pegamos apenas a hora do hidri
    val_vazao = row_hidri['val_vazaodefluente']

    # Percorrer todas as linhas do df_curv e aplicar os fatores de acumulação
    for i, row_curv in df_curv.iterrows():
        # Verificar se o cod_usina é igual ao "MONT" de df_curv
        if cod_usina == row_curv['MONT']:  # Verificação de igualdade
            hora_curva = row_curv['hora'].hour  # Pegamos a hora do df_curv
            fator_acum = row_curv['acum'] - fator_acumulado_anterior  # Atualiza o fator de acumulação subtraindo fator_acumulado_anterior
            incrementar_dia = row_curv['incrementa_dia']  # Flag para verificar se devemos aumentar 1 dia

            # Ajustamos a nova hora
            nova_hora_total = hora_hidri + hora_curva

            # Se a nova hora for maior ou igual a 24, subtraímos 24 e adicionamos 1 dia
            if nova_hora_total >= 24:
                nova_hora_total -= 24
                incrementar_dia = True  # Garantimos que o dia será incrementado

            # Atualizar a data conforme necessário
            nova_data = data + timedelta(days=1) if incrementar_dia else data

            # Converter a nova hora para formato de tempo
            hora_final = time(nova_hora_total, 0, 0)

            # Calcular a defluência proporcional com o fator de acumulação
            deflu = ((fator_acum) / 100) * val_vazao

            # Calcular a defluência bruta (sem o fator de acumulação)
            deflu_inteira = val_vazao  # Defluência sem o fator de acumulação

            # Adicionar a nova linha ao DataFrame com a defluência bruta e o fator
            linhas.append({
                'cod': cod_usina,
                'data': nova_data,  # Data corrigida
                'hora': hora_final,  # Hora corrigida
                'deflu': deflu,  # Defluência com fator aplicado
                'deflu_inteira': deflu_inteira,  # Defluência sem fator aplicado
                'fator_acum': fator_acum,  # Adicionar o fator de acumulação
                'acum_curv': row_curv['acum']  # Adicionar o valor de 'acum' de df_curv para verificação
            })

            # Atualizar o valor de fator_acumulado_anterior para o próximo ciclo (soma)
            fator_acumulado_anterior += fator_acum  # Soma o fator acumulado ao fator anterior

# Criar o DataFrame final com os valores calculados
deflu_acum = pd.DataFrame(linhas)

# Exportar para Excel
# deflu_acum.to_excel("deflu_acum.xlsx", index=False)

# Filtrando o DataFrame para obter apenas as linhas com a data igual a 'data_formatada_menos_um'
df_filtrado = deflu_acum[deflu_acum['data'] == data_formatada_menos_um]

# Agrupando por 'cod', 'data', e 'hora' e somando os valores de 'deflu'
df_som = df_filtrado.groupby(['cod', 'data', 'hora'], as_index=False)['deflu'].sum()

# df_som.to_excel("deflu_somado.xlsx", index=False)

# Agora, vamos filtrar e renomear as colunas de deflu para cada código (66 e 83)
deflu_66 = df_som[df_som['cod'] == 66][['data', 'hora', 'deflu']]  # Filtrando para cod 66
deflu_83 = df_som[df_som['cod'] == 83][['data', 'hora', 'deflu']]  # Filtrando para cod 83

# Renomeando as colunas para facilitar a junção
deflu_66 = deflu_66.rename(columns={'deflu': 'deflu_66'})
deflu_83 = deflu_83.rename(columns={'deflu': 'deflu_83'})

# Juntando as duas tabelas com base nas colunas 'data' e 'hora'
df_cotasr11 = pd.merge(deflu_66, deflu_83, on=['data', 'hora'], how='outer')

# Calculando a defluência com base na fórmula
df_cotasr11['defluencia'] = 1.03 * df_cotasr11['deflu_66'] + 1.17 * df_cotasr11['deflu_83']

# Selecionando as colunas finais e renomeando a coluna de 'defluencia'
df_cotasr11 = df_cotasr11[['data', 'hora', 'defluencia']]

# Aplicar o polinômio para calcular a cota
df_cotasr11['cota'] = (
        76.677112 +
        2.8660334e-3 * df_cotasr11['defluencia'] -
        1.0474654e-7 * (df_cotasr11['defluencia'] ** 2) +
        2.6583003e-12 * (df_cotasr11['defluencia'] ** 3) -
        3.8245459e-17 * (df_cotasr11['defluencia'] ** 4) +
        2.8607867e-22 * (df_cotasr11['defluencia'] ** 5) -
        8.6322234e-28 * (df_cotasr11['defluencia'] ** 6)
)

# Passo 1: Converta a coluna 'hora' para datetime (caso seja uma string) e depois extraia a hora
df_cotasr11['hora'] = pd.to_datetime(df_cotasr11['hora'], format='%H:%M:%S').dt.hour

# Passo 2: Criar uma lista para armazenar as novas linhas com meia-hora
linhas_expandidas = []

# Passo 3: Iterar sobre cada linha de df_cotasr11
for _, row in df_cotasr11.iterrows():
    # Adicionar a linha original com 'meia_hora' = 0
    linhas_expandidas.append({
        'data': row['data'],
        'hora': row['hora'],
        'meia_hora': 0,
        'defluencia': row['defluencia'],
        'cota': row['cota']
    })

    # Adicionar a linha duplicada com 'meia_hora' = 1
    linhas_expandidas.append({
        'data': row['data'],
        'hora': row['hora'],  # Mantém a mesma hora
        'meia_hora': 1,  # Linha duplicada com meia-hora
        'defluencia': row['defluencia'],
        'cota': row['cota']
    })

# Passo 4: Atualizar o DataFrame original com as novas linhas
df_cotasr11 = pd.DataFrame(linhas_expandidas)

# Passo 5: Ordenar por data e hora (caso você precise garantir a ordem)
df_cotasr11 = df_cotasr11.sort_values(by=['data', 'hora', 'meia_hora'])

# Realizar a junção com base nas colunas 'hora' == 'hh' e 'meia_hora' == 'm'
df_cotasr11 = pd.merge(df_cotasr11, df_cotas, how='left', left_on=['hora', 'meia_hora'], right_on=['hh', 'm'])

# Criar a coluna 'cotas_estimadas' a partir da coluna 'cotR11', sem sobrescrever cotR11
df_cotasr11['cotas_estimadas'] = df_cotasr11['cotR11']

# Remover as colunas do merge que não são mais necessárias
df_cotasr11 = df_cotasr11.drop(columns=['d', 'cotR11', 'hh', 'm'])

# Arredondar a coluna 'cota' para 2 casas decimais
df_cotasr11['cota'] = df_cotasr11['cota'].round(2)

# Usando ExcelWriter para adicionar uma nova aba ao arquivo existente
with pd.ExcelWriter(hidraulicos_path, engine='openpyxl', mode='a') as writer:
    df_cotasr11.to_excel(writer, sheet_name='CotasR11', index=False)

print("-----------------------------------------------")
print("Iniciando escrita dos arquivos")
print("-----------------------------------------------")

with open('dadvaz.dat', 'r+') as f:
    lines = f.readlines()  # Lê todas as linhas do arquivo

    for i, line in enumerate(lines):
        if line[24:26] == data_dia:

            for index, row in df_dadvaz.iterrows():
                if int(line[0:3]) == row['NUM'] and line[24:26] == row['DI']:
                    new_value = str(row['vazao_verificada']).rjust(9)

                    # Substitui o trecho correto da linha
                    lines[i] = line[:19] + '1' + line[20:44] + new_value + line[53:]

    # Voltar ao início do arquivo e sobrescrever com as novas linhas
    f.seek(0)
    f.truncate()  # Apaga o conteúdo do arquivo antes de reescrever
    f.writelines(lines)  # Escreve as linhas modificadas de volta no arquivo

with open('deflant.dat', 'r+') as f:
    lines = f.readlines()  # Lê todas as linhas do arquivo

    # Adiciona as 4 primeiras linhas de volta no arquivo
    lines_to_write = lines[:5]

    # A partir da linha 5, vamos escrever o DataFrame
    for index, row in df_deflant.iterrows():
        # Construa a nova linha com os valores do DataFrame
        valor_vazao = str(row['val_vazaodefluente']).rjust(9)
        valor_mont = str(row['num']).rjust(3)
        valor_jus = str(row['Jus']).rjust(3)

        # Substitui os valores específicos da linha com as colunas do DataFrame
        new_line = (
            str(row['X']) + lines[5][6:9] + valor_mont + lines[5][12:14] + valor_jus +
            lines[5][17:19] + str(row['TpJ']) + lines[5][20:24] + str(row['di']) +
            lines[5][26:28] + str(row['hi']) + lines[5][29:30] + str(row['m']) + lines[5][31:32] +
            str(row['df']) + lines[5][34:45] + valor_vazao + lines[5][54:]
        )

        lines_to_write.append(new_line)

    # Após escrever o DataFrame, não escrevemos mais nada no arquivo
    # Voltar ao início do arquivo e sobrescrever com as novas linhas
    f.seek(0)
    f.truncate()  # Apaga o conteúdo do arquivo antes de reescrever
    f.writelines(lines_to_write)  # Escreve as linhas modificadas de volta no arquivo

with open('entdados.dat', 'r+') as f:
    lines = f.readlines()  # Lê todas as linhas do arquivo

    for i, line in enumerate(lines):
        if line[:4] == 'UH  ':

            for index, row in df_entdados.iterrows():
                if int(line[4:7]) == row['ind']:

                    # Verificando se o volume útil está entre 0 e 100

                    new_value = str(row['volume_util']).rjust(6)

                    # Substitui o trecho correto da linha
                    lines[i] = line[:29] + new_value + line[35:]

    # Voltar ao início do arquivo e sobrescrever com as novas linhas
    f.seek(0)
    f.truncate()  # Apaga o conteúdo do arquivo antes de reescrever
    f.writelines(lines)  # Escreve as

with open('cotasr11.dat', 'r+') as f:
    lines = f.readlines()  # Lê todas as linhas do arquivo

    for i, line in enumerate(lines):
        if line[:1] != '&':

            for index, row in df_cotasr11.iterrows():
                if int(line[3:5]) == int(row['hora']) and int(line[6:7]) == int(row['meia_hora']):

                    new_value = str(row['cota']).rjust(5)

                    # Substitui o trecho correto da linha
                    lines[i] = line[:21] + new_value + line[26:]

    # Voltar ao início do arquivo e sobrescrever com as novas linhas
    f.seek(0)
    f.truncate()  # Apaga o conteúdo do arquivo antes de reescrever
    f.writelines(lines)