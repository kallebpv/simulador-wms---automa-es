# -*- coding: utf-8 -*-
import pandas as pd
import sys

import pandas as pd

def processar_planilha(caminho_arquivo, paciente_inicial='#ignorate#'):
    try:
        df_planilha = pd.read_excel(caminho_arquivo, sheet_name='SAÍDA PROGRAMADA')  # [SIMULADOR] nome de aba fictício no lugar do original
    except Exception as e:
        raise RuntimeError(f"Erro ao ler o arquivo: {str(e)}")

    #Atribuindo a coluna chamada TIPO, CÓD e PEDIDO em uma variavel
    df_coluna_tratada = df_planilha[['TIPO','CÓD','PEDIDO ']]
    # Remove linhas onde PEDIDO é NaN (vazio) ou igual a 0
    df_coluna_tratada = df_coluna_tratada[df_coluna_tratada["PEDIDO "].notna() & (df_coluna_tratada["PEDIDO "] != 0)]

    # CRIAR UM DICIONARIO QUE DIVIDO CADA CÓD E PEDIDO PERTENCETE A CADA CATEGORIA DA COLUNA 'TIPO'
    df_tipos_divididos = {tipo: grupo[['CÓD','PEDIDO ']] for tipo, grupo in df_coluna_tratada.groupby('TIPO')}

    return df_tipos_divididos
def limpar_valor(valor):
    if pd.isna(valor):
        return ""
    # Se for float e não tiver parte decimal, remove o .0
    if isinstance(valor, float) and valor.is_integer():
        return str(int(valor))

    return str(valor)