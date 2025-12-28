import streamlit as st
import requests
import base64
import time

# --- PROTOCOLO DE INTERFACE ELITE ---
st.set_page_config(page_title="OPS STATION", layout="centered", initial_sidebar_state="collapsed")

# CHAVE API INTEGRADA - NÃO PRECISA MAIS DIGITAR NO SITE
GEMINI_API_KEY = "AIzaSyCX1DQKvznD4oVLdXyZZNQuCuFqMkr4ZPw"

st.markdown("""
    <style>
    .stApp { background-color: #000508; color: #4facfe; font-family: 'Courier New', monospace; }
    .map-bg {
        position: fixed; top: 0; left: 0; width: 100vw; height: 100vh;
        background-image: url('https://upload.wikimedia.org/wikipedia/commons/e/ec/World_map_blank_without_borders.svg');
        background-size: 300%; background-position: center; opacity: 0.15;
        filter: invert(1) hue-rotate(180deg) brightness(0.7);
        animation: pan 180s linear infinite; z-index: -1;
    }
    @keyframes pan { 0% { background-position: 0% 50%; } 100% { background-position: 100% 50%; } }
    .stTextInput>div>div>input {
        background: rgba(0, 20, 40, 0.7) !important; color: #00f2fe !important;
        border: 1px solid rgba(79, 172, 254, 0.4) !important; text-align: center;
    }
    .stButton>button {
        background: rgba(0, 242, 254, 0.1); color: #00f2fe; border: 1px solid #4facfe;
        text-transform: uppercase; font-weight: bold; width: 100%;
    }
    .terminal-box {
        background: rgba(0, 0, 0, 0.8); border-left: 3px solid #4facfe;
        padding: 15px; font-size: 11px; color: #4facfe;
    }
    header {visibility: hidden;}
    footer {visibility: hidden;}
    </style>
    <div class="map-bg"></div>
    """, unsafe_allow_html=True)

if 'auth' not in st.session_state: st.session_state.auth = False
if 'logs' not in st.session_state: st.session_state.logs = ["SISTEMA INICIALIZADO."]
if 'radar' not in st.session_state: st.session_state.radar = False

def add_log(msg):
    st.session_state.logs.insert(0, f"» {time.strftime('%H:%M:%S')} | {msg}")

# --- TELA DE LOGIN ---
if not st.session_state.auth:
    st.markdown("<div style='height: 20vh;'></div>", unsafe_allow_html=True)
    st.markdown("<h2 style='text-align: center; letter-spacing: 12px; color: #4facfe;'>CIA LOGIN</h2>", unsafe_allow_html=True)
    pw = st.text_input("ACCESS CODE", type="password", key="login_pw")
    if pw == "0000":
        st.session_state.auth = True
        add_log("UPLINK ACTIVE | KEY_LOADED_OK")
        st.rerun()
    st.stop()

# --- DASHBOARD ---
with st.sidebar:
    st.markdown("### 🛠️ MISSION CONTROL")
    target = st.text_input("TARGET_ID", placeholder="EX: BRA2E19").upper()
    if st.button("ACTIVATE RADAR"):
        st.session_state.radar = not st.session_state.radar
        add_log("RADAR: " + ("ON" if st.session_state.radar else "OFF"))

img = st.camera_input("")

# Lógica de Disparo Automático com a Chave Integrada
if st.session_state.radar and img and target:
    add_log("SENDING DATA TO GEMINI SAT...")
    b64 = base64.b64encode(img.getvalue()).decode('utf-8')
    
    # URL usa a variável GEMINI_API_KEY definida no topo
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"
    payload = {"contents": [{"parts": [{"text": "Identify license plate. ONLY the text or NULL."}, {"inline_data": {"mime_type": "image/jpeg", "data": b64}}]}]}
    
    try:
        res = requests.post(url, json=payload).json()
        det = res['candidates'][0]['content']['parts'][0]['text'].strip().upper()
        if det != "NULL":
            add_log(f"DETECTED: {det}")
            if target in det:
                add_log("🚨 TARGET MATCH! 🚨")
                st.balloons()
        else:
            add_log("SCANNING CLEAR...")
    except Exception as e:
        add_log(f"API_ERROR: VERIFY UPLINK")
    
    time.sleep(4)
    st.rerun()

st.markdown("<div style='height: 20px;'></div>", unsafe_allow_html=True)
log_text = "<br>".join(st.session_state.logs[:5])
st.markdown(f'<div class="terminal-box">{log_text}</div>', unsafe_allow_html=True)
