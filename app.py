import streamlit as st
import requests
import base64
import time

# --- CONFIGURAÇÃO DE AMBIENTE TÁTICO ---
st.set_page_config(page_title="CIA OPS STATION", layout="centered", initial_sidebar_state="collapsed")

# Chave API integrada
GEMINI_API_KEY = "AIzaSyCX1DQKvznD4oVLdXyZZNQuCuFqMkr4ZPw"

# BANCO DE DADOS DE ALVOS
DATABASE_PLACAS = ["BRA2E19", "KGT-4590", "LSU-1234", "ABC7J89", "RIO2K25", "CUSTOM (DIGITAR)"]

st.markdown("""
    <style>
    /* Reset total e fundo animado */
    .stApp { background: #000b14; color: #00f2fe; font-family: 'Courier New', monospace; }
    
    .map-bg {
        position: fixed; top: 0; left: 0; width: 100vw; height: 100vh;
        background-image: url('https://upload.wikimedia.org/wikipedia/commons/e/ec/World_map_blank_without_borders.svg');
        background-size: 300%; background-position: center; opacity: 0.2;
        filter: invert(1) sepia(1) saturate(5) hue-rotate(175deg) brightness(0.8);
        animation: pan 150s linear infinite; z-index: -1;
    }
    @keyframes pan { 0% { background-position: 0% 50%; } 100% { background-position: 100% 50%; } }

    /* Esconder Banners e Menus do Streamlit (Propagandas) */
    footer {visibility: hidden;}
    header {visibility: hidden;}
    #MainMenu {visibility: hidden;}
    .stDeployButton {display:none;}
    div[data-testid="stStatusWidget"] {display:none;}

    /* Painéis de Vidro Táticos */
    .main-panel {
        background: rgba(0, 20, 35, 0.75);
        backdrop-filter: blur(15px);
        border: 1px solid rgba(0, 242, 254, 0.3);
        border-radius: 15px;
        padding: 20px;
        margin-bottom: 15px;
    }

    /* Ajuste de inputs para iPhone */
    .stSelectbox>div>div, .stTextInput>div>div>input {
        background: rgba(0, 0, 0, 0.6) !important;
        color: #00f2fe !important;
        border: 1px solid rgba(0, 242, 254, 0.4) !important;
        border-radius: 8px !important;
        height: 45px !important;
    }
    
    .stButton>button {
        background: rgba(0, 242, 254, 0.2) !important;
        color: #00f2fe !important;
        border: 1px solid #00f2fe !important;
        font-weight: bold; width: 100%; height: 50px;
        text-transform: uppercase; letter-spacing: 2px;
    }

    .terminal-box {
        background: rgba(0, 0, 0, 0.8);
        border-left: 4px solid #00f2fe;
        padding: 12px; font-size: 10px; color: #00f2fe;
        text-transform: uppercase; margin-top: 10px;
    }
    </style>
    <div class="map-bg"></div>
    """, unsafe_allow_html=True)

if 'auth' not in st.session_state: st.session_state.auth = False
if 'logs' not in st.session_state: st.session_state.logs = ["SISTEMA EM STANDBY..."]
if 'radar' not in st.session_state: st.session_state.radar = False

def add_log(msg):
    st.session_state.logs.insert(0, f"» {time.strftime('%H:%M:%S')} | {msg}")

# --- TELA DE LOGIN ---
if not st.session_state.auth:
    st.markdown("<div style='height: 10vh;'></div>", unsafe_allow_html=True)
    st.markdown("<div style='text-align: center;'><img src='https://upload.wikimedia.org/wikipedia/commons/2/25/Seal_of_the_Central_Intelligence_Agency.svg' width='110' style='filter: drop-shadow(0 0 10px #00f2fe);'></div>", unsafe_allow_html=True)
    st.markdown("<h3 style='text-align: center; color: #00f2fe; letter-spacing: 10px; margin-top: 15px;'>CIA LOGIN</h3>", unsafe_allow_html=True)
    
    st.markdown('<div class="main-panel">', unsafe_allow_html=True)
    password = st.text_input("PIN DE ACESSO", type="password", placeholder="••••")
    if st.button("AUTHENTICATE") or password == "0000":
        if password == "0000":
            st.session_state.auth = True
            add_log("UPLINK ESTABLISHED | CAMPOS_RJ")
            st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)
    st.stop()

# --- INTERFACE PRINCIPAL (SEM MENU LATERAL) ---
st.markdown("<div style='text-align: right; font-size: 9px; opacity: 0.8; margin-bottom: 5px;'>UPLINK: ACTIVE | GPS: CAMPOS_RJ</div>", unsafe_allow_html=True)

# 1. CONTROLES DE ALVO (DIRETO NA TELA)
st.markdown('<div class="main-panel">', unsafe_allow_html=True)
st.markdown("<p style='font-size: 11px; margin-bottom: 5px;'>🎯 SELECIONAR ALVO DA WATCHLIST:</p>", unsafe_allow_html=True)
opcao = st.selectbox("", DATABASE_PLACAS, label_visibility="collapsed")

if opcao == "CUSTOM (DIGITAR)":
    target = st.text_input("DIGITE A PLACA ALVO", placeholder="BRA2E19").upper()
else:
    target = opcao

radar_label = "🔴 DESATIVAR RADAR" if st.session_state.radar else "🟢 ATIVAR AUTO-RADAR"
if st.button(radar_label):
    st.session_state.radar = not st.session_state.radar
    add_log(f"RADAR: {'ACTIVE' if st.session_state.radar else 'OFF'}")
st.markdown('</div>', unsafe_allow_html=True)

# 2. SCANNER ÓPTICO
st.markdown('<div class="main-panel">', unsafe_allow_html=True)
img = st.camera_input("")
st.markdown('</div>', unsafe_allow_html=True)

# LÓGICA DE PROCESSAMENTO
if st.session_state.radar and img and target:
    b64 = base64.b64encode(img.getvalue()).decode('utf-8')
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"
    payload = {"contents": [{"parts": [{"text": "Identify plate. Return ONLY plate or NULL."}, {"inline_data": {"mime_type": "image/jpeg", "data": b64}}]}]}
    
    try:
        res = requests.post(url, json=payload).json()
        det = res['candidates'][0]['content']['parts'][0]['text'].strip().upper()
        if det != "NULL":
            add_log(f"DETETADO: {det}")
            if target in det:
                add_log("🚨 TARGET MATCH IDENTIFIED! 🚨")
                st.balloons()
        else:
            add_log("SCANNING AREA... CLEAR")
    except:
        add_log("SATELLITE ERROR")
    
    time.sleep(3)
    st.rerun()

# 3. TERMINAL DE LOGS
log_text = "<br>".join(st.session_state.logs[:3])
st.markdown(f'<div class="terminal-box">{log_text}</div>', unsafe_allow_html=True)
