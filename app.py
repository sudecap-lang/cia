import streamlit as st
import requests
import base64
import time
import folium
from streamlit_folium import folium_static

# --- CONFIGURAÇÃO TÁTICA ---
st.set_page_config(page_title="CIA GLOBAL TRACKER", layout="wide", initial_sidebar_state="collapsed")

# Chave API
GEMINI_API_KEY = "AIzaSyCX1DQKvznD4oVLdXyZZNQuCuFqMkr4ZPw"

# BANCO DE DADOS DE ALVOS
DATABASE_PLACAS = ["BRA2E19", "KGT-4590", "LSU-1234", "ABC7J89", "RIO2K25", "CUSTOM (DIGITAR)"]

# --- ESTILIZAÇÃO E REMOÇÃO DE PROPAGANDA ---
st.markdown("""
    <style>
    /* REMOVER PROPAGANDA E ELEMENTOS DO STREAMLIT */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .stDeployButton {display:none;}
    [data-testid="stStatusWidget"] {display:none;}
    div[data-testid="stDecoration"] {display:none;}
    
    /* FUNDO ESCURO TÁTICO */
    .stApp {
        background-color: #00080b;
    }

    /* PAINÉIS HUD (FLUTUANTES) */
    .hud-panel {
        background: rgba(0, 15, 25, 0.85);
        backdrop-filter: blur(10px);
        border: 2px solid #00f2fe;
        border-radius: 15px;
        padding: 20px;
        box-shadow: 0 0 20px rgba(0, 242, 254, 0.2);
    }

    .stButton>button {
        background: rgba(0, 242, 254, 0.2) !important;
        color: #00f2fe !important;
        border: 1px solid #00f2fe !important;
        text-transform: uppercase;
        font-weight: bold;
        letter-spacing: 2px;
    }

    /* TERMINAL */
    .terminal {
        background: rgba(0, 0, 0, 0.9);
        color: #00f2fe;
        font-family: 'Courier New', monospace;
        padding: 10px;
        font-size: 11px;
        border-left: 5px solid #00f2fe;
    }
    </style>
    """, unsafe_allow_html=True)

if 'auth' not in st.session_state: st.session_state.auth = False
if 'logs' not in st.session_state: st.session_state.logs = ["SATELLITE LINK ONLINE"]
if 'radar' not in st.session_state: st.session_state.radar = False

def add_log(msg):
    st.session_state.logs.insert(0, f"» {time.strftime('%H:%M:%S')} | {msg}")

# --- TELA DE LOGIN ---
if not st.session_state.auth:
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        st.markdown("<div style='height: 15vh;'></div>", unsafe_allow_html=True)
        st.markdown("<center><img src='https://upload.wikimedia.org/wikipedia/commons/2/25/Seal_of_the_Central_Intelligence_Agency.svg' width='120'></center>", unsafe_allow_html=True)
        st.markdown("<h2 style='text-align: center; color: #00f2fe; letter-spacing: 5px;'>AGENT LOGIN</h2>", unsafe_allow_html=True)
        password = st.text_input("SECURITY PIN", type="password")
        if st.button("ACCESS") or password == "0000":
            st.session_state.auth = True
            st.rerun()
    st.stop()

# --- INTERFACE OPERACIONAL (MAPA DINÂMICO) ---

# Criar Mapa Real (GPS Campos dos Goytacazes)
# Coordenadas aproximadas de Campos, RJ
m = folium.Map(location=[-21.7545, -41.3245], zoom_start=13, tiles="CartoDB dark_matter")
folium.Marker(
    [-21.7545, -41.3245], 
    popup="AGENT LOCATION", 
    icon=folium.Icon(color="blue", icon="info-sign")
).add_to(m)

# Colunas HUD
c1, c2 = st.columns([1, 1])

with c1:
    st.markdown('<div class="hud-panel">', unsafe_allow_html=True)
    st.markdown("### 📡 SATELLITE RADAR")
    folium_static(m, width=350, height=300)
    st.markdown('</div>', unsafe_allow_html=True)

with c2:
    st.markdown('<div class="hud-panel">', unsafe_allow_html=True)
    st.markdown("### 🎯 TARGET CONTROL")
    opcao = st.selectbox("WATCHLIST", DATABASE_PLACAS)
    target = st.text_input("PLATE ID", value="" if opcao == "CUSTOM (DIGITAR)" else opcao).upper()
    
    if st.button("ACTIVATE SCANNER"):
        st.session_state.radar = not st.session_state.radar
        add_log(f"SCANNER: {st.session_state.radar}")
    st.markdown('</div>', unsafe_allow_html=True)

# SCANNER DE CÂMERA
st.markdown("<br>", unsafe_allow_html=True)
st.markdown('<div class="hud-panel">', unsafe_allow_html=True)
img = st.camera_input("OPTICAL FEED")
st.markdown('</div>', unsafe_allow_html=True)

# PROCESSAMENTO GEMINI
if st.session_state.radar and img and target:
    b64 = base64.b64encode(img.getvalue()).decode('utf-8')
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"
    payload = {"contents": [{"parts": [{"text": "Extract plate. ONLY the plate name."}, {"inline_data": {"mime_type": "image/jpeg", "data": b64}}]}]}
    
    try:
        res = requests.post(url, json=payload).json()
        det = res['candidates'][0]['content']['parts'][0]['text'].strip().upper()
        if det != "NULL":
            add_log(f"DETETADO: {det}")
            if target in det:
                add_log("🚨 ALVO LOCALIZADO! 🚨")
                st.warning(f"MATCH: {det}")
        else:
            add_log("SEARCHING...")
    except:
        add_log("CONNECTION LOST")
    time.sleep(2)
    st.rerun()

# TERMINAL DE LOGS FINAL
log_display = "<br>".join(st.session_state.logs[:3])
st.markdown(f'<div class="terminal">{log_display}</div>', unsafe_allow_html=True)
