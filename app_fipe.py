import streamlit as st
import requests

# 1. Título e Instruções (O Streamlit cria o HTML H1 e P)
st.title("🚗 Consultor FIPE Hub Segs")
st.write("Digite o código FIPE abaixo para ver o valor atualizado.")

# 2. A Caixa de Entrada (Input)
codigo_fipe = st.text_input("Código FIPE (Ex: 002196-2)", max_chars=8)

# 3. O Botão de Ação
if st.button("Consultar Preço"):
    if codigo_fipe:
        try:
            # Lógica que você já conhece
            url = f"https://brasilapi.com.br/api/fipe/preco/v1/{codigo_fipe}"
            resposta = requests.get(url)
            
            if resposta.status_code == 200:
                # A API retorna uma lista, pegamos o primeiro (modelo mais novo ou zero km)
                dados = resposta.json()[0] 
                
                # 4. Exibindo o resultado bonito (Cartões métricos)
                st.success("Veículo Encontrado!")
                
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("Modelo", dados['modelo'])
                with col2:
                    st.metric("Valor Tabela", dados['valor'])
                    
                st.text(f"Referência: {dados['mesReferencia']}")
                
            else:
                st.error("Código FIPE não encontrado. Verifique se digitou certo.")
                
        except Exception as e:
            st.error(f"Erro de conexão: {e}")
    else:
        st.warning("Por favor, digite um código antes de clicar.")