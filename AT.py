import streamlit as st
import pandas as pd
from statsbombpy import sb

from mplsoccer import Pitch, Sbopen
import matplotlib.pyplot as plt
import seaborn as sns

# QUESTÕES 3 E 4
@st.cache_data
def carregar_competicoes():
    competicoes = sb.competitions()
    return competicoes

@st.cache_data
def carregar_jogos(competicao_id, temporada_id):
    jogos = sb.matches(competition_id=competicao_id, season_id=temporada_id)
    return jogos

@st.cache_data
def carregar_eventos(jogo_id):
    eventos = sb.events(match_id=jogo_id)
    return eventos

# Sidebar para seleção de campeonato, temporada e partida
st.sidebar.title('Análise de futebol - StatsBombPy')
competicoes = carregar_competicoes()

competicao_selecionada = st.sidebar.selectbox(
    'Selecione uma competição',
    competicoes['competition_name'].unique()
)

competicao_id = competicoes[competicoes['competition_name'] == competicao_selecionada]['competition_id'].values[0]

temporadas_disponiveis = competicoes[competicoes['competition_id'] == competicao_id]['season_name'].unique()

temporada_selecionada = st.sidebar.selectbox(
    'Selecione uma temporada',
    temporadas_disponiveis
)

temporada_id = competicoes[
    (competicoes['competition_id'] == competicao_id) & (competicoes['season_name'] == temporada_selecionada)]['season_id'].values[0]

# Carrega os jogos da competição e temporada selecionadas
jogos = carregar_jogos(competicao_id, temporada_id)

# Seleção de jogo
jogo_selecionado = st.sidebar.selectbox(
    'Selecione uma partida',
    jogos.apply(lambda x: f"{x['home_team']} vs {x['away_team']}", axis=1)
)

# Filtra o ID da partida selecionada
jogos_id = jogos[jogos.apply(lambda x: f"{x['home_team']} vs {x['away_team']}", axis=1) == jogo_selecionado]['match_id'].values[0]
jogos_info = jogos[jogos['match_id'] == jogos_id].iloc[0]

# Carrega os eventos da partida selecionada
eventos = carregar_eventos(jogos_id)

# Filtrando os eventos
chutes = eventos[eventos['type'] == 'Shot']
gols = eventos[eventos['shot_outcome'] == 'Goal']

chutes_casa = chutes[chutes['team'] == jogos_info['home_team']]
chutes_fora = chutes[chutes['team'] == jogos_info['away_team']]

# Layout principal usando colunas e containers
with st.container():
    st.header('Informações da partida selecionada')
    col1, col2, col3 = st.columns(3)

    col1.metric('Competição', competicao_selecionada)
    col2.metric('Temporada', temporada_selecionada)
    col3.metric('Partida', f"{jogos_info['home_team']} vs {jogos_info['away_team']}")

    st.subheader('Estatísticas da partida')
    
    # Exibe o resultado da partida
    st.write(f"Resultado: {jogos_info['home_score']} - {jogos_info['away_score']}")

    # Exibe os jogadores que marcaram os gols
    st.write('Gols:')
    if gols.empty:
        st.write('Nenhum gol registrado.')
    else:
        for index, gol in gols.iterrows():
            minuto = gol['minute']
            jogador = gol['player']
            time = gol['team']
            st.write(f"{jogador} ({time}) - {minuto} min")

    # Exibe o nº de finalizações de cada time
    st.write(f"Finalizações do {jogos_info['home_team']}: {len(chutes_casa)}")
    st.write(f"Finalizações do {jogos_info['away_team']}: {len(chutes_fora)}")
    
    # Exibe um DataFrame com os eventos da partida
    st.subheader('Eventos da partida')
    eventos_df = eventos[['type', 'team', 'player', 'minute', 'second', 'location', 'pass_end_location']]
    st.dataframe(eventos_df)

# QUESTÃO 5

# Função para gerar o mapa de passes
def gerar_mapa_passes(eventos):
    passes = eventos[eventos['type'] == 'Pass']
    pitch = Pitch(line_color='black', pitch_type='statsbomb')
    fig, ax = pitch.draw(figsize=(10, 7))
    pitch.arrows(passes['location'].apply(lambda x: x[0]),
                 passes['location'].apply(lambda x: x[1]),
                 passes['pass_end_location'].apply(lambda x: x[0]),
                 passes['pass_end_location'].apply(lambda x: x[1]),
                 ax=ax, color='blue', lw=2, label='Passes')
    
    plt.title('Mapa de passes')
    plt.legend()
    st.pyplot(fig)

