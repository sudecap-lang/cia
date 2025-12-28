import streamlit as st
import requests
import base64
import time

# --- PROTOCOLO DE INTERFACE ELITE ---
st.set_page_config(page_title="OPS STATION", layout="centered", initial_sidebar_state="collapsed")

st.markdown("""
    <style>
    /* Reset total para preencher a tela */
    .stApp {
        background-color: #000508;
        color: #4facfe;
        font-family: 'Courier New', monospace;
    }
    
    /* Mapa Mundi Imersivo e Elegante */
    .map-bg {
        position: fixed;
        top: 0; left: 0; width: 100vw; height: 100vh;
        background-image: url('https://upload.wikimedia.org/wikipedia/commons/e/ec/World_map_blank_without_borders.svg');
        background-size: 250%;
        background-position: center;
        opacity: 0.15;
        filter: invert(1) hue-rotate(180deg) brightness(0.6);
        animation: pan 180s linear infinite;
        z-index: -1;
    }
    
    @keyframes pan {
        0% { background-position: 0% 50%; }
        100% { background-position: 100% 50%; }
    }

    /* Estilo Glassmorphism para os Paineis */
    .stTextInput>div>div>input {
        background: rgba(0, 20, 40, 0.6) !important;
        color: #00f2fe !important;
        border: 1px solid rgba(79, 172, 254, 0.3) !important;
        border-radius: 4px !important;
        text-align: center;
        letter-spacing: 2px;
    }
    
    .stButton>button {
        background: rgba(0, 242, 254, 0.05);
        color: #00f2fe;
        border: 1px solid #4facfe;
        border-radius: 2px;
        text-transform: uppercase;
        font-weight: bold;
        letter-spacing: 2px;
        width: 100%;
        transition: 0.5s;
    }
    
    .stButton>button:hover {
        background: rgba(0, 242, 254, 0.2);
        box-shadow: 0 0 15px rgba(0, 242, 254, 0.4);
    }

    /* Terminal de Logs Minimalista */
    .terminal-box {
        background: rgba(0, 0, 0, 0.7);
        border-left: 2px solid #4facfe;
        padding: 15px;
        font-size: 10px;
        color: #4facfe;
        text-transform: uppercase;
    }

    /* Esconder elementos desnecessários do Streamlit */
    header {visibility: hidden;}
    footer {visibility: hidden;}
    </style>
    <div class="map-bg"></div>
    """, unsafe_allow_html=True)

if 'auth' not in st.session_state: st.session_state.auth = False
if 'logs' not in st.session_state: st.session_state.logs = []
if 'radar' not in st.session_state: st.session_state.radar = False

def add_log(msg):
    st.session_state.logs.insert(0, f"» {time.strftime('%H:%M:%S')} | {msg}")

# --- TELA DE ACESSO ---
if not st.session_state.auth:
    st.markdown("<div style='height: 20vh;'></div>", unsafe_allow_html=True)
    st.markdown("<h2 style='text-align: center; letter-spacing: 15px; font-weight: 100; color: #4facfe;'>SECURE LOGIN</h2>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1,3,1])
    with col2:
        pw = st.text_input("CREDENTIALS", type="password")
        if pw == "0000":
            st.session_state.auth = True
            add_log("SYSTEM ONLINE / ENCRYPTION ACTIVE")
            st.rerun()
    st.stop()

# --- DASHBOARD DE OPERAÇÕES ---
st.markdown("<div style='text-align: right; font-size: 8px; opacity: 0.5;'>SECURE_UPLINK: CAMPOS_RJ_SATELLITE</div>", unsafe_allow_html=True)

with st.sidebar:
    st.markdown("### 🛠 SYSTEM")
    api_key = st.text_input("GEMINI_KEY", type="password")
    target = st.text_input("TARGET_ID", placeholder="BRA2E19").upper()
    if st.button("TOGGLE RADAR"):
        st.session_state.radar = not st.session_state.radar
        add_log("RADAR AUTO: " + ("ON" if st.session_state.radar else "OFF"))

# Feed da Câmera (Scanner Óptico)
img = st.camera_input("")

if st.session_state.radar and img and api_key and target:
    b64 = base64.b64encode(img.getvalue()).decode('utf-8')
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
    payload = {"contents": [{"parts": [{"text": "Extract plate or NULL."}, {"inline_data": {"mime_type": "image/jpeg", "data": b64}}]}]}
    
    try:
        res = requests.post(url, json=payload).json()
        det = res['candidates'][0]['content']['parts'][0]['text'].strip().upper()
        if det != "NULL":
            add_log(f"DETECTED: {det}")
            if target in det:
                add_log("!!! TARGET ACQUIRED !!!")
                st.balloons()
        else:
            add_log("SCANNING...")
    except:
        add_log("CONNECTION ERROR")
    
    time.sleep(4)
    st.rerun()

# Espaço e Logs
st.markdown("<div style='height: 20px;'></div>", unsafe_allow_html=True)
log_text = "<br>".join(st.session_state.logs[:5])
st.markdown(f'<div class="terminal-box">{log_text}</div>', unsafe_allow_html=True)
