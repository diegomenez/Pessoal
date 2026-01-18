import streamlit as st
import pandas as pd
import requests
import time
import io

# ==============================
# CONFIGURAÇÃO DA PÁGINA
# ==============================
st.set_page_config(
    page_title="Cotador de Frota by Diego Menezes",
    layout="wide"
)

st.title("📊 Cotador de Frota por FIPE e Ano")
st.markdown("""
Upload da planilha com **Códigos FIPE** e **Ano do Modelo**.
O sistema buscará o valor exato correspondente ao ano do veículo.
""")

# ==============================
# PARÂMETROS DO COTADOR
# ==============================

TAXA_BASE_FROTA = 0.025  # 2,5%

FATOR_TIPO_VEICULO = {
    "Passeio": 1.00,
    "Pesado": 1.60,
    "Misto": 1.30,
}

FATOR_REGIAO = {
    "Baixo Risco": 0.90,
    "Médio Risco": 1.00,
    "Alto Risco": 1.15,
    "Crítico": 1.30
}

FATOR_COBERTURA = {
    "RCF": 0.45,
    "Compreensiva": 1.00,
    "Compreensiva + RCF": 1.15
}

FATOR_FRANQUIA = {
    "Normal": 1.00,
    "Reduzida": 1.95
}

FATOR_SINISTRO = {
    "0%": 0.85,
    "Até 20%": 1.00,
    "21% a 40%": 1.15,
    "41% a 60%": 1.30,
    "Acima de 60%": 1.50
}

FATOR_SEGURO_NOVO = {
    "Renovação": 1.00,
    "Seguro Novo": 1.10
}

FATOR_DM_DC = {
    "50k / 100k": 1.00,
    "100k / 200k": 1.10,
    "300k / 500k": 1.25,
    "500k / 1MM": 1.40
}

FATOR_REBOQUE = {
    "200 km": 1.00,
    "500 km": 1.05,
    "800 km": 1.10,
    "Ilimitado": 1.30
}

FATOR_VIDROS = {
    "Sem": 1.00,
    "Básico": 1.05,
    "Completo": 1.10
}

FATOR_CARRO_RESERVA = {
    "Sem": 1.00,
    "7 dias": 1.04,
    "30 dias": 1.10
}

# ==============================
# SIDEBAR – PARÂMETROS DA FROTA
# ==============================

st.sidebar.title("⚙️ Parâmetros da Frota")

tipo_veiculo = st.sidebar.selectbox("Tipo de Veículo", list(FATOR_TIPO_VEICULO.keys()))
regiao = st.sidebar.selectbox("Região (CEP)", list(FATOR_REGIAO.keys()))
cobertura = st.sidebar.selectbox("Cobertura", list(FATOR_COBERTURA.keys()))
franquia = st.sidebar.selectbox("Franquia", list(FATOR_FRANQUIA.keys()))
sinistro = st.sidebar.selectbox("Sinistralidade da Frota", list(FATOR_SINISTRO.keys()))
seguro_novo = st.sidebar.selectbox("Seguro", list(FATOR_SEGURO_NOVO.keys()))
dm_dc = st.sidebar.selectbox("DM / DC", list(FATOR_DM_DC.keys()))
reboque = st.sidebar.selectbox("Reboque", list(FATOR_REBOQUE.keys()))
vidros = st.sidebar.selectbox("Vidros", list(FATOR_VIDROS.keys()))
carro_reserva = st.sidebar.selectbox("Carro Reserva", list(FATOR_CARRO_RESERVA.keys()))

# ==============================
# UPLOAD DA PLANILHA
# ==============================

arquivo = st.file_uploader(
    "📂 Envie sua planilha (.xlsx)",
    type=["xlsx"]
)

