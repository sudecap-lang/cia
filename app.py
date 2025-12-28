import streamlit as st
import requests
import base64
import time

# --- CONFIGURAÇÃO DE AMBIENTE CIR ---
st.set_page_config(page_title="CIR OPS", layout="centered", initial_sidebar_state="collapsed")

# Chave API Integrada
GEMINI_API_KEY = "AIzaSyCX1DQKvznD4oVLdXyZZNQuCuFqMkr4ZPw"
DATABASE_PLACAS = ["BRA2E19", "KGT-4590", "ABC7J89", "RIO2K25", "CUSTOM (DIGITAR)"]

st.markdown("""
    <style>
    /* BLOQUEIO DE ELEMENTOS NATIVOS */
    header, footer, .stDeployButton, [data-testid="stDecoration"], 
    [data-testid="stStatusWidget"], button[title="Manage app"],
    .viewerBadge_container__1QS13, .stAppDeployButton, .stException {
        display: none !important; visibility: hidden !important;
        opacity: 0 !important; height: 0 !important;
    }
    
    /* MAPA MUNDI - FIXAÇÃO FORÇADA */
    .stApp { background-color: #000408; color: #00f2fe; font-family: 'Courier New', monospace; }
    
    .map-background {
        position: fixed; top: 0; left: 0; width: 100%; height: 100%;
        background-image: url('https://upload.wikimedia.org/wikipedia/commons/e/ec/World_map_blank_without_borders.svg');
        background-size: 300%; background-position: center; opacity: 0.25 !important;
        filter: invert(1) sepia(1) saturate(5) hue-rotate(180deg) brightness(0.4);
        animation: pan 180s linear infinite; z-index: -999;
        pointer-events: none;
    }
    @keyframes pan { 0% { background-position: 0% 50%; } 100% { background-position: 100% 50%; } }

    /* ESTILO CIR HUD */
    .hud-box {
        background: rgba(0, 15, 25, 0.85);
        backdrop-filter: blur(15px);
        border: 1px solid #00f2fe;
        border-radius: 12px; padding: 15px; margin-bottom: 10px;
    }

    .cir-badge {
        width: 60px; height: 60px; border: 2px solid #00f2fe;
        border-radius: 50%; display: flex; align-items: center;
        justify-content: center; margin: 0 auto 10px auto;
        font-weight: bold; box-shadow: 0 0 10px #00f2fe;
    }

    .stButton>button {
        background: rgba(0, 242, 254, 0.1) !important;
        color: #00f2fe !important; border: 1px solid #00f2fe !important;
        width: 100%; font-weight: bold;
    }
    </style>
    <div class="map-background"></div>
    """, unsafe_allow_html=True)

if 'auth' not in st.session_state: st.session_state.auth = False
if 'logs' not in st.session_state: st.session_state.logs = ["CIR SYSTEM: ONLINE"]
if 'radar' not in st.session_state: st.session_state.radar = False

def add_log(msg):
    st.session_state.logs.insert(0, f"» {time.strftime('%H:%M:%S')} | {msg}")

# --- TELA DE ACESSO ---
if not st.session_state.auth:
    st.markdown("<div style='height: 12vh;'></div>", unsafe_allow_html=True)
    st.markdown('<div class="cir-badge">CIR</div>', unsafe_allow_html=True)
    st.markdown("<h4 style='text-align: center;'>CENTRO DE INTELIGÊNCIA</h4>", unsafe_allow_html=True)
    with st.container():
        st.markdown('<div class="hud-box">', unsafe_allow_html=True)
        user = st.text_input("ID OPERADOR", placeholder="EX: OPERATOR")
        pw = st.text_input("PASSWORD", type="password")
        if st.button("AUTHENTICATE"):
            if user.upper() == "OPERATOR" and pw == "8142":
                st.session_state.auth = True
                add_log("OPERADOR AUTORIZADO")
                st.rerun()
            else:
                st.error("ACESSO NEGADO")
        st.markdown('</div>', unsafe_allow_html=True)
    st.stop()

# --- DASHBOARD DE RECONHECIMENTO ---
st.markdown("<p style='text-align: center; font-size: 10px; opacity: 0.8;'>UPLINK CAMPOS_RJ | SENSOR ATIVO</p>", unsafe_allow_html=True)

# Controles
st.markdown('<div class="hud-box">', unsafe_allow_html=True)
opcao = st.selectbox("BANCO DE DADOS PLACAS", DATABASE_PLACAS)
target = st.text_input("ALVO", value="" if opcao == "CUSTOM (DIGITAR)" else opcao).upper()

radar_label = "🔴 DESATIVAR" if st.session_state.radar else "🟢 ATIVAR RADAR"
if st.button(radar_label):
    st.session_state.radar = not st.session_state.radar
    add_log(f"RADAR: {st.session_state.radar}")
st.markdown('</div>', unsafe_allow_html=True)

# Câmera (Tentativa de Traseira por Padrão via Streamlit)
st.markdown('<div class="hud-box">', unsafe_allow_html=True)
img = st.camera_input("CAPTURE FEED", help="O sistema solicitará a câmera traseira.")
st.markdown('</div>', unsafe_allow_html=True)

# Lógica IA
if st.session_state.radar and img and target:
    try:
        b64 = base64.b64encode(img.getvalue()).decode('utf-8')
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"
        payload = {"contents": [{"parts": [{"text": "Recognize plate or NULL."}, {"inline_data": {"mime_type": "image/jpeg", "data": b64}}]}]}
        res = requests.post(url, json=payload).json()
        det = res['candidates'][0]['content']['parts'][0]['text'].strip().upper()
        if det != "NULL":
            add_log(f"DETETADO: {det}")
            if target in det:
                add_log("🚨 ALVO LOCALIZADO! 🚨")
                st.balloons()
        else:
            add_log("SCANNING...")
    except:
        add_log("ERRO DE LINK")
    time.sleep(2)
    st.rerun()

# Logs e Encerramento
log_txt = "<br>".join(st.session_state.logs[:2])
st.markdown(f'<div style="background:rgba(0,0,0,0.8); color:#00f2fe; padding:8px; font-size:10px; border-left:3px solid #00f2fe;">{log_txt}</div>', unsafe_allow_html=True)

if st.button("TERMINAR SESSÃO"):
    st.session_state.auth = False
    st.rerun()
