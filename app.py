import streamlit as st
import requests
import base64
import time

# --- CONFIGURAÇÃO DE AMBIENTE CIR ---
st.set_page_config(page_title="CIR - OPS STATION", layout="centered", initial_sidebar_state="collapsed")

# Chave API e Banco de Dados
GEMINI_API_KEY = "AIzaSyCX1DQKvznD4oVLdXyZZNQuCuFqMkr4ZPw"
DATABASE_PLACAS = ["BRA2E19", "KGT-4590", "ABC7J89", "RIO2K25", "CUSTOM (DIGITAR)"]

st.markdown("""
    <style>
    /* REMOÇÃO TOTAL DE INTERFERÊNCIAS EXTERNAS */
    header, footer, .stDeployButton, [data-testid="stDecoration"], 
    [data-testid="stStatusWidget"], button[title="Manage app"],
    .viewerBadge_container__1QS13, .stAppDeployButton {
        display: none !important; visibility: hidden !important;
        opacity: 0 !important; height: 0 !important;
    }
    
    /* FUNDO TÁTICO E MAPA MUNDI DINÂMICO CIR */
    .stApp { background-color: #000408; color: #00f2fe; font-family: 'Courier New', monospace; }
    
    .map-overlay {
        position: fixed; top: 0; left: 0; width: 100vw; height: 100vh;
        background-image: url('https://upload.wikimedia.org/wikipedia/commons/e/ec/World_map_blank_without_borders.svg');
        background-size: 300%; background-position: center; opacity: 0.18;
        filter: invert(1) sepia(1) saturate(4) hue-rotate(175deg) brightness(0.6);
        animation: pan 200s linear infinite; z-index: -1;
        pointer-events: none;
    }
    @keyframes pan { 0% { background-position: 0% 50%; } 100% { background-position: 100% 50%; } }

    /* HUD PARA IPHONE 15 */
    .hud-container {
        padding-top: 10px;
        background: rgba(0, 10, 20, 0.8);
        backdrop-filter: blur(12px);
        border: 1px solid rgba(0, 242, 254, 0.4);
        border-radius: 18px;
        padding: 20px;
        margin-bottom: 15px;
        box-shadow: 0 0 20px rgba(0, 242, 254, 0.15);
    }

    .stButton>button {
        background: rgba(0, 242, 254, 0.1) !important;
        color: #00f2fe !important; border: 1px solid #00f2fe !important;
        width: 100%; font-weight: bold; border-radius: 8px; height: 50px;
    }

    .stTextInput>div>div>input, .stSelectbox>div>div {
        background: rgba(0, 0, 0, 0.7) !important;
        color: #00f2fe !important; border: 1px solid rgba(0, 242, 254, 0.5) !important;
    }

    /* LOGO CIR MINIMALISTA */
    .cir-logo {
        width: 80px; height: 80px; border: 3px solid #00f2fe;
        border-radius: 50%; display: flex; align-items: center;
        justify-content: center; margin: 0 auto 15px auto;
        font-size: 24px; font-weight: bold; letter-spacing: 3px;
        box-shadow: 0 0 15px #00f2fe; text-shadow: 0 0 5px #00f2fe;
    }
    </style>
    <div class="map-overlay"></div>
    """, unsafe_allow_html=True)

if 'auth' not in st.session_state: st.session_state.auth = False
if 'logs' not in st.session_state: st.session_state.logs = ["CIR SYSTEM ONLINE"]
if 'radar' not in st.session_state: st.session_state.radar = False

def add_log(msg):
    st.session_state.logs.insert(0, f"» {time.strftime('%H:%M:%S')} | {msg}")

# --- PROTOCOLO DE ACESSO CIR ---
if not st.session_state.auth:
    st.markdown("<div style='height: 12vh;'></div>", unsafe_allow_html=True)
    st.markdown('<div class="cir-logo">CIR</div>', unsafe_allow_html=True)
    st.markdown("<h3 style='text-align: center; color: #00f2fe; letter-spacing: 8px;'>SECURE LOGIN</h3>", unsafe_allow_html=True)
    with st.container():
        st.markdown('<div class="hud-container">', unsafe_allow_html=True)
        user = st.text_input("ID OPERADOR")
        pw = st.text_input("PASSWORD", type="password")
        if st.button("AUTHENTICATE"):
            if user.upper() == "OPERATOR" and pw == "8142":
                st.session_state.auth = True
                add_log("OPERATOR ACCESS GRANTED")
                st.rerun()
            else:
                st.error("ACCESS DENIED")
        st.markdown('</div>', unsafe_allow_html=True)
    st.stop()

# --- INTERFACE OPERACIONAL CIR ---
st.markdown("<p style='text-align: center; font-size: 9px; opacity: 0.8; letter-spacing: 2px;'>CIR UPLINK: STABLE | CAMPOS_RJ</p>", unsafe_allow_html=True)

# Bloco de Alvos
st.markdown('<div class="hud-container">', unsafe_allow_html=True)
opcao = st.selectbox("WATCHLIST DATABASE", DATABASE_PLACAS)
target = st.text_input("PLATE TARGET ID", value="" if opcao == "CUSTOM (DIGITAR)" else opcao).upper()

radar_label = "🔴 STOP RADAR" if st.session_state.radar else "🟢 START RADAR"
if st.button(radar_label):
    st.session_state.radar = not st.session_state.radar
    add_log(f"RADAR STATUS: {st.session_state.radar}")
st.markdown('</div>', unsafe_allow_html=True)

# Scanner Central
st.markdown('<div class="hud-container">', unsafe_allow_html=True)
img = st.camera_input("OPTICAL SCANNER")
st.markdown('</div>', unsafe_allow_html=True)

# Lógica de Reconhecimento
if st.session_state.radar and img and target:
    b64 = base64.b64encode(img.getvalue()).decode('utf-8')
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"
    payload = {"contents": [{"parts": [{"text": "Extract plate or NULL."}, {"inline_data": {"mime_type": "image/jpeg", "data": b64}}]}]}
    
    try:
        res = requests.post(url, json=payload).json()
        det = res['candidates'][0]['content']['parts'][0]['text'].strip().upper()
        if det != "NULL":
            add_log(f"DETECTADO: {det}")
            if target in det:
                add_log("🚨 ALVO IDENTIFICADO! 🚨")
                st.balloons()
        else:
            add_log("VARREDURA EM CURSO...")
    except:
        add_log("UPLINK ERROR")
    time.sleep(3)
    st.rerun()

# Logs do Terminal
log_txt = "<br>".join(st.session_state.logs[:3])
st.markdown(f'<div style="background:rgba(0,0,0,0.9); color:#00f2fe; padding:10px; font-size:10px; border-left:3px solid #00f2fe; border-radius:8px;">{log_text}</div>', unsafe_allow_html=True)

if st.button("TERMINATE OPS"):
    st.session_state.auth = False
    st.rerun()
