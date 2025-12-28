import streamlit as st
import requests
import base64
import time

# --- PROTOCOLO DE INTERFACE ELITE ---
st.set_page_config(page_title="OPS STATION", layout="centered", initial_sidebar_state="collapsed")

# Chave API integrada para ativação imediata
GEMINI_API_KEY = "AIzaSyCX1DQKvznD4oVLdXyZZNQuCuFqMkr4ZPw"

st.markdown("""
    <style>
    /* Estilização para preenchimento total da tela do iPhone 15 */
    .stApp { background-color: #000508; color: #4facfe; font-family: 'Courier New', monospace; }
    
    .map-bg {
        position: fixed; top: 0; left: 0; width: 100vw; height: 100vh;
        background-image: url('https://upload.wikimedia.org/wikipedia/commons/e/ec/World_map_blank_without_borders.svg');
        background-size: 300%; background-position: center; opacity: 0.15;
        filter: invert(1) hue-rotate(180deg) brightness(0.7);
        animation: pan 180s linear infinite; z-index: -1;
    }
    
    @keyframes pan { 0% { background-position: 0% 50%; } 100% { background-position: 100% 50%; } }

    /* Glassmorphism UI */
    .stTextInput>div>div>input {
        background: rgba(0, 20, 40, 0.7) !important; color: #00f2fe !important;
        border: 1px solid rgba(79, 172, 254, 0.4) !important; text-align: center; font-size: 18px;
    }
    
    .stButton>button {
        background: rgba(0, 242, 254, 0.1); color: #00f2fe; border: 1px solid #4facfe;
        text-transform: uppercase; font-weight: bold; letter-spacing: 3px; width: 100%;
    }

    .terminal-box {
        background: rgba(0, 0, 0, 0.8); border-left: 3px solid #4facfe;
        padding: 15px; font-size: 11px; color: #4facfe; line-height: 1.5;
    }

    header {visibility: hidden;}
    footer {visibility: hidden;}
    </style>
    <div class="map-bg"></div>
    """, unsafe_allow_html=True)

if 'auth' not in st.session_state: st.session_state.auth = False
if 'logs' not in st.session_state: st.session_state.logs = ["SISTEMA AGUARDANDO AUTENTICAÇÃO..."]
if 'radar' not in st.session_state: st.session_state.radar = False

def add_log(msg):
    st.session_state.logs.insert(0, f"» {time.strftime('%H:%M:%S')} | {msg}")

# --- TELA DE ACESSO ---
if not st.session_state.auth:
    st.markdown("<div style='height: 15vh;'></div>", unsafe_allow_html=True)
    st.markdown("<div style='text-align: center;'><img src='https://upload.wikimedia.org/wikipedia/commons/2/25/Seal_of_the_Central_Intelligence_Agency.svg' width='100' style='opacity: 0.5;'></div>", unsafe_allow_html=True)
    st.markdown("<h2 style='text-align: center; letter-spacing: 12px; color: #4facfe; margin-top: 20px;'>CIA LOGIN</h2>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1,4,1])
    with col2:
        pw = st.text_input("ACCESS CODE", type="password")
        if pw == "0000":
            st.session_state.auth = True
            add_log("UPLINK ESTABLISHED / CAMPOS_RJ")
            st.rerun()
    st.stop()

# --- DASHBOARD OPERACIONAL ---
st.markdown("<div style='text-align: right; font-size: 9px; opacity: 0.6; letter-spacing: 1px;'>GLOBAL_SCAN_ACTIVE | SATELLITE_UPLINK</div>", unsafe_allow_html=True)

with st.sidebar:
    st.markdown("### 🛠️ MISSION CONTROL")
    target = st.text_input("TARGET_ID", placeholder="EX: BRA2E19").upper()
    if st.button("ACTIVATE AUTO-RADAR"):
        st.session_state.radar = not st.session_state.radar
        add_log("RADAR AUTO: " + ("ENABLED" if st.session_state.radar else "DISABLED"))
    st.divider()
    if st.button("TERMINATE SESSION"):
        st.session_state.auth = False
        st.rerun()

# Scanner Óptico (Câmera do iPhone 15)
img = st.camera_input("")

if st.session_state.radar and img and target:
    add_log("SCANNING FRAME...")
    b64 = base64.b64encode(img.getvalue()).decode('utf-8')
    
    # Conexão direta via Gemini Pro Vision
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"
    payload = {"contents": [{"parts": [{"text": "Extract car plate. Return ONLY plate or NULL."}, {"inline_data": {"mime_type": "image/jpeg", "data": b64}}]}]}
    
    try:
        res = requests.post(url, json=payload).json()
        det = res['candidates'][0]['content']['parts'][0]['text'].strip().upper()
        if det != "NULL":
            add_log(f"DETECTION CONFIRMED: {det}")
            if target in det:
                add_log("🚨 TARGET MATCH IDENTIFIED 🚨")
                st.balloons()
                st.error(f"TARGET ACQUIRED: {det}")
        else:
            add_log("NO VISUAL TARGET")
    except:
        add_log("UPLINK ERROR: CHECK SATELLITE")
    
    # Loop de Automação
    time.sleep(4)
    st.rerun()

# Terminal de Logs Estilo Agência
st.markdown("<div style='height: 20px;'></div>", unsafe_allow_html=True)
log_text = "<br>".join(st.session_state.logs[:5])
st.markdown(f'<div class="terminal-box">{log_text}</div>', unsafe_allow_html=True)
