import streamlit as st
import pandas as pd
import requests
import plotly.express as px
import warnings

# --- 1. CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="CriptoAlerta Terminal", page_icon="🦅", layout="wide")
warnings.filterwarnings("ignore")

# --- 2. CSS AVANÇADO (A MÁGICA VISUAL) ---
st.markdown("""
<style>
    /* Fundo Global (Dark Tech) */
    .stApp {
        background-color: #050505;
        color: #e0e0e0;
    }
    
    /* Barra Lateral */
    section[data-testid="stSidebar"] {
        background-color: #0a0a0a;
        border-right: 1px solid #333;
    }
    
    /* Cards de Métricas (Estilo Glass) */
    div[data-testid="metric-container"] {
        background: rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 12px;
        padding: 20px;
        transition: transform 0.2s;
    }
    div[data-testid="metric-container"]:hover {
        transform: scale(1.02);
        border: 1px solid #00C853;
    }
    
    /* Títulos e Textos */
    h1, h2, h3 {
        color: white !important;
        font-family: 'Helvetica Neue', sans-serif;
        font-weight: 700;
    }
    
    /* Botões (Verde Institucional) */
    .stButton button {
        background: linear-gradient(45deg, #00C853, #009624);
        color: white;
        border: none;
        border-radius: 8px;
        font-weight: bold;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    
    /* Tabela */
    div[data-testid="stDataFrame"] {
        border: 1px solid #333;
        border-radius: 10px;
    }
</style>
""", unsafe_allow_html=True)

# --- 3. SISTEMA DE LOGIN (Mantido) ---
def check_password():
    if "password_correct" not in st.session_state:
        st.session_state["password_correct"] = False
    if st.session_state["password_correct"]:
        return True

    # Login Visual
    col1, col2, col3 = st.columns([1,1,1])
    with col2:
        st.markdown("<h2 style='text-align: center;'>🔐 TERMINAL CRIPTO ALERTA</h2>", unsafe_allow_html=True)
        st.info("Acesso Restrito a Membros do Dossiê.")
        senha = st.text_input("Chave de Acesso:", type="password")
        if st.button("CONECTAR AO SISTEMA"):
            if senha == "baleia2026": 
                st.session_state["password_correct"] = True
                st.rerun()
            else:
                st.error("Acesso Negado.")
    return False

if not check_password():
    st.stop()

# --- 4. FUNÇÕES ---
@st.cache_data(ttl=60)
def get_price(coin_id):
    try:
        url = f"https://api.coingecko.com/api/v3/simple/price?ids={coin_id}&vs_currencies=usd"
        res = requests.get(url, timeout=3)
        return res.json()[coin_id]['usd'] if res.status_code == 200 else 0
    except:
        return 0

# --- 5. SIDEBAR (Identidade Visual) ---
with st.sidebar:
    # URL de um logo genérico de Bitcoin ou SEU LOGO (Substitua a URL se tiver um logo online)
    st.image("https://cdn-icons-png.flaticon.com/512/12114/12114233.png", width=80)
    st.markdown("### CRIPTO ALERTA 2.0")
    st.caption("Intelligence Unit")
    st.divider()
    
    st.header("➕ Nova Posição")
    
    if 'portfolio' not in st.session_state:
        st.session_state['portfolio'] = pd.DataFrame(columns=['Ativo', 'ID', 'Qtd', 'Preço_Medio', 'Meta', 'Stop'])

    with st.form("form_sidebar"):
        ativo = st.text_input("Ativo (Ex: Bitcoin)", "Bitcoin")
        id_coin = st.text_input("ID API (Ex: bitcoin)", "bitcoin")
        c1, c2 = st.columns(2)
        qtd = c1.number_input("Qtd", min_value=0.0, format="%.6f")
        pm = c2.number_input("Preço Médio ($)", min_value=0.0)
        c3, c4 = st.columns(2)
        meta = c3.number_input("Alvo ($)", min_value=0.0)
        stop = c4.number_input("Stop ($)", min_value=0.0)
        
        if st.form_submit_button("REGISTRAR NA BLOCKCHAIN"):
            novo = pd.DataFrame([{'Ativo': ativo, 'ID': id_coin.lower().strip(), 'Qtd': qtd, 'Preço_Medio': pm, 'Meta': meta, 'Stop': stop}])
            st.session_state['portfolio'] = pd.concat([st.session_state['portfolio'], novo], ignore_index=True)
            st.success("Ordem Registrada!")

# --- 6. DASHBOARD PRINCIPAL ---
st.markdown("## 🦅 PAINEL DE CONTROLE INSTITUCIONAL")
st.markdown("Monitoramento em Tempo Real | Estratégia On-Chain")
st.divider()

