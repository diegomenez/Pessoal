import streamlit as st
import requests

# 1. Configuração da Página
st.set_page_config(page_title="Consultor FIPE Hub Segs", page_icon="🚗")

st.title("🚗 Consultor FIPE Hub Segs")
st.write("Digite o código FIPE e o Ano do modelo para buscar o valor exato.")

# 2. As Caixas de Entrada (Inputs lado a lado)
col_input1, col_input2 = st.columns(2)

with col_input1:
    codigo_fipe = st.text_input("Código FIPE (Ex: 002196-2)", max_chars=8)

with col_input2:
    # Input numérico para evitar erros de digitação
    # 32000 é o código padrão da FIPE para "Zero KM"
    ano_modelo = st.number_input(
        "Ano do Modelo (Use 32000 para Zero KM)", 
        min_value=1980, 
        max_value=32000, 
        value=2024,
        step=1
    )

# 3. O Botão de Ação
if st.button("Consultar Preço"):
    if codigo_fipe:
        try:
            # Limpa espaços em branco caso o usuário copie e cole errado
            codigo_limpo = codigo_fipe.strip()
            
            url = f"https://brasilapi.com.br/api/fipe/preco/v1/{codigo_limpo}"
            resposta = requests.get(url)
            
            if resposta.status_code == 200:
                lista_anos = resposta.json()
                
                # Variável para guardar o carro se acharmos
                veiculo_encontrado = None
                
                # Procura o ano digitado dentro da lista da API
                for item in lista_anos:
                    if item['anoModelo'] == ano_modelo:
                        veiculo_encontrado = item
                        break
                
                # 4. Exibindo o resultado
                if veiculo_encontrado:
                    st.success("✅ Veículo Encontrado!")
                    st.subheader(veiculo_encontrado['modelo'])
                    
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Ano Modelo", veiculo_encontrado['anoModelo'])
                    with col2:
                        st.metric("Valor Tabela", veiculo_encontrado['valor'])
                    with col3:
                        st.metric("Combustível", veiculo_encontrado['combustivel'])
                        
                    st.caption(f"Mês de Referência: {veiculo_encontrado['mesReferencia']} | Código Fipe: {veiculo_encontrado['codigoFipe']}")
                
                else:
                    # Se o código existe, mas o ano não
                    st.warning(f"⚠️ O código FIPE existe, mas o ano {ano_modelo} não consta na tabela.")
                    
                    # AJUDA: Mostra quais anos estão disponíveis para esse carro
                    anos_disponiveis = sorted([item['anoModelo'] for item in lista_anos], reverse=True)
                    st.info(f"Anos disponíveis para este modelo: {anos_disponiveis}")
                    
            else:
                st.error("❌ Código FIPE não encontrado. Verifique se digitou certo.")
                
        except Exception as e:
            st.error(f"Erro de conexão: {e}")
    else:
        st.warning("⚠️ Por favor, digite um código FIPE antes de clicar.")