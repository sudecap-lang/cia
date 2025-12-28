import streamlit as st
import requests
import base64
import time

# --- CONFIGURAÇÃO DA INTERFACE DE AGÊNCIA ---
st.set_page_config(page_title="CIA OPS STATION", layout="centered")

# CSS para forçar o visual de agência e o mapa giratório de fundo
st.markdown("""
    <style>
    .stApp {
        background-color: #020507;
        color: #1a3a5a;
        font-family: 'Courier New', monospace;
    }
    /* Mapa Mundi Giratório de Fundo */
    .map-background {
        position: fixed;
        top: 0; left: 0; width: 100%; height: 100%;
        opacity: 0.08;
        background-image: url('https://upload.wikimedia.org/wikipedia/commons/e/ec/World_map_blank_without_borders.svg');
        background-size: cover;
        filter: invert(1) sepia(1) saturate(5) hue-rotate(190deg);
        animation: rotateMap 120s linear infinite;
        z-index: -1;
    }
    @keyframes rotateMap {
        from { background-position: 0% 50%; }
        to { background-position: 100% 50%; }
    }
    /* Inputs e Botões */
    .stTextInput>div>div>input {
        background-color: #000 !important;
        color: #4a90e2 !important;
        border: 1px solid #1a3a5a !important;
        text-align: center;
        letter-spacing: 5px;
    }
    .stButton>button {
        background-color: #0a1a2a;
        color: #4a90e2;
        border: 1px solid #1a3a5a;
        width: 100%;
        border-radius: 0;
        font-weight: bold;
    }
    .log-box {
        background-color: rgba(0,0,0,0.8);
        border: 1px solid #1a3a5a;
        padding: 10px;
        font-size: 11px;
        color: #1e40af;
        height: 150px;
        overflow: hidden;
    }
    </style>
    <div class="map-background"></div>
    """, unsafe_allow_html=True)

# --- SISTEMA DE ESTADO ---
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
if 'logs' not in st.session_state:
    st.session_state.logs = []

def add_log(msg):
    ts = time.strftime("%H:%M:%S")
    st.session_state.logs.insert(0, f"[{ts}] > {msg}")

# --- TELA DE LOGIN ---
if not st.session_state.authenticated:
    st.markdown("<h1 style='text-align: center; color: #1a3a5a; letter-spacing: 10px; font-size: 20px;'>CLASSIFIED ACCESS</h1>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        pin = st.text_input("ENTER AGENT PIN", type="password")
        if pin == "0000":
            st.session_state.authenticated = True
            add_log("SESSION_START: GPS_SYNC_OK")
            st.rerun()
    st.stop()

# --- PAINEL DE CONTROLE ---
st.markdown("### 🛰️ SATELLITE_UPLINK: CAMPOS_RJ")

with st.sidebar:
    st.header("⚙️ SYSTEM_KEYS")
    gemini_key = st.text_input("GEMINI_API_KEY", type="password")
    target_id = st.text_input("TARGET_PLATE", placeholder="ABC1234").upper()
    st.divider()
    if st.button("LOGOUT"):
        st.session_state.authenticated = False
        st.rerun()

# CÂMERA (Funciona nativamente no iPhone 15)
img_captured = st.camera_input("OPTICAL_SCANNER")

if img_captured and gemini_key and target_id:
    add_log("ANALYZING_OPTICAL_FEED...")
    
    # Converter para Base64
    bytes_data = img_captured.getvalue()
    b64_img = base64.b64encode(bytes_data).decode('utf-8')
    
    # Chamada Gemini
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={gemini_key}"
    payload = {
        "contents": [{"parts": [
            {"text": "Identify license plate. Return ONLY the text or 'NULL'."},
            {"inline_data": {"mime_type": "image/jpeg", "data": b64_img}}
        ]}]
    }
    
    try:
        res = requests.post(url, json=payload).json()
        detected = res['candidates'][0]['content']['parts'][0]['text'].strip().upper()
        
        if detected != "NULL":
            add_log(f"ID_CONFIRMED: {detected}")
            if target_id in detected:
                add_log("!!! TARGET_ACQUIRED !!!")
                st.warning(f"MATCH FOUND: {detected}")
        else:
            add_log("SCANNING: NO_TARGET")
    except:
        add_log("UPLINK_ERROR: CHECK_API_KEY")

# TERMINAL DE LOGS
st.markdown("---")
log_content = "<br>".join(st.session_state.logs[:6])
st.markdown(f'<div class="log-box">{log_content}</div>', unsafe_allow_html=True)
