import streamlit as st
import requests
import base64
import time

# --- CONFIGURAÇÃO CIR AUTO-RADAR ---
st.set_page_config(page_title="CIR OPS STATION", layout="centered", initial_sidebar_state="collapsed")

# Chave API e Banco de Dados
GEMINI_API_KEY = "AIzaSyCX1DQKvznD4oVLdXyZZNQuCuFqMkr4ZPw"
DATABASE_PLACAS = ["POX4G21", "BRA2E19", "KGT-4590", "CUSTOM (DIGITAR)"]

st.markdown("""
    <style>
    /* BLOQUEIO TOTAL DE BANNERS E INTERFACES STREAMLIT */
    header, footer, .stDeployButton, [data-testid="stDecoration"], 
    [data-testid="stStatusWidget"], button[title="Manage app"],
    .viewerBadge_container__1QS13, .stAppDeployButton, .stException {
        display: none !important; visibility: hidden !important;
        opacity: 0 !important; height: 0 !important;
    }

    /* MAPA MUNDI TÁTICO CIR (ESTÁVEL) */
    .stApp {
        background-color: #00080b;
        background-image: url('https://upload.wikimedia.org/wikipedia/commons/e/ec/World_map_blank_without_borders.svg');
        background-size: 250%; background-position: center;
        background-repeat: no-repeat; background-attachment: fixed;
    }
    
    .stApp::before {
        content: ""; position: fixed; top: 0; left: 0; width: 100%; height: 100%;
        background: rgba(0, 5, 10, 0.88); z-index: -1;
    }

    /* HUD ESTILO CIR */
    .main-hud {
        background: rgba(0, 20, 35, 0.75);
        backdrop-filter: blur(12px);
        border: 2px solid #00f2fe;
        border-radius: 15px; padding: 20px; margin-bottom: 10px;
    }

    .cir-title {
        text-align: center; color: #00f2fe; font-size: 22px;
        font-weight: bold; letter-spacing: 3px; text-shadow: 0 0 10px #00f2fe;
    }

    .match-alert {
        background: rgba(255, 255, 0, 0.2);
        border: 2px solid yellow; color: yellow;
        padding: 10px; border-radius: 10px; text-align: center;
        font-weight: bold; animation: blink 1s infinite;
    }
    @keyframes blink { 0% { opacity: 1; } 50% { opacity: 0.3; } 100% { opacity: 1; } }
    </style>
    """, unsafe_allow_html=True)

if 'auth' not in st.session_state: st.session_state.auth = False
if 'radar_active' not in st.session_state: st.session_state.radar_active = False
if 'logs' not in st.session_state: st.session_state.logs = ["SISTEMA CIR ONLINE"]

def add_log(msg):
    st.session_state.logs.insert(0, f"» {time.strftime('%H:%M:%S')} | {msg}")

# --- LOGIN ---
if not st.session_state.auth:
    st.markdown("<div style='height: 15vh;'></div>", unsafe_allow_html=True)
    st.markdown('<div class="cir-title">CIR ACCESS</div>', unsafe_allow_html=True)
    with st.container():
        st.markdown('<div class="main-hud">', unsafe_allow_html=True)
        u = st.text_input("ID OPERADOR")
        p = st.text_input("PASSWORD", type="password")
        if st.button("AUTHENTICATE"):
            if u.upper() == "OPERATOR" and p == "8142":
                st.session_state.auth = True
                st.rerun()
    st.stop()

# --- DASHBOARD DE VARREDURA ---
st.markdown('<div class="main-hud">', unsafe_allow_html=True)
st.markdown('<div class="cir-title">CIR OPS STATION</div>', unsafe_allow_html=True)

opcao = st.selectbox("ALVOS MONITORADOS", DATABASE_PLACAS)
target = st.text_input("TARGET ID", value="" if opcao == "CUSTOM (DIGITAR)" else opcao).upper()

# Controle do Radar
col1, col2 = st.columns(2)
with col1:
    if st.button("🟢 INICIAR RADAR"):
        st.session_state.radar_active = True
        add_log("RADAR ATIVADO")
with col2:
    if st.button("🔴 PARAR RADAR"):
        st.session_state.radar_active = False
        add_log("RADAR DESATIVADO")

status = "📡 SCANNING..." if st.session_state.radar_active else "⏸️ STANDBY"
st.write(f"STATUS: {status}")
st.markdown('</div>', unsafe_allow_html=True)

# Feed de Câmera
st.markdown('<div class="main-hud">', unsafe_allow_html=True)
img = st.camera_input("OPTICAL FEED")
st.markdown('</div>', unsafe_allow_html=True)

# Lógica de Reconhecimento e Repetição
if st.session_state.radar_active and img:
    try:
        b64 = base64.b64encode(img.getvalue()).decode('utf-8')
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"
        payload = {"contents": [{"parts": [{"text": "Extract only the license plate text. If not found, return NULL."}, {"inline_data": {"mime_type": "image/jpeg", "data": b64}}]}]}
        
        res = requests.post(url, json=payload).json()
        det = res['candidates'][0]['content']['parts'][0]['text'].strip().upper()
        
        if det != "NULL" and det != "":
            add_log(f"DETECTADO: {det}")
            if target in det:
                st.markdown('<div class="match-alert">🚨 VEÍCULO LOCALIZADO: ' + det + ' 🚨</div>', unsafe_allow_html=True)
                st.balloons()
                add_log("MATCH CONFIRMADO")
            else:
                st.info(f"PLACA: {det}")
        else:
            add_log("VARREDURA LIMPA")
    except:
        add_log("ERRO DE COMUNICAÇÃO")
    
    # Pausa e recarrega para simular monitoramento contínuo
    time.sleep(2)
    st.rerun()

# Logs do Sistema
log_display = "<br>".join(st.session_state.logs[:2])
st.markdown(f'<div style="background:rgba(0,0,0,0.8); color:#00f2fe; padding:10px; font-size:11px; border-left:3px solid #00f2fe; margin-top:5px;">{log_display}</div>', unsafe_allow_html=True)