if not st.session_state['portfolio'].empty:
    df = st.session_state['portfolio'].copy()
    
    # Atualização de Preços
    with st.spinner('📡 Sincronizando com satélites...'):
        df['Preço_Atual'] = [get_price(x) for x in df['ID']]
    
    # Matemática
    df['Total Investido'] = df['Qtd'] * df['Preço_Medio']
    df['Saldo Atual'] = df['Qtd'] * df['Preço_Atual']
    df['Lucro $'] = df['Saldo Atual'] - df['Total Investido']
    df['Lucro %'] = ((df['Preço_Atual'] - df['Preço_Medio']) / df['Preço_Medio']) * 100
    
    # Lógica de Alerta
    def get_status(row):
        if row['Preço_Atual'] == 0: return "⚠️ OFF"
        if row['Preço_Atual'] >= row['Meta']: return "💰 VENDER AGORA"
        if row['Preço_Atual'] <= row['Stop']: return "🛑 STOP LOSS"
        return "🛡️ HOLD"
    df['STATUS'] = df.apply(get_status, axis=1)

    # --- MÉTRICAS (TOP CARDS) ---
    tot_inv = df['Total Investido'].sum()
    tot_atu = df['Saldo Atual'].sum()
    tot_lucro = tot_atu - tot_inv
    
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("CAPITAL ALOCADO", f"$ {tot_inv:,.2f}")
    col2.metric("SALDO EM CARTEIRA", f"$ {tot_atu:,.2f}")
    col3.metric("LUCRO / PREJUÍZO", f"$ {tot_lucro:,.2f}", delta=f"{tot_lucro:,.2f}")
    
    # Card de Performance
    roi_total = (tot_lucro / tot_inv * 100) if tot_inv > 0 else 0
    col4.metric("ROI TOTAL", f"{roi_total:.2f}%")

    st.markdown("<br>", unsafe_allow_html=True)

    # --- GRÁFICOS VISUAIS (NOVIDADE!) ---
    c_chart1, c_chart2 = st.columns([2, 1])
    
    with c_chart1:
        st.subheader("📊 Composição da Carteira")
        # Gráfico de Rosca (Donut Chart) estilo Institucional
        if tot_atu > 0:
            fig = px.pie(df, values='Saldo Atual', names='Ativo', hole=0.5, 
                         color_discrete_sequence=px.colors.sequential.Greens_r)
            fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", 
                              font={'color': "white"}, showlegend=True)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Sem dados para gráfico.")

    with c_chart2:
        st.subheader("🎯 Status dos Alvos")
        # Mostra apenas texto resumido
        lucro_ops = df[df['Lucro $'] > 0].shape[0]
        preju_ops = df[df['Lucro $'] < 0].shape[0]
        st.write(f"Operações no Verde: **{lucro_ops}**")
        st.write(f"Operações no Vermelho: **{preju_ops}**")
        
        # Barra de Progresso Simples
        st.markdown("---")
        st.caption("Confiança do Mercado (Fear & Greed)")
        st.progress(75) # Valor estático simulado, pode conectar API depois
        st.caption("Extreme Greed (Cuidado)")

    # --- TABELA DETALHADA ---
    st.subheader("📋 Ordens Abertas")
    
    def style_dataframe(val):
        if val == '💰 VENDER AGORA': return 'color: #00E676; font-weight: bold; background-color: #002200'
        if val == '🛑 STOP LOSS': return 'color: #FF5252; font-weight: bold; background-color: #220000'
        if val == '🛡️ HOLD': return 'color: #FFD600; font-weight: bold'
        return ''

    st.dataframe(
        df[['Ativo', 'Qtd', 'Preço_Medio', 'Preço_Atual', 'Meta', 'Lucro %', 'STATUS']]
        .style.applymap(style_dataframe, subset=['STATUS'])
        .format({'Preço_Medio': '${:.2f}', 'Preço_Atual': '${:.2f}', 'Meta': '${:.2f}', 'Lucro %': '{:.2f}%'}),
        use_container_width=True,
        height=300
    )
    
    if st.button("🗑️ LIMPAR DADOS DO SISTEMA"):
        st.session_state['portfolio'] = pd.DataFrame(columns=['Ativo', 'ID', 'Qtd', 'Preço_Medio', 'Meta', 'Stop'])
        st.rerun()

else:
    # Tela de "Vazio" Bonita
    st.info("⚠️ Nenhuma posição detectada.")
    st.markdown("""
    <div style='background-color: #111; padding: 20px; border-radius: 10px; border: 1px dashed #444;'>
        <h4>Como começar:</h4>
        <ol>
            <li>Use o menu lateral esquerdo.</li>
            <li>Adicione seus ativos (Ex: Render, Bitcoin).</li>
            <li>O sistema monitorará 24/7 os alvos institucionais.</li>
        </ol>
    </div>
    """, unsafe_allow_html=True)
