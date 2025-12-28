import streamlit as st
import requests
import base64
import time

# --- CONFIGURAÇÃO CIR REAL-TIME ---
st.set_page_config(page_title="CIR - REAL TIME SCAN", layout="centered", initial_sidebar_state="collapsed")

# Chave API e Banco de Dados (Alvos)
GEMINI_API_KEY = "AIzaSyCX1DQKvznD4oVLdXyZZNQuCuFqMkr4ZPw"
DATABASE_PLACAS = ["POX4G21", "BRA2E19", "KGT-4590", "CUSTOM (DIGITAR)"]

st.markdown("""
    <style>
    /* ELIMINAÇÃO DE INTERFERÊNCIAS E BANNERS */
    header, footer, .stDeployButton, [data-testid="stDecoration"], 
    [data-testid="stStatusWidget"], button[title="Manage app"],
    .viewerBadge_container__1QS13, .stAppDeployButton {
        display: none !important; visibility: hidden !important;
        opacity: 0 !important; height: 0 !important;
    }

    /* FUNDO MAPA MUNDI DINÂMICO CIR */
    .stApp {
        background-color: #00080b;
        background-image: url('https://upload.wikimedia.org/wikipedia/commons/e/ec/World_map_blank_without_borders.svg');
        background-size: 250%; background-position: center;
        background-repeat: no-repeat; background-attachment: fixed;
    }
    
    .stApp::before {
        content: ""; position: fixed; top: 0; left: 0; width: 100%; height: 100%;
        background: rgba(0, 5, 10, 0.85); z-index: -1;
    }

    /* HUD CENTRALIZADO */
    .main-hud {
        background: rgba(0, 25, 40, 0.7);
        backdrop-filter: blur(10px);
        border: 2px solid #00f2fe;
        border-radius: 15px; padding: 20px;
        box-shadow: 0 0 25px rgba(0, 242, 254, 0.3);
    }

    .cir-header {
        text-align: center; color: #00f2fe; font-size: 24px;
        font-weight: bold; letter-spacing: 5px; text-shadow: 0 0 10px #00f2fe;
        margin-bottom: 15px;
    }

    /* ALERTA DE MATCH POSITIVO */
    .match-found {
        background: rgba(255, 0, 0, 0.2);
        border: 2px solid #ff4b4b; color: #ff4b4b;
        padding: 15px; border-radius: 10px; text-align: center;
        font-weight: bold; font-size: 18px; margin: 10px 0;
        animation: pulse 1s infinite;
    }
    @keyframes pulse { 0% { opacity: 1; } 50% { opacity: 0.5; } 100% { opacity: 1; } }

    /* ESTILO DE BOTÕES */
    .stButton>button {
        background: #00f2fe !important; color: #000 !important;
        font-weight: bold; border-radius: 5px; width: 100%; height: 50px;
    }
    </style>
    """, unsafe_allow_html=True)

if 'auth' not in st.session_state: st.session_state.auth = False
if 'radar_active' not in st.session_state: st.session_state.radar_active = False
if 'logs' not in st.session_state: st.session_state.logs = ["CIR SYSTEM READY"]

def add_log(msg):
    st.session_state.logs.insert(0, f"» {time.strftime('%H:%M:%S')} | {msg}")

# --- TELA DE ACESSO ---
if not st.session_state.auth:
    st.markdown("<div style='height: 15vh;'></div>", unsafe_allow_html=True)
    st.markdown('<div class="cir-header">CIR ACCESS</div>', unsafe_allow_html=True)
    with st.container():
        st.markdown('<div class="main-hud">', unsafe_allow_html=True)
        u = st.text_input("ID OPERADOR")
        p = st.text_input("PASSWORD", type="password")
        if st.button("AUTHENTICATE"):
            if u.upper() == "OPERATOR" and p == "8142":
                st.session_state.auth = True
                st.rerun()
    st.stop()

# --- INTERFACE DE MONITORAMENTO ---
st.markdown("<p style='text-align: center; color: #00f2fe; font-size: 10px; letter-spacing: 2px;'>CIR_UPLINK_STABLE | SENSOR: REAR_CAM</p>", unsafe_allow_html=True)

st.markdown('<div class="main-hud">', unsafe_allow_html=True)
st.markdown('<div class="cir-header">CIR OPS STATION</div>', unsafe_allow_html=True)

opcao = st.selectbox("LISTA DE ALVOS", DATABASE_PLACAS)
target = st.text_input("ID ALVO", value="" if opcao == "CUSTOM (DIGITAR)" else opcao).upper()

if not st.session_state.radar_active:
    if st.button("🟢 INICIAR MONITORAMENTO"):
        st.session_state.radar_active = True
        st.rerun()
else:
    if st.button("🔴 DESATIVAR SISTEMA"):
        st.session_state.radar_active = False
        st.rerun()

st.markdown('</div>', unsafe_allow_html=True)

# Feed de Câmera em Tempo Real
if st.session_state.radar_active:
    st.markdown('<div class="main-hud">', unsafe_allow_html=True)
    img = st.camera_input("POSICIONE O VEÍCULO NO ENQUADRAMENTO")
    st.markdown('</div>', unsafe_allow_html=True)

    if img:
        try:
            b64 = base64.b64encode(img.getvalue()).decode('utf-8')
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"
            payload = {"contents": [{"parts": [{"text": "Recognize only the license plate. If target " + target + " is found, confirm it. Return NULL if no plate."}, {"inline_data": {"mime_type": "image/jpeg", "data": b64}}]}]}
            
            res = requests.post(url, json=payload).json()
            det = res['candidates'][0]['content']['parts'][0]['text'].strip().upper()
            
            if det != "NULL" and det != "":
                add_log(f"PLACA: {det}")
                if target in det:
                    st.markdown('<div class="match-found">🚨 VEÍCULO IDENTIFICADO: ' + det + ' 🚨</div>', unsafe_allow_html=True)
                    st.balloons()
                    add_log("MATCH CONFIRMADO!")
                else:
                    st.info(f"VEÍCULO LIDO: {det}")
            else:
                add_log("VARREDURA EM CURSO...")
        except:
            add_log("ERRO DE COMUNICAÇÃO")
        
        # Recarrega automaticamente para manter o fluxo
        time.sleep(1)
        st.rerun()

# Terminal de Logs
log_display = "<br>".join(st.session_state.logs[:2])
st.markdown(f'<div style="background:rgba(0,0,0,0.8); color:#00f2fe; padding:10px; font-size:11px; border-left:3px solid #00f2fe; margin-top:10px;">{log_display}</div>', unsafe_allow_html=True)
