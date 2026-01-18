import streamlit as st
import pandas as pd
import requests
import time
import io

# Configuração da Página
st.set_page_config(page_title="Cotador de Frota Hub Segs", layout="wide")

st.title("📊 Decodificador de Frotas")
st.write("Faça upload da planilha, selecione a coluna da FIPE e deixe o Python trabalhar.")

# 1. O Uploader de Arquivos (A Mágica do Excel)
arquivo = st.file_uploader("Solte sua planilha aqui (formato .xlsx)", type=["xlsx"])

if arquivo:
    # Lê o Excel que você subiu
    df = pd.read_excel(arquivo)
    
    st.success("Planilha carregada com sucesso!")
    st.write("Prévia dos dados:")
    st.dataframe(df.head(3)) # Mostra só as 3 primeiras linhas pra não poluir

    # 2. Pergunta qual coluna usar (Inteligência)
    # O Python lista todas as colunas do seu Excel e pede pra você escolher
    coluna_fipe = st.selectbox("Qual coluna contém os códigos FIPE?", df.columns)

    if st.button("🚀 Iniciar Decodifiação da Frota"):
        
        # Cria uma barra de progresso visual
        barra_progresso = st.progress(0)
        status_texto = st.empty()
        
        lista_resultados = []
        total_carros = len(df)

        # 3. O Loop da Frota (Varre linha por linha)
        for index, linha in df.iterrows():
            codigo = str(linha[coluna_fipe]).strip() # Limpa espaços extras
            
            status_texto.text(f"Decodificando item {index+1}/{total_carros}: FIPE {codigo}...")
            
            # --- Lógica de Consulta (Mesma de antes) ---
            url = f"https://brasilapi.com.br/api/fipe/preco/v1/{codigo}"
            try:
                resposta = requests.get(url)
                if resposta.status_code == 200:
                    dados = resposta.json()[0] # Pega o modelo mais novo/Zero KM
                    
                    lista_resultados.append({
                        "FIPE Original": codigo,
                        "Modelo Encontrado": dados['modelo'],
                        "Ano Modelo": dados['anoModelo'],
                        "Valor Tabela": dados['valor'],
                        "Status": "Sucesso"
                    })
                else:
                    lista_resultados.append({
                        "FIPE Original": codigo,
                        "Status": "Não Encontrado"
                    })
            except:
                lista_resultados.append({"FIPE Original": codigo, "Status": "Erro na API"})
            
            # Atualiza a barra
            barra_progresso.progress((index + 1) / total_carros)
            time.sleep(0.1) # Uma pequena pausa para não travar a API

        # 4. Mostra o Resultado Final
        df_resultado = pd.DataFrame(lista_resultados)
        
        st.success("Decodificação Finalizada!")
        st.dataframe(df_resultado)

        # 5. Botão de Download (Agora em EXCEL .xlsx)
        # Função que cria o arquivo Excel na memória RAM
        def converter_para_excel(df):
            output = io.BytesIO()
            # Usa o 'openpyxl' (que você já instalou) para escrever o Excel
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                df.to_excel(writer, index=False, sheet_name='Resultado_FIPE')
            
            # Prepara o arquivo para ser baixado
            return output.getvalue()

        # Gera o arquivo
        dados_excel = converter_para_excel(df_resultado)

        st.download_button(
            label="💾 Baixar Planilha em Excel (.xlsx)",
            data=dados_excel,
            file_name="frota_decodificada.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )