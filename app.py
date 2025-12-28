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
    /* Reset de Fundo e Layout */
    .stApp {
        background: #000b14;
        color: #00f2fe;
        font-family: 'Courier New', monospace;
        overflow: hidden;
    }

    /* MAPA MUNDI ANIMADO - CAMADA FUNDO */
    .map-bg {
        position: fixed;
        top: 0; left: 0;
        width: 100vw; height: 100vh;
        background-image: url('https://upload.wikimedia.org/wikipedia/commons/e/ec/World_map_blank_without_borders.svg');
        background-size: 300%;
        background-position: center;
        opacity: 0.25;
        filter: invert(1) sepia(1) saturate(5) hue-rotate(175deg) brightness(0.8);
        animation: pan 150s linear infinite;
        z-index: -1;
    }
    
    /* EFEITO DE VARREDURA DE RADAR */
    .radar-sweep {
        position: fixed;
        top: 0; left: 0; width: 100vw; height: 100vh;
        background: linear-gradient(to bottom, rgba(0,242,254,0) 0%, rgba(0,242,254,0.05) 50%, rgba(0,242,254,0) 100%);
        background-size: 100% 200%;
        animation: sweep 4s linear infinite;
        pointer-events: none;
        z-index: 0;
    }

    @keyframes pan { 0% { background-position: 0% 50%; } 100% { background-position: 100% 50%; } }
    @keyframes sweep { 0% { background-position: 0% -100%; } 100% { background-position: 0% 100%; } }

    /* PAINÉIS TRANSPARENTES (GLASSMORPHISM) */
    .main-panel {
        background: rgba(0, 20, 35, 0.7);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(0, 242, 254, 0.2);
        border-radius: 12px;
        padding: 20px;
        margin-top: 10px;
        z-index: 10;
    }

    .stTextInput>div>div>input, .stSelectbox>div>div {
        background: rgba(0, 0, 0, 0.5) !important;
        color: #00f2fe !important;
        border: 1px solid rgba(0, 242, 254, 0.3) !important;
        border-radius: 5px !important;
    }
    
    .stButton>button {
        background: rgba(0, 242, 254, 0.15) !important;
        color: #00f2fe !important;
        border: 1px solid #00f2fe !important;
        letter-spacing: 2px;
        font-weight: bold;
        width: 100%;
    }

    .terminal-box {
        background: rgba(0, 10, 20, 0.8);
        border-left: 3px solid #00f2fe;
        padding: 10px;
        font-size: 10px;
        color: #00f2fe;
        text-transform: uppercase;
        margin-top: 15px;
    }

    header {visibility: hidden;}
    footer {visibility: hidden;}
    #MainMenu {visibility: hidden;}
    </style>
    <div class="map-bg"></div>
    <div class="radar-sweep"></div>
    """, unsafe_allow_html=True)

if 'auth' not in st.session_state: st.session_state.auth = False
if 'logs' not in st.session_state: st.session_state.logs = ["SISTEMA EM STANDBY..."]
if 'radar' not in st.session_state: st.session_state.radar = False

def add_log(msg):
    st.session_state.logs.insert(0, f"» {time.strftime('%H:%M:%S')} | {msg}")

# --- LOGIN TÁTICO ---
if not st.session_state.auth:
    st.markdown("<div style='height: 10vh;'></div>", unsafe_allow_html=True)
    st.markdown("<div style='text-align: center;'><img src='https://upload.wikimedia.org/wikipedia/commons/2/25/Seal_of_the_Central_Intelligence_Agency.svg' width='100' style='filter: drop-shadow(0 0 10px #00f2fe); opacity: 0.8;'></div>", unsafe_allow_html=True)
    st.markdown("<h3 style='text-align: center; color: #00f2fe; letter-spacing: 8px; margin-top: 20px;'>SECURE ACCESS</h3>", unsafe_allow_html=True)
    
    with st.container():
        st.markdown('<div class="main-panel">', unsafe_allow_html=True)
        password = st.text_input("ENTER AGENT PIN", type="password", placeholder="••••")
        if st.button("AUTHORIZE") or password == "0000":
            if password == "0000":
                st.session_state.auth = True
                add_log("UPLINK ESTABLISHED | CAMPOS_RJ")
                st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
    st.stop()

# --- DASHBOARD DE OPERAÇÕES ---
st.markdown("<div style='text-align: center; font-size: 9px; opacity: 0.8; letter-spacing: 2px;'>GLOBAL_MONITORING: ACTIVE</div>", unsafe_allow_html=True)

with st.sidebar:
    st.markdown("### 🎯 MISSION CONTROL")
    opcao = st.selectbox("ALVO (WATCHLIST)", DATABASE_PLACAS)
    target = st.text_input("MANUAL ID", value="" if opcao == "CUSTOM (DIGITAR)" else opcao).upper()
    
    if st.button("TOGGLE AUTO-RADAR"):
        st.session_state.radar = not st.session_state.radar
        add_log(f"RADAR: {'ON' if st.session_state.radar else 'OFF'}")
    
    st.divider()
    if st.button("LOGOUT"):
        st.session_state.auth = False
        st.rerun()

# Scanner de Câmera (Fica dentro de um painel transparente)
st.markdown('<div class="main-panel">', unsafe_allow_html=True)
img = st.camera_input("")
st.markdown('</div>', unsafe_allow_html=True)

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
                add_log("!!! ALVO IDENTIFICADO !!!")
                st.balloons()
        else:
            add_log("VARREDURA: PISTA LIMPA")
    except:
        add_log("SATELLITE LINK ERROR")
    
    time.sleep(3)
    st.rerun()

# Terminal de Logs
log_text = "<br>".join(st.session_state.logs[:3])
st.markdown(f'<div class="terminal-box">{log_text}</div>', unsafe_allow_html=True)
