import streamlit as st
import requests
import base64
import time

# --- CONFIGURAÇÃO DE AMBIENTE DE ELITE ---
st.set_page_config(page_title="CIA OPS STATION", layout="centered", initial_sidebar_state="collapsed")

# Chave API Integrada
GEMINI_API_KEY = "AIzaSyCX1DQKvznD4oVLdXyZZNQuCuFqMkr4ZPw"
DATABASE_PLACAS = ["BRA2E19", "KGT-4590", "ABC7J89", "RIO2K25", "CUSTOM (DIGITAR)"]

st.markdown("""
    <style>
    /* REMOÇÃO TOTAL DE PROPAGANDAS E ELEMENTOS DO STREAMLIT */
    header, footer, .stDeployButton, [data-testid="stDecoration"], 
    [data-testid="stStatusWidget"], button[title="Manage app"],
    .viewerBadge_container__1QS13, .stAppDeployButton {
        display: none !important;
        visibility: hidden !important;
        opacity: 0 !important;
        height: 0 !important;
    }
    
    /* FUNDO TÁTICO E MAPA MUNDI DINÂMICO */
    .stApp { background-color: #000508; color: #00f2fe; font-family: 'Courier New', monospace; }
    
    .map-overlay {
        position: fixed; top: 0; left: 0; width: 100vw; height: 100vh;
        background-image: url('https://upload.wikimedia.org/wikipedia/commons/e/ec/World_map_blank_without_borders.svg');
        background-size: 300%; background-position: center; opacity: 0.2;
        filter: invert(1) sepia(1) saturate(5) hue-rotate(170deg) brightness(0.7);
        animation: pan 180s linear infinite; z-index: -1;
        pointer-events: none;
    }
    @keyframes pan { 0% { background-position: 0% 50%; } 100% { background-position: 100% 50%; } }

    /* HUD PARA IPHONE 15 (DYNAMIC ISLAND COMPATIBLE) */
    .hud-container {
        padding-top: 40px;
        background: rgba(0, 15, 25, 0.75);
        backdrop-filter: blur(15px);
        border: 1px solid rgba(0, 242, 254, 0.3);
        border-radius: 20px;
        padding: 20px;
        margin-bottom: 10px;
    }

    .stButton>button {
        background: rgba(0, 242, 254, 0.1) !important;
        color: #00f2fe !important; border: 1px solid #00f2fe !important;
        width: 100%; font-weight: bold; border-radius: 10px;
    }

    .logout-btn>div>button {
        background: rgba(255, 0, 0, 0.1) !important;
        color: #ff4b4b !important; border: 1px solid #ff4b4b !important;
        font-size: 10px !important; margin-top: 20px;
    }
    </style>
    <div class="map-overlay"></div>
    """, unsafe_allow_html=True)

if 'auth' not in st.session_state: st.session_state.auth = False
if 'logs' not in st.session_state: st.session_state.logs = ["SISTEMA INICIALIZADO"]
if 'radar' not in st.session_state: st.session_state.radar = False

def add_log(msg):
    st.session_state.logs.insert(0, f"» {time.strftime('%H:%M:%S')} | {msg}")

# --- TELA DE ACESSO ---
if not st.session_state.auth:
    st.markdown("<div style='height: 15vh;'></div>", unsafe_allow_html=True)
    st.markdown("<center><img src='https://upload.wikimedia.org/wikipedia/commons/2/25/Seal_of_the_Central_Intelligence_Agency.svg' width='100'></center>", unsafe_allow_html=True)
    st.markdown("<h3 style='text-align: center; color: #00f2fe; letter-spacing: 5px;'>CIA LOGIN</h3>", unsafe_allow_html=True)
    with st.container():
        st.markdown('<div class="hud-container">', unsafe_allow_html=True)
        pw = st.text_input("PIN", type="password")
        if st.button("AUTHORIZE") or pw == "0000":
            if pw == "0000":
                st.session_state.auth = True
                st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
    st.stop()

# --- INTERFACE OPERACIONAL ---
st.markdown("<p style='text-align: center; font-size: 9px; opacity: 0.7;'>GLOBAL_UPLINK: ACTIVE | CAMPOS_RJ</p>", unsafe_allow_html=True)

# Bloco de Controle de Alvos
st.markdown('<div class="hud-container">', unsafe_allow_html=True)
opcao = st.selectbox("WATCHLIST", DATABASE_PLACAS)
target = st.text_input("ID ALVO", value="" if opcao == "CUSTOM (DIGITAR)" else opcao).upper()

radar_color = "🔴" if st.session_state.radar else "🟢"
if st.button(f"{radar_color} TOGGLE RADAR"):
    st.session_state.radar = not st.session_state.radar
    add_log(f"RADAR: {'ON' if st.session_state.radar else 'OFF'}")
st.markdown('</div>', unsafe_allow_html=True)

# Câmera / Scanner
st.markdown('<div class="hud-container">', unsafe_allow_html=True)
img = st.camera_input("")
st.markdown('</div>', unsafe_allow_html=True)

# Lógica de Detecção
if st.session_state.radar and img and target:
    b64 = base64.b64encode(img.getvalue()).decode('utf-8')
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"
    payload = {"contents": [{"parts": [{"text": "Identify license plate text or return NULL."}, {"inline_data": {"mime_type": "image/jpeg", "data": b64}}]}]}
    
    try:
        res = requests.post(url, json=payload).json()
        det = res['candidates'][0]['content']['parts'][0]['text'].strip().upper()
        if det != "NULL":
            add_log(f"VISTO: {det}")
            if target in det:
                add_log("🚨 ALVO ENCONTRADO 🚨")
                st.balloons()
        else:
            add_log("SCANNING AREA...")
    except:
        add_log("SIGNAL LOST")
    time.sleep(2)
    st.rerun()

# Terminal e Logout
st.markdown(f'<div style="background:rgba(0,0,0,0.8); color:#00f2fe; padding:10px; font-size:10px; border-left:3px solid #00f2fe; border-radius:5px;">{"<br>".join(st.session_state.logs[:3])}</div>', unsafe_allow_html=True)

st.markdown('<div class="logout-btn">', unsafe_allow_html=True)
if st.button("TERMINATE SESSION"):
    st.session_state.auth = False
    st.rerun()
st.markdown('</div>', unsafe_allow_html=True)
