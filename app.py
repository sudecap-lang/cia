import streamlit as st
import requests
import base64
import time
from PIL import Image
import io

# --- CONFIGURAÇÃO VISUAL TÁTICA ---
st.set_page_config(page_title="CIA AUTOMATED RADAR", layout="centered")

st.markdown("""
    <style>
    .stApp { background-color: #020507; color: #1a3a5a; font-family: 'Courier New', monospace; }
    .map-background {
        position: fixed; top: 0; left: 0; width: 100%; height: 100%; opacity: 0.08;
        background-image: url('https://upload.wikimedia.org/wikipedia/commons/e/ec/World_map_blank_without_borders.svg');
        background-size: cover; filter: invert(1) sepia(1) saturate(5) hue-rotate(190deg);
        animation: rotateMap 120s linear infinite; z-index: -1;
    }
    @keyframes rotateMap { from { background-position: 0% 50%; } to { background-position: 100% 50%; } }
    .log-box { background-color: rgba(0,0,0,0.9); border: 1px solid #1a3a5a; padding: 10px; font-size: 11px; color: #1e40af; height: 180px; overflow-y: auto; }
    .radar-active { color: #ff0000; font-weight: bold; animation: blinker 1.5s linear infinite; }
    @keyframes blinker { 50% { opacity: 0; } }
    </style>
    <div class="map-background"></div>
    """, unsafe_allow_html=True)

if 'auth' not in st.session_state: st.session_state.auth = False
if 'logs' not in st.session_state: st.session_state.logs = []
if 'run_radar' not in st.session_state: st.session_state.run_radar = False

def add_log(msg):
    ts = time.strftime("%H:%M:%S")
    st.session_state.logs.insert(0, f"[{ts}] > {msg}")

# --- LOGIN ---
if not st.session_state.auth:
    st.markdown("<h1 style='text-align: center; color: #1a3a5a;'>CIA ACCESS</h1>", unsafe_allow_html=True)
    pin = st.text_input("PASSWORD", type="password")
    if pin == "0000":
        st.session_state.auth = True
        st.rerun()
    st.stop()

# --- INTERFACE ---
st.markdown("### 🛰️ AUTO-RADAR UPLINK: CAMPOS_RJ")

with st.sidebar:
    st.title("⚙️ RADAR_CONFIG")
    api_key = st.text_input("GEMINI_API_KEY", type="password")
    target_id = st.text_input("TARGET_PLATE", placeholder="BRA2E19").upper()
    intervalo = st.slider("INTERVALO DE SCAN (SEG)", 3, 10, 5)
    
    if st.button("INICIAR RADAR AUTOMÁTICO"):
        st.session_state.run_radar = True
        add_log("RADAR AUTOMÁTICO ATIVADO.")
    
    if st.button("PARAR RADAR"):
        st.session_state.run_radar = False
        add_log("RADAR DESATIVADO.")

# Componente de Câmera
img_captured = st.camera_input("OPTICAL_FEED")

# LÓGICA DE AUTOMAÇÃO
if st.session_state.run_radar and img_captured and api_key and target_id:
    st.markdown("<p class='radar-active'>● RADAR EM OPERAÇÃO - MONITORANDO VEÍCULOS...</p>", unsafe_allow_html=True)
    
    # Processamento Gemini
    bytes_data = img_captured.getvalue()
    b64_img = base64.b64encode(bytes_data).decode('utf-8')
    
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
    payload = {
        "contents": [{"parts": [
            {"text": "Detect license plate. Return ONLY plate or 'NULL'."},
            {"inline_data": {"mime_type": "image/jpeg", "data": b64_img}}
        ]}]
    }
    
    try:
        res = requests.post(url, json=payload).json()
        detected = res['candidates'][0]['content']['parts'][0]['text'].strip().upper()
        
        if detected != "NULL":
            add_log(f"DETECTADO AUTOMATICAMENTE: {detected}")
            if target_id in detected:
                add_log("🚨 ALVO IDENTIFICADO! ENVIANDO ALERTA!")
                st.error(f"MATCH: {detected}")
                st.balloons()
                # Aqui pode entrar o código do Telegram
        else:
            add_log("SCAN: PISTA LIMPA")
    except:
        add_log("ERRO DE COMUNICAÇÃO")

    # Força o refresh automático para a próxima "foto"
    time.sleep(intervalo)
    st.rerun()

# TERMINAL
st.markdown("---")
log_content = "<br>".join(st.session_state.logs[:8])
st.markdown(f'<div class="log-box">{log_content}</div>', unsafe_allow_html=True)
