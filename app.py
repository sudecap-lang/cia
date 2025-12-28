import streamlit as st
import requests
import base64
import time

# --- CONFIGURAÇÃO DE AMBIENTE CIR ---
st.set_page_config(page_title="CIR OPS STATION", layout="centered", initial_sidebar_state="collapsed")

# Chave API Integrada
GEMINI_API_KEY = "AIzaSyCX1DQKvznD4oVLdXyZZNQuCuFqMkr4ZPw"
DATABASE_PLACAS = ["BRA2E19", "KGT-4590", "ABC7J89", "RIO2K25", "CUSTOM (DIGITAR)"]

st.markdown("""
    <style>
    /* BLOQUEIO TOTAL DE BANNERS E ERROS VISÍVEIS */
    header, footer, .stDeployButton, [data-testid="stDecoration"], 
    [data-testid="stStatusWidget"], button[title="Manage app"],
    .viewerBadge_container__1QS13, .stAppDeployButton, .stException {
        display: none !important; visibility: hidden !important;
        opacity: 0 !important; height: 0 !important;
    }
    
    /* FUNDO TÁTICO E MAPA MUNDI DINÂMICO CIR */
    .stApp { background-color: #000508; color: #00f2fe; font-family: 'Courier New', monospace; }
    
    .map-bg {
        position: fixed; top: 0; left: 0; width: 100vw; height: 100vh;
        background-image: url('https://upload.wikimedia.org/wikipedia/commons/e/ec/World_map_blank_without_borders.svg');
        background-size: 350%; background-position: center; opacity: 0.15;
        filter: invert(1) sepia(1) saturate(5) hue-rotate(170deg) brightness(0.5);
        animation: pan 180s linear infinite; z-index: -1;
        pointer-events: none;
    }
    @keyframes pan { 0% { background-position: 0% 50%; } 100% { background-position: 100% 50%; } }

    /* ESTILO DOS PAINÉIS HUD */
    .hud-panel {
        background: rgba(0, 15, 25, 0.85);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(0, 242, 254, 0.4);
        border-radius: 15px; padding: 15px; margin-bottom: 10px;
    }

    .cir-logo {
        width: 70px; height: 70px; border: 2px solid #00f2fe;
        border-radius: 50%; display: flex; align-items: center;
        justify-content: center; margin: 0 auto 10px auto;
        font-size: 20px; font-weight: bold; box-shadow: 0 0 15px #00f2fe;
    }

    .stButton>button {
        background: rgba(0, 242, 254, 0.1) !important;
        color: #00f2fe !important; border: 1px solid #00f2fe !important;
        width: 100%; border-radius: 8px; font-weight: bold;
    }

    /* TERMINAL DE LOGS */
    .terminal-output {
        background: rgba(0, 0, 0, 0.9); border-left: 3px solid #00f2fe;
        padding: 8px; font-size: 10px; color: #00f2fe; margin-top: 10px;
    }
    </style>
    <div class="map-bg"></div>
    """, unsafe_allow_html=True)

# Inicialização de Estado Segura
if 'auth' not in st.session_state: st.session_state.auth = False
if 'logs' not in st.session_state: st.session_state.logs = ["ESTABELECENDO LINK..."]
if 'radar' not in st.session_state: st.session_state.radar = False

def add_log(msg):
    st.session_state.logs.insert(0, f"» {time.strftime('%H:%M:%S')} | {msg}")

# --- TELA DE LOGIN CIR ---
if not st.session_state.auth:
    st.markdown("<div style='height: 15vh;'></div>", unsafe_allow_html=True)
    st.markdown('<div class="cir-logo">CIR</div>', unsafe_allow_html=True)
    st.markdown("<h3 style='text-align: center; letter-spacing: 5px;'>SECURE ACCESS</h3>", unsafe_allow_html=True)
    with st.container():
        st.markdown('<div class="hud-panel">', unsafe_allow_html=True)
        u = st.text_input("OPERATOR ID")
        p = st.text_input("PASSWORD", type="password")
        if st.button("LOGIN"):
            if u.upper() == "OPERATOR" and p == "8142":
                st.session_state.auth = True
                add_log("ACESSO AUTORIZADO")
                st.rerun()
            else:
                st.error("ACESSO NEGADO")
        st.markdown('</div>', unsafe_allow_html=True)
    st.stop()

# --- DASHBOARD OPERACIONAL ---
st.markdown("<p style='text-align: center; font-size: 9px; opacity: 0.7;'>CIR_UPLINK_STABLE | LOCAL: CAMPOS_RJ</p>", unsafe_allow_html=True)

# Controles de Alvo
st.markdown('<div class="hud-panel">', unsafe_allow_html=True)
opcao = st.selectbox("ALVOS MONITORADOS", DATABASE_PLACAS)
target = st.text_input("PLACA ALVO", value="" if opcao == "CUSTOM (DIGITAR)" else opcao).upper()

btn_text = "🔴 PARAR RADAR" if st.session_state.radar else "🟢 INICIAR RADAR"
if st.button(btn_text):
    st.session_state.radar = not st.session_state.radar
    add_log(f"RADAR: {'ATIVO' if st.session_state.radar else 'OFF'}")
st.markdown('</div>', unsafe_allow_html=True)

# Scanner de Câmera
st.markdown('<div class="hud-panel">', unsafe_allow_html=True)
img = st.camera_input("SCANNER ÓPTICO")
st.markdown('</div>', unsafe_allow_html=True)

# Processamento Gemini
if st.session_state.radar and img and target:
    try:
        b64 = base64.b64encode(img.getvalue()).decode('utf-8')
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"
        payload = {"contents": [{"parts": [{"text": "Identify plate or NULL."}, {"inline_data": {"mime_type": "image/jpeg", "data": b64}}]}]}
        res = requests.post(url, json=payload).json()
        det = res['candidates'][0]['content']['parts'][0]['text'].strip().upper()
        if det != "NULL":
            add_log(f"DETETADO: {det}")
            if target in det:
                add_log("🚨 ALVO IDENTIFICADO! 🚨")
                st.balloons()
        else:
            add_log("VARREDURA LIMPA")
    except:
        add_log("ERRO DE CONEXÃO")
    time.sleep(2)
    st.rerun()

# Terminal de Logs Seguro
log_display = "<br>".join(st.session_state.logs[:3])
st.markdown(f'<div class="terminal-output">{log_display}</div>', unsafe_allow_html=True)

if st.button("ENCERRAR OPERAÇÃO"):
    st.session_state.auth = False
    st.rerun()
