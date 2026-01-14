import streamlit as st
import pandas as pd
import requests
import warnings

# --- 1. CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="CriptoAlerta Terminal", page_icon="🦅", layout="wide")
warnings.filterwarnings("ignore")

# --- 2. CSS AVANÇADO (VISUAL DARK PREMIUM) ---
st.markdown("""
<style>
    /* Fundo Global */
    .stApp {
        background-color: #050505;
        color: #e0e0e0;
    }
    
    /* Barra Lateral */
    section[data-testid="stSidebar"] {
        background-color: #0a0a0a;
        border-right: 1px solid #333;
    }
    
    /* Cards de Métricas */
    div[data-testid="metric-container"] {
        background: #111;
        border: 1px solid #333;
        border-radius: 12px;
        padding: 15px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.3);
    }
    
    /* Botões Verdes */
    .stButton button {
        background: linear-gradient(90deg, #00C853, #009624);
        color: white;
        border: none;
        border-radius: 6px;
        font-weight: bold;
        text-transform: uppercase;
    }
    
    /* Tabela */
    div[data-testid="stDataFrame"] {
        border: 1px solid #333;
    }
</style>
""", unsafe_allow_html=True)

# --- 3. SISTEMA DE LOGIN ---
def check_password():
    if "password_correct" not in st.session_state:
        st.session_state["password_correct"] = False
    if st.session_state["password_correct"]:
        return True

    col1, col2, col3 = st.columns([1,1,1])
    with col2:
        st.markdown("<h3 style='text-align: center; color: #00C853;'>🔐 ACESSO RESTRITO</h3>", unsafe_allow_html=True)
        senha = st.text_input("Senha do Dossiê:", type="password")
        if st.button("CONECTAR"):
            if senha == "baleia2026": 
                st.session_state["password_correct"] = True
                st.rerun()
            else:
                st.error("Senha Inválida.")
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

# --- 5. SIDEBAR ---
with st.sidebar:
    st.header("🦅 Cripto Alerta")
    st.caption("Intelligence Unit")
    st.divider()
    
    st.write("**Registrar Operação**")
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
        
        if st.form_submit_button("REGISTRAR"):
            novo = pd.DataFrame([{'Ativo': ativo, 'ID': id_coin.lower().strip(), 'Qtd': qtd, 'Preço_Medio': pm, 'Meta': meta, 'Stop': stop}])
            st.session_state['portfolio'] = pd.concat([st.session_state['portfolio'], novo], ignore_index=True)
            st.success("Salvo!")

# --- 6. DASHBOARD ---
st.markdown("## PAINEL DE CONTROLE INSTITUCIONAL")
st.divider()

if not st.session_state['portfolio'].empty:
    df = st.session_state['portfolio'].copy()
    
    # Atualiza Preços
    with st.spinner('Sincronizando dados...'):
        df['Preço_Atual'] = [get_price(x) for x in df['ID']]
    
    # Cálculos
    df['Total Investido'] = df['Qtd'] * df['Preço_Medio']
    df['Saldo Atual'] = df['Qtd'] * df['Preço_Atual']
    df['Lucro $'] = df['Saldo Atual'] - df['Total Investido']
    df['Lucro %'] = ((df['Preço_Atual'] - df['Preço_Medio']) / df['Preço_Medio']) * 100
    
    def get_status(row):
        if row['Preço_Atual'] == 0: return "⚠️ OFF"
        if row['Preço_Atual'] >= row['Meta']: return "💰 VENDER"
        if row['Preço_Atual'] <= row['Stop']: return "🛑 STOP"
        return "🛡️ HOLD"
    df['STATUS'] = df.apply(get_status, axis=1)

    # Métricas
    tot_inv = df['Total Investido'].sum()
    tot_atu = df['Saldo Atual'].sum()
    lucro = tot_atu - tot_inv
    
    c1, c2, c3 = st.columns(3)
    c1.metric("CAPITAL ALOCADO", f"$ {tot_inv:,.2f}")
    c2.metric("SALDO ATUAL", f"$ {tot_atu:,.2f}")
    c3.metric("LUCRO LÍQUIDO", f"$ {lucro:,.2f}", delta=f"{lucro:,.2f}")

    st.markdown("---")

    # GRÁFICOS NATIVOS (SEM ERRO DE PLOTLY)
    col_g1, col_g2 = st.columns([2, 1])
    
    with col_g1:
        st.subheader("📊 Alocação por Ativo")
        # Gráfico de Barras Nativo (Muito rápido e não dá erro)
        chart_data = df.set_index("Ativo")[["Saldo Atual"]]
        st.bar_chart(chart_data, color="#00C853")

    with col_g2:
        st.subheader("🎯 Performance")
        st.write("Confiança do Mercado")
        st.progress(75) # Barra de progresso nativa
        st.caption("Índice: Extreme Greed")
        
        lucro_count = len(df[df['Lucro $'] >= 0])
        st.write(f"Ativos no Lucro: **{lucro_count}**")

    # Tabela
    st.subheader("📋 Ordens")
    def style_df(val):
        if val == '💰 VENDER': return 'color: #00E676; font-weight: bold'
        if val == '🛑 STOP': return 'color: #FF5252; font-weight: bold'
        return ''

    st.dataframe(
        df[['Ativo', 'Qtd', 'Preço_Medio', 'Preço_Atual', 'Lucro %', 'STATUS']]
        .style.applymap(style_df, subset=['STATUS'])
        .format({'Preço_Medio': '${:.2f}', 'Preço_Atual': '${:.2f}', 'Lucro %': '{:.2f}%'}),
        use_container_width=True
    )
    
    if st.button("LIMPAR SISTEMA"):
        st.session_state['portfolio'] = pd.DataFrame(columns=['Ativo', 'ID', 'Qtd', 'Preço_Medio', 'Meta', 'Stop'])
        st.rerun()

else:
    st.info("⚠️ Nenhuma posição ativa. Use a barra lateral.")
