import streamlit as st
import requests
import base64
import time

# --- CONFIGURAÇÃO CIR HIGH-FIDELITY ---
st.set_page_config(page_title="CIR OPS STATION", layout="centered", initial_sidebar_state="collapsed")

# Chave API e Dados
GEMINI_API_KEY = "AIzaSyCX1DQKvznD4oVLdXyZZNQuCuFqMkr4ZPw"
DATABASE_PLACAS = ["BRA2E19", "KGT-4590", "ABC7J89", "RIO2K25", "CUSTOM (DIGITAR)"]

st.markdown("""
    <style>
    /* BLOQUEIO TOTAL DE INTERFERÊNCIAS */
    header, footer, .stDeployButton, [data-testid="stDecoration"], 
    [data-testid="stStatusWidget"], button[title="Manage app"],
    .viewerBadge_container__1QS13, .stAppDeployButton {
        display: none !important; visibility: hidden !important;
        opacity: 0 !important; height: 0 !important;
    }

    /* FUNDO TÁTICO COM MAPA MUNDI IMERSIVO */
    .stApp {
        background-color: #00080b;
        background-image: url('https://upload.wikimedia.org/wikipedia/commons/e/ec/World_map_blank_without_borders.svg');
        background-size: 250%;
        background-position: center;
        background-repeat: no-repeat;
        background-attachment: fixed;
    }
    
    /* CAMADA DE ESCURECIMENTO PARA O MAPA */
    .stApp::before {
        content: ""; position: fixed; top: 0; left: 0; width: 100%; height: 100%;
        background: rgba(0, 5, 10, 0.85); /* Controla a visibilidade do mapa */
        z-index: -1;
    }

    /* PAINEL CENTRAL (HUD) - EXATAMENTE COMO NA IMAGEM */
    .main-hud {
        background: rgba(0, 20, 30, 0.6);
        backdrop-filter: blur(10px);
        border: 2px solid #00f2fe;
        border-radius: 20px;
        padding: 30px;
        box-shadow: 0 0 30px rgba(0, 242, 254, 0.2);
        margin-top: 20px;
    }

    .cir-header {
        text-align: center; color: #00f2fe; font-size: 28px;
        font-weight: bold; letter-spacing: 5px; margin-bottom: 20px;
        text-shadow: 0 0 10px #00f2fe;
    }

    /* ESTILO DOS BOTÕES E INPUTS */
    .stButton>button {
        background: #00f2fe !important; color: #000 !important;
        font-weight: bold; border-radius: 5px; border: none;
        width: 100%; height: 45px; letter-spacing: 2px;
    }

    .stTextInput>div>div>input, .stSelectbox>div>div {
        background: rgba(0, 0, 0, 0.5) !important;
        color: #fff !important; border: 1px solid #444 !important;
        border-radius: 5px !important;
    }

    /* LOGO CIRCULAR CIR */
    .target-icon {
        width: 80px; height: 80px; border: 3px solid #00f2fe;
        border-radius: 50%; display: flex; align-items: center;
        justify-content: center; margin: 0 auto 10px auto;
        color: #00f2fe; font-size: 20px; font-weight: bold;
        box-shadow: 0 0 20px #00f2fe;
    }
    </style>
    """, unsafe_allow_html=True)

if 'auth' not in st.session_state: st.session_state.auth = False
if 'logs' not in st.session_state: st.session_state.logs = ["CIR SYSTEM: ONLINE"]
if 'radar' not in st.session_state: st.session_state.radar = False

def add_log(msg):
    st.session_state.logs.insert(0, f"» {time.strftime('%H:%M:%S')} | {msg}")

# --- TELA DE LOGIN TÁTICA ---
if not st.session_state.auth:
    st.markdown("<div style='height: 10vh;'></div>", unsafe_allow_html=True)
    st.markdown('<div class="target-icon">CIR</div>', unsafe_allow_html=True)
    st.markdown('<div class="cir-header">CENTRO DE INTELIGÊNCIA</div>', unsafe_allow_html=True)
    
    with st.container():
        st.markdown('<div class="main-hud">', unsafe_allow_html=True)
        user = st.text_input("ID OPERADOR", placeholder="EX: OPERATOR")
        pw = st.text_input("PASSWORD", type="password")
        if st.button("AUTHENTICATE"):
            if user.upper() == "OPERATOR" and pw == "8142":
                st.session_state.auth = True
                add_log("OPERADOR AUTORIZADO")
                st.rerun()
            else:
                st.error("ACCESS DENIED")
        st.markdown('</div>', unsafe_allow_html=True)
    st.stop()

# --- INTERFACE OPERACIONAL (CIR OPS STATION) ---
st.markdown("<p style='text-align: center; color: #00f2fe; font-size: 10px; letter-spacing: 2px;'>CIR_UPLINK: ACTIVE | GPS: CAMPOS_RJ</p>", unsafe_allow_html=True)

st.markdown('<div class="main-hud">', unsafe_allow_html=True)
st.markdown('<div class="cir-header">CIR OPS STATION</div>', unsafe_allow_html=True)

# Seleção de Alvos
opcao = st.selectbox("WATCHLIST", DATABASE_PLACAS)
target = st.text_input("TARGET", value="" if opcao == "CUSTOM (DIGITAR)" else opcao).upper()

radar_label = "🔴 STOP RADAR" if st.session_state.radar else "🟢 START RADAR"
if st.button(radar_label):
    st.session_state.radar = not st.session_state.radar
    add_log(f"RADAR: {st.session_state.radar}")
st.markdown('</div>', unsafe_allow_html=True)

# Scanner de Câmera (Traseira Prioritária)
st.markdown('<div class="main-hud">', unsafe_allow_html=True)
img = st.camera_input("OPTICAL FEED")
st.markdown('</div>', unsafe_allow_html=True)

# Lógica IA
if st.session_state.radar and img and target:
    try:
        b64 = base64.b64encode(img.getvalue()).decode('utf-8')
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"
        payload = {"contents": [{"parts": [{"text": "Recognize license plate text or return NULL."}, {"inline_data": {"mime_type": "image/jpeg", "data": b64}}]}]}
        res = requests.post(url, json=payload).json()
        det = res['candidates'][0]['content']['parts'][0]['text'].strip().upper()
        if det != "NULL":
            add_log(f"DETETADO: {det}")
            if target in det:
                add_log("🚨 ALVO LOCALIZADO! 🚨")
                st.balloons()
        else:
            add_log("VARREDURA EM CURSO...")
    except:
        add_log("UPLINK ERROR")
    time.sleep(2)
    st.rerun()

# Logs Finais
log_txt = "<br>".join(st.session_state.logs[:2])
st.markdown(f'<div style="background:rgba(0,0,0,0.8); color:#00f2fe; padding:10px; font-size:11px; border-left:3px solid #00f2fe; margin-top:10px;">{log_txt}</div>', unsafe_allow_html=True)

if st.button("TERMINATE OPS"):
    st.session_state.auth = False
    st.rerun()