# Função para gerar o mapa de chutes
def gerar_mapa_chutes(eventos):
    chutes = eventos[eventos['type'] == 'Shot']
    pitch = Pitch(line_color='black', pitch_type='statsbomb')
    fig, ax = pitch.draw(figsize=(10, 7))
    pitch.scatter(chutes['location'].apply(lambda x: x[0]),
                  chutes['location'].apply(lambda x: x[1]),
                  ax=ax, color='red', s=100, edgecolor='black', label='Chutes')
    
    plt.title('Mapa de chutes')
    plt.legend()
    st.pyplot(fig)

# Gerar visualizações
st.subheader('Visualizações com mplsoccer')
gerar_mapa_passes(eventos)
gerar_mapa_chutes(eventos)

# Função para criar visualização adicional com Seaborn
def explorar_relacoes(eventos):
    passes = eventos[eventos['type'] == 'Pass']
    chutes = eventos[eventos['type'] == 'Shot']
    
    stats_por_time = passes.groupby('team').size().reset_index(name='passes')
    stats_por_time['chutes'] = chutes.groupby('team').size().values

    fig, ax = plt.subplots(figsize=(8, 6))
    sns.barplot(x='team', y='passes', data=stats_por_time, ax=ax, color='blue', label='Passes')
    sns.barplot(x='team', y='chutes', data=stats_por_time, ax=ax, color='red', label='Chutes')
    ax.set_title('Relação entre passes e chutes por time')
    legend_labels = [plt.Rectangle((0, 0), 1, 1, color='blue'), plt.Rectangle((0, 0), 1, 1, color='red')]
    ax.legend(legend_labels, ['Passes', 'Chutes'])
    st.pyplot(fig)

st.subheader('Exploração de Estatísticas')
explorar_relacoes(eventos)

# QUESTÃO 6

def filtrar_por_jogador(eventos, jogador):
    return eventos[eventos['player'] == jogador]

def download_csv(data, filename):
    csv = data.to_csv(index=False)
    st.download_button(label='Baixar dados em CSV', data=csv, file_name=filename, mime='text/csv')

def calcular_metricas(eventos, jogador):
    eventos_jogador = eventos[eventos['player'] == jogador]

    #total_gols = eventos[eventos['type'] == 'Goal'].shape[0]
    total_chutes = eventos_jogador[eventos_jogador['type'] == 'Shot'].shape[0]
    total_passes_tentados = eventos_jogador[eventos_jogador['type'] == 'Pass'].shape[0]
    total_dibres = eventos_jogador[(eventos_jogador['type'] == 'Dribble')].shape[0]

    return total_chutes, total_passes_tentados, total_dibres

st.title('Interatividade')

with st.spinner('Carregando dados...'):
    eventos = carregar_eventos(jogos_id)

    progress_bar = st.progress(0)
    for i in range(100):
        progress_bar.progress(i + 1)

# Selecionar jogador para filtrar eventos
jogadores = eventos['player'].dropna().unique()
jogador_selecionado = st.selectbox('Selecione um jogador', jogadores)

eventos_filtrados = filtrar_por_jogador(eventos, jogador_selecionado)
total_chutes, total_passes_tentados, total_dibres = calcular_metricas(eventos, jogador_selecionado)

# Exibir métricas
st.subheader('Indicadores do jogador')
st.metric(label='Total de chutes', value=total_chutes, delta_color='normal', help='Total de chutes')
st.metric(label='Total de passes', value=total_passes_tentados, delta_color='normal', help='Total de passes')
st.metric(label='Total de dribles', value=total_dibres, delta_color='normal', help='Total de dribles')
#st.metric(label="Taxa de Conversão de Chutes", value=f"{taxa_conversao:.2f}%", delta_color="normal", help="Taxa de conversão de chutes em gol")


# Botões de visualização e download
with st.container():
    st.subheader(f'Eventos do jogador: {jogador_selecionado}')
    col1, col2 = st.columns(2)
    with col1:
        st.subheader('Mapa de passes')
        gerar_mapa_passes(eventos_filtrados)
    with col2:
        st.subheader('Mapa de chutes')
        gerar_mapa_chutes(eventos_filtrados)

st.subheader('Download dos dados filtrados')
download_csv(eventos_filtrados, f'eventos_{jogador_selecionado}.csv')

# QUESTÕES 8 E 9

# Inicia o estado da sessão
if 'quantidade_eventos' not in st.session_state:
    st.session_state['quantidade_eventos'] = 100
if 'intervalo_inicio' not in st.session_state:
    st.session_state['intervalo_inicio'] = "00:00"
if 'intervalo_fim' not in st.session_state:
    st.session_state['intervalo_fim'] = "90:00"
if 'jogador1' not in st.session_state or st.session_state['jogador1'] not in eventos['player'].unique():
    st.session_state['jogador1'] = eventos['player'].unique()[0]
if 'jogador2' not in st.session_state or st.session_state['jogador2'] not in eventos['player'].unique():
    st.session_state['jogador2'] = eventos['player'].unique()[1]
