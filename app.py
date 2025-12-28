import streamlit as st
import requests
import base64
import time

# --- CONFIGURAÇÃO TÁTICA DE ELITE ---
st.set_page_config(page_title="CIA OPS STATION", layout="centered", initial_sidebar_state="collapsed")

# Chave API Integrada (Protocolo Seguro)
GEMINI_API_KEY = "AIzaSyCX1DQKvznD4oVLdXyZZNQuCuFqMkr4ZPw"
DATABASE_PLACAS = ["BRA2E19", "KGT-4590", "ABC7J89", "RIO2K25", "CUSTOM (DIGITAR)"]

st.markdown("""
    <style>
    /* REMOÇÃO RADICAL DE PROPAGANDAS E ELEMENTOS STREAMLIT */
    header, footer, .stDeployButton, [data-testid="stDecoration"], 
    [data-testid="stStatusWidget"], button[title="Manage app"] {
        display: none !important;
        visibility: hidden !important;
    }
    
    .stApp { background-color: #00050a; color: #00f2fe; font-family: 'Courier New', monospace; }

    /* RADAR DINÂMICO DE FUNDO (SEM DEPENDÊNCIA DE MÓDULOS) */
    .radar-bg {
        position: fixed; top: 0; left: 0; width: 100vw; height: 100vh;
        background: radial-gradient(circle, rgba(0,242,254,0.05) 0%, rgba(0,0,0,1) 80%);
        z-index: -1;
    }
    
    .map-ani {
        position: fixed; top: 0; left: 0; width: 100vw; height: 100vh;
        background-image: url('https://upload.wikimedia.org/wikipedia/commons/e/ec/World_map_blank_without_borders.svg');
        background-size: 350%; background-position: center; opacity: 0.15;
        filter: invert(1) hue-rotate(180deg) brightness(0.7);
        animation: pan 180s linear infinite; z-index: -2;
    }
    @keyframes pan { 0% { background-position: 0% 50%; } 100% { background-position: 100% 50%; } }

    /* PAINÉIS HUD IPHONE 15 */
    .hud-panel {
        background: rgba(0, 15, 25, 0.8);
        backdrop-filter: blur(12px);
        border: 1px solid rgba(0, 242, 254, 0.4);
        border-radius: 15px;
        padding: 15px; margin-bottom: 10px;
        box-shadow: 0 0 15px rgba(0, 242, 254, 0.1);
    }

    .stTextInput>div>div>input, .stSelectbox>div>div {
        background: rgba(0, 0, 0, 0.7) !important;
        color: #00f2fe !important; border: 1px solid #00f2fe !important;
    }
    
    .stButton>button {
        background: rgba(0, 242, 254, 0.15) !important;
        color: #00f2fe !important; border: 1px solid #00f2fe !important;
        width: 100%; font-weight: bold; letter-spacing: 2px;
    }

    .log-box {
        background: rgba(0, 0, 0, 0.9); border-left: 3px solid #00f2fe;
        padding: 8px; font-size: 10px; color: #00f2fe; margin-top: 5px;
    }
    </style>
    <div class="map-ani"></div>
    <div class="radar-bg"></div>
    """, unsafe_allow_html=True)

if 'auth' not in st.session_state: st.session_state.auth = False
if 'logs' not in st.session_state: st.session_state.logs = ["SATELLITE_LINK: OK"]
if 'radar' not in st.session_state: st.session_state.radar = False

def add_log(msg):
    st.session_state.logs.insert(0, f"» {time.strftime('%H:%M:%S')} | {msg}")

# --- PROTOCOLO DE ACESSO ---
if not st.session_state.auth:
    st.markdown("<div style='height: 12vh;'></div>", unsafe_allow_html=True)
    st.markdown("<center><img src='https://upload.wikimedia.org/wikipedia/commons/2/25/Seal_of_the_Central_Intelligence_Agency.svg' width='100'></center>", unsafe_allow_html=True)
    st.markdown("<h3 style='text-align: center; color: #00f2fe; letter-spacing: 5px;'>AGENT LOGIN</h3>", unsafe_allow_html=True)
    st.markdown('<div class="hud-panel">', unsafe_allow_html=True)
    pw = st.text_input("PIN ACCESS", type="password")
    if st.button("AUTHORIZE") or pw == "0000":
        if pw == "0000":
            st.session_state.auth = True
            st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)
    st.stop()

# --- DASHBOARD HUD (DIRETO NA TELA) ---
st.markdown("<p style='text-align: center; font-size: 10px; opacity: 0.7;'>GPS_SYNC: CAMPOS_RJ | OPS_STATION_ACTIVE</p>", unsafe_allow_html=True)

st.markdown('<div class="hud-panel">', unsafe_allow_html=True)
opcao = st.selectbox("BANCO DE DADOS (WATCHLIST)", DATABASE_PLACAS)
target = st.text_input("ALVO ATUAL", value="" if opcao == "CUSTOM (DIGITAR)" else opcao).upper()

radar_btn = "🔴 STOP RADAR" if st.session_state.radar else "🟢 START AUTO-RADAR"
if st.button(radar_btn):
    st.session_state.radar = not st.session_state.radar
    add_log(f"RADAR {'ACTIVE' if st.session_state.radar else 'OFF'}")
st.markdown('</div>', unsafe_allow_html=True)

# Scanner Óptico Central
st.markdown('<div class="hud-panel">', unsafe_allow_html=True)
img = st.camera_input("")
st.markdown('</div>', unsafe_allow_html=True)

# Lógica de Detecção Inteligente
if st.session_state.radar and img and target:
    b64 = base64.b64encode(img.getvalue()).decode('utf-8')
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"
    payload = {"contents": [{"parts": [{"text": "Extract license plate text or return NULL."}, {"inline_data": {"mime_type": "image/jpeg", "data": b64}}]}]}
    
    try:
        res = requests.post(url, json=payload).json()
        det = res['candidates'][0]['content']['parts'][0]['text'].strip().upper()
        if det != "NULL":
            add_log(f"VISTO: {det}")
            if target in det:
                add_log("🚨 ALVO IDENTIFICADO 🚨")
                st.balloons()
        else:
            add_log("SCANNING... CLEAR")
    except:
        add_log("SIGNAL LOST")
    time.sleep(3)
    st.rerun()

# Logs do Terminal
log_txt = "<br>".join(st.session_state.logs[:3])
st.markdown(f'<div class="log-box">{log_txt}</div>', unsafe_allow_html=True)
