import streamlit as st
import pandas as pd
import requests
import time

# --- 1. CONFIGURAÇÃO DA PÁGINA (Deve ser a primeira linha de comando Streamlit) ---
st.set_page_config(page_title="CriptoManager 2.0", page_icon="🚀", layout="wide")

# --- 2. SISTEMA DE LOGIN (SEGURANÇA) ---
def check_password():
    """Retorna `True` se o usuário tiver a senha correta."""
    
    # Inicializa o estado da senha se não existir
    if "password_correct" not in st.session_state:
        st.session_state["password_correct"] = False

    # Se a senha já estiver correta, libera o acesso
    if st.session_state["password_correct"]:
        return True

    # Tela de Login
    st.markdown("## 🔒 Área Exclusiva CriptoAlerta")
    st.markdown("Insira a senha disponível no seu **Dossiê Cripto 2026**.")
    
    password = st.text_input("Senha de Acesso:", type="password")
    
    if st.button("Entrar no Sistema"):
        # --- AQUI VOCÊ DEFINE A SENHA ---
        if password == "baleia2026": 
            st.session_state["password_correct"] = True
            st.rerun() # Recarrega a página para liberar
        else:
            st.error("🚫 Senha incorreta. Tente novamente.")
            
    return False

# Se a senha não estiver correta, o script PARA aqui e não mostra o resto.
if not check_password():
    st.stop()

# =========================================================
# --- DAQUI PARA BAIXO É O SISTEMA LIBERADO ---
# =========================================================

# --- 3. FUNÇÃO PARA PEGAR PREÇOS (API COINGECKO) ---
@st.cache_data(ttl=60) # Cache de 60 segundos para não bloquear a API
def get_crypto_price(coin_id):
    try:
        # Tenta pegar o preço na API
        url = f"https://api.coingecko.com/api/v3/simple/price?ids={coin_id}&vs_currencies=usd"
        response = requests.get(url, timeout=5)
        data = response.json()
        return data[coin_id]['usd']
    except:
        # Se der erro (moeda não existe ou API fora), retorna 0
        return 0

# --- 4. ESTILO VISUAL (CSS) ---
st.markdown("""
<style>
    .stMetric {
        background-color: #0E1117;
        padding: 15px;
        border: 1px solid #333;
        border-radius: 10px;
    }
    div[data-testid="stDataFrame"] {
        width: 100%;
    }
</style>
""", unsafe_allow_html=True)

# --- 5. CABEÇALHO DO APP ---
st.title("📊 CriptoManager Pro")
st.markdown("**Gestão de Ativos Baseada em Alvos Matemáticos | CriptoAlerta 2.0**")
st.divider()

# --- 6. BARRA LATERAL (CADASTRO) ---
st.sidebar.header("📝 Adicionar Nova Operação")

# Inicializa a carteira na memória se não existir
if 'portfolio' not in st.session_state:
    st.session_state['portfolio'] = pd.DataFrame(columns=['Ativo', 'ID_Coingecko', 'Qtd', 'Preço_Medio', 'Meta_Lucro', 'Stop_Loss'])

with st.sidebar.form("add_coin_form"):
    st.write("Preencha os dados da sua compra:")
    ativo_nome = st.text_input("Nome (Ex: Bitcoin)", "Bitcoin")
    ativo_id = st.text_input("ID CoinGecko (Ex: bitcoin, ethereum, solana)", "bitcoin")
    st.caption("Dica: O ID deve ser minúsculo, igual na URL do CoinGecko.")
    
    col_sb1, col_sb2 = st.columns(2)
    with col_sb1:
        qtd = st.number_input("Quantidade", min_value=0.0, format="%.6f")
        preco_medio = st.number_input("Preço Médio Pagou ($)", min_value=0.0)
    with col_sb2:
        meta = st.number_input("Meta de Venda ($)", min_value=0.0)
        stop = st.number_input("Stop Loss ($)", min_value=0.0)
    
    submitted = st.form_submit_button("💾 Salvar Ativo")
    
    if submitted:
        if qtd > 0:
            new_row = pd.DataFrame({
                'Ativo': [ativo_nome],
                'ID_Coingecko': [ativo_id.lower().strip()],
                'Qtd': [qtd],
                'Preço_Medio': [preco_medio],
                'Meta_Lucro': [meta],
                'Stop_Loss': [stop]
            })
            st.session_state['portfolio'] = pd.concat([st.session_state['portfolio'], new_row], ignore_index=True)
            st.success(f"✅ {ativo_nome} adicionado com sucesso!")
        else:
            st.warning("A quantidade deve ser maior que zero.")