if arquivo:
    df = pd.read_excel(arquivo)

    st.success("Planilha carregada com sucesso!")
    st.dataframe(df.head(5))

    col1, col2 = st.columns(2)
    
    with col1:
        coluna_fipe = st.selectbox(
            "Qual coluna contém os códigos FIPE?",
            df.columns
        )
    
    with col2:
        coluna_ano = st.selectbox(
            "Qual coluna contém o ANO do Modelo?",
            df.columns
        )

    if st.button("🚀 Processar Frota"):
        barra = st.progress(0)
        status = st.empty()

        resultados = []
        total = len(df)
        total_fipe_frota = 0
        total_premio_frota = 0


        for i, linha in df.iterrows():
            codigo = str(linha[coluna_fipe]).strip()
            
            # Tenta converter o ano da planilha para inteiro para bater com a API
            try:
                ano_alvo = int(linha[coluna_ano])
            except:
                ano_alvo = 0 # Valor inválido se não conseguir converter
            
            status.text(f"Processando {i+1}/{total} — FIPE {codigo} (Ano {ano_alvo})")

            url = f"https://brasilapi.com.br/api/fipe/preco/v1/{codigo}"

            try:
                r = requests.get(url, timeout=10)

                if r.status_code == 200:
                    lista_anos = r.json()
                    
                    # Procura o ano exato na lista retornada pela API
                    dados_veiculo = None
                    
                    # Carro Zero KM na tabela FIPE costuma vir como 32000
                    if ano_alvo == 0 or ano_alvo == 32000: 
                        dados_veiculo = lista_anos[0] # Pega o mais novo (Zero KM)
                    else:
                        for item in lista_anos:
                            if item['anoModelo'] == ano_alvo:
                                dados_veiculo = item
                                break
                    
                    if dados_veiculo:
                        valor_fipe = float(
                            dados_veiculo["valor"]
                            .replace("R$", "")
                            .replace(".", "")
                            .replace(",", ".")
                        )

                        premio_base = valor_fipe * TAXA_BASE_FROTA

                        premio_final = premio_base \
                            * FATOR_TIPO_VEICULO[tipo_veiculo] \
                            * FATOR_REGIAO[regiao] \
                            * FATOR_COBERTURA[cobertura] \
                            * FATOR_FRANQUIA[franquia] \
                            * FATOR_SINISTRO[sinistro] \
                            * FATOR_SEGURO_NOVO[seguro_novo] \
                            * FATOR_DM_DC[dm_dc] \
                            * FATOR_REBOQUE[reboque] \
                            * FATOR_VIDROS[vidros] \
                            * FATOR_CARRO_RESERVA[carro_reserva]
                        
                        total_fipe_frota += valor_fipe
                        total_premio_frota += premio_final

                        resultados.append({
                            "FIPE": codigo,
                            "Modelo": dados_veiculo["modelo"],
                            "Ano Modelo": dados_veiculo["anoModelo"],
                            "Valor FIPE": round(valor_fipe, 2),
                            "Prêmio Final": round(premio_final, 2),
                            "Status": "Sucesso"
                        })
                    else:
                        # Se não achou o ano específico
                        resultados.append({
                            "FIPE": codigo,
                            "Modelo": "-",
                            "Ano Modelo": ano_alvo,
                            "Valor FIPE": 0,
                            "Prêmio Final": 0,
                            "Status": "Ano não encontrado na Tabela"
                        })

                else:
                    resultados.append({
                        "FIPE": codigo,
                        "Modelo": "-",
                        "Ano Modelo": ano_alvo,
                        "Valor FIPE": 0,
                        "Prêmio Final": 0,
                        "Status": "FIPE Inexistente"
                    })

            except Exception as e:
                resultados.append({
                    "FIPE": codigo,
                    "Modelo": "-",
                    "Ano Modelo": ano_alvo,
                    "Valor FIPE": 0,
                    "Prêmio Final": 0,
                    "Status": f"Erro API: {e}"
                })

            barra.progress((i + 1) / total)
            time.sleep(0.1)

        df_final = pd.DataFrame(resultados)

        st.success("✅ Cotação finalizada!")
        st.dataframe(df_final)
        st.write("Veja abaixo os resultados da cotação da sua frota.")
        

        st.subheader("📊 Totais da Frota")

        col1, col2 = st.columns(2)

        col1.metric("FIPE Total da Frota", f"R$ {total_fipe_frota:,.2f}")
        col2.metric("Prêmio Total da Frota", f"R$ {total_premio_frota:,.2f}")


        # ==============================
        # EXPORTAÇÃO PARA EXCEL
        # ==============================

        def gerar_excel(df):
            buffer = io.BytesIO()
            with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
                df.to_excel(writer, index=False, sheet_name="Cotacao_Frota")
            return buffer.getvalue()

        arquivo_excel = gerar_excel(df_final)

        st.download_button(
            label="💾 Baixar cotação em Excel",
            data=arquivo_excel,
            file_name="cotacao_frota_v2.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )