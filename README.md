# 🚗 Cotador de Frota Inteligente

Este projeto é uma ferramenta de automação desenvolvida em Python para agilizar o processo de cotação de seguros de frotas de automóveis.

A aplicação processa planilhas em massa, consulta valores atualizados na Tabela FIPE em tempo real e aplica fatores de risco customizáveis para calcular o prêmio final.

## 🚀 Funcionalidades

- **Consulta Automática à FIPE:** Integração com a BrasilAPI para buscar valores de veículos pelo código FIPE.
- **Cálculo de Precificação:** Aplicação dinâmica de taxas baseada em:
  - Tipo de Veículo (Passeio, Pesado, Misto)
  - Região de Risco e CEP
  - Coberturas e Franquias
  - Histórico de Sinistralidade
- **Interface Visual:** Painel interativo construído com Streamlit para ajuste fácil dos parâmetros.
- **Processamento em Lote:** Suporta upload de arquivos Excel (`.xlsx`) com múltiplos veículos.
- **Exportação de Dados:** Gera um relatório final em Excel pronto para uso.

## 🛠️ Tecnologias Utilizadas

- **Python**
- **Streamlit** (Interface Web)
- **Pandas** (Manipulação de Dados)
- **BrasilAPI** (Dados da FIPE)
- **OpenPyXL** (Geração de Excel)

## 📦 Como rodar o projeto

1. Clone o repositório:
   ```bash
   git clone [https://github.com/diegomenez/Pessoal.git](https://github.com/diegomenez/Pessoal.git)
