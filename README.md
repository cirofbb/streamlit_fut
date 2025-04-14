# streamlit_fut

### Análise de Dados de Futebol com StatsBomb

Dashboard interativo para análise avançada de dados de futebol utilizando a API StatsBomb.

### Visão Geral
Este projeto permite a exploração detalhada de dados de partidas de futebol, incluindo visualizações de passes, chutes, comparação entre jogadores e análise temporal dos eventos.

### Funcionalidades Principais

🏆 Seleção de Competições
- Escolha entre diversas competições disponíveis
- Filtro por temporada específica
- Seleção de partidas individuais

📊 Visualizações de Jogo
- Mapa de passes com direção e frequência
- Mapa de chutes com localização no campo
- Estatísticas comparativas entre times
- Relação entre passes e chutes por equipe

⚽ Análise de Jogadores
- Filtro por jogador específico
- Métricas individuais (chutes, passes, dribles)
- Mapas personalizados por jogador
- Exportação de dados em CSV

⏱️ Filtros Avançados
- Intervalo de tempo personalizado
- Quantidade de eventos a visualizar
- Comparação entre dois jogadores
- Filtro por tipo de evento (passes, chutes)

### Como Executar
Instale as dependências:

pip install streamlit pandas statsbombpy mplsoccer seaborn matplotlib

Execute o aplicativo:

streamlit run AT.py
Estrutura do Código
```
.
├── AT.py                # Aplicativo principal
├── requirements.txt     # Dependências
└── README.md            # Este arquivo

```

Dependências
- Python 3.8+
- streamlit
- pandas
- statsbombpy
- mplsoccer
- seaborn
- matplotlib

### Exemplos de Uso
Análise de Partida:

- Selecione uma competição e temporada

- Escolha uma partida específica

- Visualize os mapas de passes e chutes

Comparação de Jogadores:

- Ative a opção "Comparar jogadores"

- Selecione dois jogadores

- Analise as métricas lado a lado

Exportação de Dados:

- Filtre por jogador específico

- Baixe os dados em formato CSV

### Dados Utilizados
O aplicativo utiliza a API pública do StatsBomb, que fornece:

Dados de mais de 100 competições

Eventos detalhados de cada partida

Informações táticas e de desempenho