# --- 7. LÓGICA DE CÁLCULO E EXIBIÇÃO ---
if not st.session_state['portfolio'].empty:
    
    # Criar uma cópia para manipular
    df_display = st.session_state['portfolio'].copy()
    
    # Buscar preços atuais
    with st.spinner('Atualizando cotações em tempo real...'):
        price_list = []
        for id_coin in df_display['ID_Coingecko']:
            price_list.append(get_crypto_price(id_coin))
        
    df_display['Preço_Atual'] = price_list
    
    # Cálculos Matemáticos
    df_display['Total_Investido'] = df_display['Qtd'] * df_display['Preço_Medio']
    df_display['Valor_Hoje'] = df_display['Qtd'] * df_display['Preço_Atual']
    df_display['Resultado_%'] = ((df_display['Preço_Atual'] - df_display['Preço_Medio']) / df_display['Preço_Medio']) * 100
    
    # Lógica do ALERTA (O Segredo do App)
    def definir_status(row):
        # Evitar erro se preço for 0
        if row['Preço_Atual'] == 0:
            return "⚠️ ERRO ID"
            
        if row['Preço_Atual'] >= row['Meta_Lucro']:
            return "💰 LUCRO (VENDER)"
        elif row['Preço_Atual'] <= row['Stop_Loss']:
            return "🛑 STOP (SAIR)"
        else:
            return "⏳ HOLD (SEGURAR)"
            
    df_display['STATUS'] = df_display.apply(definir_status, axis=1)

    # --- 8. DASHBOARD (MÉTRICAS TOTAIS) ---
    total_investido = df_display['Total_Investido'].sum()
    valor_total = df_display['Valor_Hoje'].sum()
    lucro_total = valor_total - total_investido
    
    c1, c2, c3 = st.columns(3)
    c1.metric("Total Investido", f"$ {total_investido:,.2f}")
    c2.metric("Patrimônio Atual", f"$ {valor_total:,.2f}", delta=f"{lucro_total:,.2f}")
    
    status_geral = "Lucro" if lucro_total >= 0 else "Prejuízo"
    c3.metric("Balanço Geral", status_geral)

    # --- 9. TABELA PRINCIPAL ---
    st.subheader("Sua Carteira")
    
    # Função para colorir a tabela (Design)
    def color_coding(val):
        if isinstance(val, str):
            if 'LUCRO' in val:
                return 'background-color: #2e7d32; color: white; font-weight: bold'
            elif 'STOP' in val:
                return 'background-color: #c62828; color: white; font-weight: bold'
            elif 'HOLD' in val:
                return 'background-color: #f9a825; color: black; font-weight: bold'
        return ''

    # Selecionar colunas para mostrar
    cols_to_show = ['Ativo', 'Qtd', 'Preço_Medio', 'Preço_Atual', 'Meta_Lucro', 'Resultado_%', 'STATUS']
    
    # Exibir tabela estilizada
    st.dataframe(
        df_display[cols_to_show].style.applymap(color_coding, subset=['STATUS'])
        .format({
            'Qtd': '{:.6f}',
            'Preço_Medio': '$ {:.2f}',
            'Preço_Atual': '$ {:.2f}',
            'Meta_Lucro': '$ {:.2f}',
            'Resultado_%': '{:.2f}%'
        }),
        use_container_width=True,
        height=(len(df_display) + 1) * 35 + 3
    )

    # Botão de Reset
    st.divider()
    if st.button("🗑️ Limpar Carteira e Começar do Zero"):
        st.session_state['portfolio'] = pd.DataFrame(columns=['Ativo', 'ID_Coingecko', 'Qtd', 'Preço_Medio', 'Meta_Lucro', 'Stop_Loss'])
        st.rerun()

else:
    # Mensagem de Boas-vindas se estiver vazio
    st.info("👈 Use a barra lateral para adicionar sua primeira criptomoeda.")
    st.markdown("""
    **Como encontrar o ID CoinGecko?**
    1. Entre no site coingecko.com
    2. Pesquise a moeda (ex: Render)
    3. Olhe a URL: coingecko.com/en/coins/**render-token**
    4. O ID é a parte final: `render-token`
    """)
