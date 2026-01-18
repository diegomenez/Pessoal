import requests # Biblioteca que "navega" na internet

# Imagine que você tem o código FIPE dos carros da frota
# (Exemplo: Fiat Strada e Toyota Hilux)
lista_fipes = ["001306-4", "002196-2"] 

print("Consultando valores atualizados na FIPE...")

for fipe in lista_fipes:
    # O Python vai na API pública da FIPE consultar
    url = f"https://brasilapi.com.br/api/fipe/preco/v1/{fipe}"
    resposta = requests.get(url)
    
    if resposta.status_code == 200:
        dados = resposta.json()[0]
        modelo = dados['modelo']
        valor = dados['valor']
        ano = dados['anoModelo']
        
        print(f"Carro: {modelo} ({ano}) | Valor Tabela: {valor}")
    else:
        print(f"FIPE {fipe} não encontrada.")

# Resultado na tela:
# Carro: Strada Freedom 1.3 Flex 8V CD 4p (2024) | Valor Tabela: R$ 108.450,00
# Carro: Hilux CD SRV 4x4 2.8 TDI Diesel Aut. (2024) | Valor Tabela: R$ 265.900,00