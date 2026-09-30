# -*- coding: utf-8 -*-
import pandas as pd
import sys

import pandas as pd

def processar_planilha(caminho_arquivo, paciente_inicial='#ignorate#'):
    try:
        df = pd.read_excel(caminho_arquivo, header=None)
    except Exception as e:
        raise RuntimeError(f"Erro ao ler o arquivo: {str(e)}")

    linha_atual = 0
    total_linhas = df.shape[0]
    encontrou_inicial = False if paciente_inicial != '#ignorate#' else True
    cancelado_encontrado = False
    pacientes_processados = []  # Lista para controle de duplicatas

    while linha_atual < total_linhas and not cancelado_encontrado:
        # Etapa 1: Buscar cabeçalhos válidos
        while linha_atual < total_linhas:
            celula = df.iloc[linha_atual, 2]
            
            if pd.notnull(celula) and 'cancelado' in str(celula).lower():
                cancelado_encontrado = True
                break
                
            if pd.isnull(celula):
                linha_atual += 1
                continue
                
            celula_str = str(celula).lower()
            
            if 'registro de paciente' in celula_str:  # [SIMULADOR] rótulo fictício no lugar do original
                linha_processo = linha_atual
                tem_estabelecimento = False
                
                # Verificar estabelecimento nas próximas linhas
                for offset in range(1, 3):  # Verifica até 2 linhas abaixo
                    if (linha_atual + offset) >= total_linhas:
                        break
                    celula_check = df.iloc[linha_atual + offset, 2]
                    if pd.notnull(celula_check) and 'estabelecimento' in str(celula_check).lower():
                        tem_estabelecimento = True
                        linha_atual += offset + 1
                        break
                
                if tem_estabelecimento:
                    continue  # Ignora pacientes com estabelecimento

                # Verificar paciente inicial
                if not encontrou_inicial and paciente_inicial != '#ignorate#':
                    celula_paciente = df.iloc[linha_atual + 1, 2] if (linha_atual + 1) < total_linhas else None
                    if celula_paciente and paciente_inicial.lower() not in str(celula_paciente).lower():
                        linha_atual += 1
                        continue
                    else:
                        encontrou_inicial = True
                
                linha_atual = linha_processo
                break
                
            linha_atual += 1

        if cancelado_encontrado or linha_atual >= total_linhas:
            break

        # Etapa 2: Coletar informações do paciente
        info_paciente = []
        prontuario = None
        nome_paciente = None
        
        while linha_atual < total_linhas and not cancelado_encontrado:
            celula = df.iloc[linha_atual, 2]
            
            if pd.notnull(celula):
                if 'cancelado' in str(celula).lower():
                    cancelado_encontrado = True
                    break
                    
                if 'registro de paciente' in str(celula).lower():  # [SIMULADOR] rótulo fictício no lugar do original
                    prontuario = celula.split(':')[-1].strip()
                    
                if 'paciente:' in str(celula).lower():
                    nome_paciente = celula.split(':')[-1].strip()
                    
            if pd.notnull(celula) and 'agendado' in str(celula).lower():
                linha_atual += 1
                break
                
            info_paciente.append(str(celula))
            linha_atual += 1

        # Etapa 3: Buscar seção de produtos
        produto_encontrado = False
        while linha_atual < total_linhas:
            celula = df.iloc[linha_atual, 2]
            
            if pd.notnull(celula):
                if 'cancelado' in str(celula).lower():
                    cancelado_encontrado = True
                    break
                    
                if 'produto' in str(celula).lower():
                    linha_atual += 1
                    produto_encontrado = True
                    break
                    
            linha_atual += 1

        if cancelado_encontrado:
            break

        # Etapa 4: Coletar itens
        itens = []
        codigos_quant = []
        while linha_atual < total_linhas:
            celula_item = df.iloc[linha_atual, 2]
            
            if pd.notnull(celula_item):
                celula_str = str(celula_item).lower()
                
                if 'registro de paciente' in celula_str or 'cancelado' in celula_str:  # [SIMULADOR] rótulo fictício no lugar do original
                    if 'cancelado' in celula_str:
                        cancelado_encontrado = True
                    break

                # Coletar código e quantidade
                codigo, quantidade = None, None
                for col in range(3, df.shape[1]):
                    val = df.iloc[linha_atual, col]
                    if pd.notnull(val):
                        codigo = str(val)
                        for q_col in range(col + 1, df.shape[1]):
                            q_val = df.iloc[linha_atual, q_col]
                            if pd.notnull(q_val):
                                try:
                                    quantidade = int(float(q_val))
                                    break
                                except:
                                    continue
                        break
                
                if codigo and quantidade:
                    itens.append(str(celula_item))
                    codigos_quant.append(f"{codigo}\t{quantidade}")

            linha_atual += 1

        # Gerar dados ANTES de verificar cancelado
        yield {
            "paciente": "\n".join(info_paciente),
            "itens": itens,
            "numeracao_dos_itens_e_quantidade": "\n".join(codigos_quant)
        }

        if cancelado_encontrado:
            break
        # Prevenir loop infinito
        if linha_atual <= linha_processo:
            linha_atual += 1
# caminho = r""  # ⚠️ ALTERE!

# print("\n" + "="*50)
# print("RELATÓRIO PROCESSADO")
# print("="*50 + "\n")

# try:
#     # Processa a planilha UMA VEZ e armazena em uma lista
#     pacientes_processados = list(processar_planilha(caminho))  # Converta o gerador em lista
    
#     # Parte 1: Códigos e Quantidades
#     print("[1] CÓDIGOS E QUANTIDADES:")
#     for idx, paciente in enumerate(pacientes_processados, 1):
#         print(f"\n--- PACIENTE {idx} ---")
#         print(paciente["paciente"])  # Remova encode/decode redundante
#         if paciente["numeracao_dos_itens_e_quantidade"]:
#             print("\nCódigo | Quantidade")
#             print("-------------------")
#             for linha in paciente["numeracao_dos_itens_e_quantidade"].split('\n'):
#                 cod, qtd = linha.split('\t')
#                 print(f"{cod.strip():8} | {qtd.strip():>3}")
#         else:
#             print("Sem itens válidos!")
#         print("-" * 50)

#     # Parte 2: Nomes dos Itens (usa a mesma lista)
#     print("\n\n[2] NOMES DOS ITENS PRESCRITOS:")
#     for idx, paciente in enumerate(pacientes_processados, 1):
#         print(f"\n--- PACIENTE {idx} ---")
#         print(paciente["paciente"])  # Remova encode/decode redundante
#         if paciente["itens"]:
#             print("\nItens:")
#             for item in paciente["itens"]:
#                 print(f"- {item}")
#         else:
#             print("Sem itens registrados!")
#         print("-" * 50)

# except Exception as e:
#     print(f"\n⚠️ ERRO: {str(e)}")
#     print("Verifique:")
#     print("- Caminho do arquivo")
#     print("- Formato das colunas (coluna 2 deve conter os textos)")
#     print("- Valores numéricos na coluna de quantidade")

# print("\n" + "="*50)
# print("FIM DO RELATÓRIO")
# print("="*50)