if 'tipo_evento' not in st.session_state:
    st.session_state['tipo_evento'] = 'Todos'
if 'comparar_jogadores' not in st.session_state:
    st.session_state['comparar_jogadores'] = False

# Formulário para selecionar opções de visualização
with st.form('form_opcoes_visualizacao'):
    st.header('Opções de visualização')

    # Campo de entrada para definir a quantidade de eventos
    st.session_state['quantidade_eventos'] = st.slider(
        'Quantidade de Eventos a Serem Visualizados', 
        min_value=1, 
        max_value=100, 
        value=st.session_state['quantidade_eventos']
    )

    # Define intervalo de tempo
    st.session_state['intervalo_inicio'] = st.text_input(
        'Início do Intervalo de Tempo (em minutos)', 
        value=st.session_state['intervalo_inicio']
    )
    st.session_state['intervalo_fim'] = st.text_input(
        'Fim do Intervalo de Tempo (em minutos)', 
        value=st.session_state['intervalo_fim']
    )

    intervalo_inicio_minutos = int(st.session_state['intervalo_inicio'].split(":")[0]) * 60 + int(st.session_state['intervalo_inicio'].split(":")[1])
    intervalo_fim_minutos = int(st.session_state['intervalo_fim'].split(":")[0]) * 60 + int(st.session_state['intervalo_fim'].split(":")[1])

    # Seleção de jogadores para comparar
    st.session_state['jogador1'] = st.selectbox(
        'Selecione o Jogador 1', 
        options=eventos['player'].unique(), 
        index=list(eventos['player'].unique()).index(st.session_state['jogador1'])
    )
    st.session_state['jogador2'] = st.selectbox(
        'Selecione o Jogador 2', 
        options=eventos['player'].unique(), 
        index=list(eventos['player'].unique()).index(st.session_state['jogador2'])
    )

    # Radio buttons para selecionar tipo de evento
    st.session_state['tipo_evento'] = st.radio(
        'Selecione o tipo de evento para visualização', 
        ('Passes', 'Chutes', 'Todos'), 
        index=['Passes', 'Chutes', 'Todos'].index(st.session_state['tipo_evento'])
    )

    # Checkbox para definir a comparação de jogadores
    st.session_state['comparar_jogadores'] = st.checkbox(
        'Comparar estatísticas entre dois jogadores', 
        value=st.session_state['comparar_jogadores']
    )

    # Botão para submeter o formulário
    submitted = st.form_submit_button('Aplicar Filtros')

# Se o formulário for submetido, realizar os cálculos e exibir as informações
if submitted:
    eventos_filtrados = eventos[
        (eventos['minute'] * 60 + eventos['second'] >= intervalo_inicio_minutos) &
        (eventos['minute'] * 60 + eventos['second'] <= intervalo_fim_minutos)
    ]
    
    # Aplica filtro de tipo de evento
    if st.session_state['tipo_evento'] == 'Passes':
        eventos_filtrados = eventos_filtrados[eventos_filtrados['type'] == 'Pass']
    elif st.session_state['tipo_evento'] == 'Chutes':
        eventos_filtrados = eventos_filtrados[eventos_filtrados['type'] == 'Shot']

    # Filtrar apenas pelos jogadores selecionados
    eventos_filtrados = eventos_filtrados[
        (eventos_filtrados['player'] == st.session_state['jogador1']) |
        (eventos_filtrados['player'] == st.session_state['jogador2'])
    ]
    


    # Limita a quantidade de eventos
    eventos_filtrados = eventos_filtrados.head(st.session_state['quantidade_eventos'])

    # Exibe os eventos filtrados
    st.subheader(f"Eventos Filtrados de {st.session_state['jogador1']} e {st.session_state['jogador2']}")
    st.dataframe(eventos_filtrados)

    # Exibe as métricas de comparação
    if st.session_state['comparar_jogadores']:
        st.subheader(f"Comparação entre {st.session_state['jogador1']} e {st.session_state['jogador2']}")
        
        metrics_jogador1 = calcular_metricas(eventos, st.session_state['jogador1'])
        metrics_jogador2 = calcular_metricas(eventos, st.session_state['jogador2'])

        col1, col2 = st.columns(2)

        with col1:
            st.metric(label=f"{st.session_state['jogador1']}: Total de Chutes", value=metrics_jogador1[0])
            st.metric(label='Passes Completos', value=metrics_jogador1[1])
            #st.metric(label="Taxa de Conversão de Passes (%)", value=f"{metrics_jogador1[2]:.2f}")

        with col2:
            st.metric(label=f"{st.session_state['jogador2']}: Total de Chutes", value=metrics_jogador2[0])
            st.metric(label='Passes Completos', value=metrics_jogador2[1])
            #st.metric(label="Taxa de Conversão de Passes (%)", value=f"{metrics_jogador2[2]:.2f}")
