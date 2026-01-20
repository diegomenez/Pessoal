import streamlit as st
import pandas as pd
import requests
import time
import io

# Configuração da Página
st.set_page_config(page_title="Decodificador Fipe em Massa", layout="wide")

st.title("📊 Decodificador de Fipe em Massa")
st.write("Faça upload da planilha, selecione as colunas de FIPE e ANO, e o sistema buscará o valor exato.")

# 1. O Uploader de Arquivos
arquivo = st.file_uploader("Solte sua planilha aqui (formato .xlsx)", type=["xlsx"])

if arquivo:
    # Lê o Excel
    df = pd.read_excel(arquivo)
    
    st.success("Planilha carregada com sucesso!")
    st.write("Prévia dos dados:")
    st.dataframe(df.head(3))

    # --- SELEÇÃO DE COLUNAS (AGORA SÃO DUAS) ---
    col1, col2 = st.columns(2)
    with col1:
        coluna_fipe = st.selectbox("Qual coluna contém o CÓDIGO FIPE?", df.columns)
    with col2:
        coluna_ano = st.selectbox("Qual coluna contém o ANO DO MODELO?", df.columns)

    st.warning("⚠️ Importante: A coluna de ANO deve conter apenas números (ex: 2015, 2022).")

    if st.button("🚀 Iniciar Decodificação"):
        
        barra_progresso = st.progress(0)
        status_texto = st.empty()
        
        lista_resultados = []
        total_carros = len(df)

        # 3. O Loop da Frota
        for index, linha in df.iterrows():
            # Tratamento do Código Fipe
            codigo = str(linha[coluna_fipe]).strip()
            
            # Tratamento do Ano (Converte para inteiro para bater com a API)
            try:
                ano_alvo = int(linha[coluna_ano])
            except:
                ano_alvo = None # Se não for número, marca como inválido

            status_texto.text(f"Processando item {index+1}/{total_carros}: FIPE {codigo} | Ano {ano_alvo}...")
            
            # --- Lógica de Consulta Ajustada ---
            url = f"https://brasilapi.com.br/api/fipe/preco/v1/{codigo}"
            
            resultado_linha = {
                "FIPE Original": codigo,
                "Ano Informado": ano_alvo,
                "Status": "Erro Desconhecido"
            }

            if not ano_alvo:
                resultado_linha["Status"] = "Ano Inválido na Planilha"
            else:
                try:
                    resposta = requests.get(url)
                    if resposta.status_code == 200:
                        lista_anos = resposta.json() # Recebe a lista de todos os anos
                        
                        # --- O FILTRO MÁGICO ---
                        # Procura dentro da lista o ano que bate com a planilha
                        carro_encontrado = None
                        for item in lista_anos:
                            if item['anoModelo'] == ano_alvo:
                                carro_encontrado = item
                                break
                        
                        if carro_encontrado:
                            resultado_linha.update({
                                "Modelo Encontrado": carro_encontrado['modelo'],
                                "Ano Tabela": carro_encontrado['anoModelo'],
                                "Valor Tabela": carro_encontrado['valor'],
                                "Combustivel": carro_encontrado['combustivel'],
                                "Status": "Sucesso"
                            })
                        else:
                            resultado_linha["Status"] = "Ano não encontrado para este FIPE"
                            # Opcional: Pegar o ano mais próximo ou avisar quais anos existem
                    
                    elif resposta.status_code == 404:
                        resultado_linha["Status"] = "Código FIPE não existe"
                    else:
                        resultado_linha["Status"] = f"Erro API: {resposta.status_code}"

                except Exception as e:
                    resultado_linha["Status"] = f"Erro de Conexão/Código: {e}"

            lista_resultados.append(resultado_linha)
            
            # Atualiza a barra
            barra_progresso.progress((index + 1) / total_carros)
            time.sleep(0.1) # Pausa respeitosa para a API

        # 4. Mostra o Resultado Final
        df_resultado = pd.DataFrame(lista_resultados)
        
        st.success("Decodificação Finalizada!")
        st.dataframe(df_resultado)

        # 5. Botão de Download
        def converter_para_excel(df):
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                df.to_excel(writer, index=False, sheet_name='Resultado_FIPE')
            return output.getvalue()

        dados_excel = converter_para_excel(df_resultado)

        st.download_button(
            label="💾 Baixar Planilha (.xlsx)",
            data=dados_excel,
            file_name="frota_decodificada_com_valores.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )