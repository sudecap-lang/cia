import streamlit as st
import requests
import base64
import time

# --- CONFIGURAÇÃO DE AMBIENTE TÁTICO ---
st.set_page_config(page_title="CIA OPS STATION", layout="centered", initial_sidebar_state="collapsed")

# Chave API integrada
GEMINI_API_KEY = "AIzaSyCX1DQKvznD4oVLdXyZZNQuCuFqMkr4ZPw"

# BANCO DE DADOS DE PLACAS PESQUISADAS
DATABASE_PLACAS = [
    "BRA2E19", 
    "KGT-4590", 
    "LSU-1234", 
    "ABC7J89", 
    "RIO2K25",
    "CUSTOM (DIGITAR)"
]

st.markdown("""
    <style>
    .stApp { background-color: #01080b; color: #4facfe; font-family: 'Courier New', monospace; }
    
    .map-bg {
        position: fixed; top: 0; left: 0; width: 100vw; height: 100vh;
        background-image: url('https://upload.wikimedia.org/wikipedia/commons/e/ec/World_map_blank_without_borders.svg');
        background-size: 280%; background-position: center; opacity: 0.12;
        filter: invert(1) hue-rotate(185deg) brightness(0.6);
        animation: pan 200s linear infinite; z-index: -1;
    }
    @keyframes pan { 0% { background-position: 0% 50%; } 100% { background-position: 100% 50%; } }

    .main-panel {
        background: rgba(0, 15, 25, 0.85);
        border: 1px solid rgba(0, 242, 254, 0.3);
        border-radius: 8px; padding: 25px;
    }

    /* Estilo para o Seletor (Dropdown) */
    .stSelectbox>div>div {
        background: rgba(0, 5, 10, 0.9) !important; color: #00f2fe !important;
        border: 1px solid #1a3a5a !important;
    }

    .stTextInput>div>div>input {
        background: rgba(0, 5, 10, 0.9) !important; color: #00f2fe !important;
        border: 1px solid #1a3a5a !important; text-align: center;
    }
    
    .stButton>button {
        background: #208080; color: #fff; border: none;
        text-transform: uppercase; font-weight: bold; width: 100%; height: 45px;
    }

    .terminal-box {
        background: rgba(0, 0, 0, 0.8); border-left: 3px solid #4facfe;
        padding: 15px; font-size: 11px; color: #4facfe;
    }

    header {visibility: hidden;}
    footer {visibility: hidden;}
    </style>
    <div class="map-bg"></div>
    """, unsafe_allow_html=True)

if 'auth' not in st.session_state: st.session_state.auth = False
if 'logs' not in st.session_state: st.session_state.logs = ["SISTEMA EM ESPERA."]
if 'radar' not in st.session_state: st.session_state.radar = False

def add_log(msg):
    st.session_state.logs.insert(0, f"» {time.strftime('%H:%M:%S')} | {msg}")

# --- TELA DE LOGIN ---
if not st.session_state.auth:
    st.markdown("<div style='height: 8vh;'></div>", unsafe_allow_html=True)
    st.markdown("<div style='text-align: center;'><img src='https://upload.wikimedia.org/wikipedia/commons/2/25/Seal_of_the_Central_Intelligence_Agency.svg' width='120'></div>", unsafe_allow_html=True)
    st.markdown("<h3 style='text-align: center; color: #4facfe; letter-spacing: 4px; margin-bottom: 25px;'>CIA OPS STATION</h3>", unsafe_allow_html=True)
    
    with st.container():
        st.markdown('<div class="main-panel">', unsafe_allow_html=True)
        password = st.text_input("SECURITY PASSWORD", type="password", placeholder="••••")
        if st.button("ACCESS SYSTEM") or password == "0000":
            if password == "0000":
                st.session_state.auth = True
                add_log("UPLINK ACTIVE | CAMPOS_RJ")
                st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
    st.stop()

# --- DASHBOARD OPERACIONAL ---
st.markdown("<div style='text-align: center; font-size: 9px; opacity: 0.6;'>WATCHLIST_UPLINK | SATELLITE_SCAN</div>", unsafe_allow_html=True)

with st.sidebar:
    st.markdown("### 🎯 WATCHLIST CONTROL")
    
    # SELETOR DE PLACAS DO BANCO DE DADOS
    opcao = st.selectbox("SELECIONAR ALVO", DATABASE_PLACAS)
    
    if opcao == "CUSTOM (DIGITAR)":
        target = st.text_input("DIGITAR PLACA", value="").upper()
    else:
        target = opcao
        st.info(f"ALVO ATUAL: {target}")

    if st.button("TOGGLE AUTO-RADAR"):
        st.session_state.radar = not st.session_state.radar
        add_log(f"RADAR ON: TARGET {target}")
    
    st.divider()
    if st.button("LOGOUT"):
        st.session_state.auth = False
        st.rerun()

# Scanner Óptico (Câmera)
img = st.camera_input("")

if st.session_state.radar and img and target:
    b64 = base64.b64encode(img.getvalue()).decode('utf-8')
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"
    payload = {"contents": [{"parts": [{"text": "Extract plate or NULL."}, {"inline_data": {"mime_type": "image/jpeg", "data": b64}}]}]}
    
    try:
        res = requests.post(url, json=payload).json()
        det = res['candidates'][0]['content']['parts'][0]['text'].strip().upper()
        if det != "NULL":
            add_log(f"DETECTED: {det}")
            if target in det:
                add_log(f"🚨 TARGET MATCH: {det} 🚨")
                st.balloons()
                st.error(f"CONFIRMADO: ALVO LOCALIZADO ({det})")
        else:
            add_log("SCANNING... AREA CLEAR")
    except:
        add_log("UPLINK ERROR")
    
    time.sleep(4)
    st.rerun()

# Terminal de Logs
st.markdown("<div style='height: 20px;'></div>", unsafe_allow_html=True)
log_text = "<br>".join(st.session_state.logs[:4])
st.markdown(f'<div class="terminal-box">{log_text}</div>', unsafe_allow_html=True)
