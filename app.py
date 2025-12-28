import streamlit as st
import requests
import base64
import time
import folium
from streamlit_folium import folium_static

# --- CONFIGURAÇÃO DE AMBIENTE ELITE ---
st.set_page_config(page_title="CIA OPS STATION", layout="centered", initial_sidebar_state="collapsed")

# Chave API Integrada
GEMINI_API_KEY = "AIzaSyCX1DQKvznD4oVLdXyZZNQuCuFqMkr4ZPw"
DATABASE_PLACAS = ["BRA2E19", "KGT-4590", "ABC7J89", "RIO2K25", "CUSTOM (DIGITAR)"]

st.markdown("""
    <style>
    /* REMOÇÃO TOTAL DE PROPAGANDAS E BANNERS (MÉTODO RADICAL) */
    header, footer, .stDeployButton, [data-testid="stDecoration"], [data-testid="stStatusWidget"] {
        display: none !important;
        visibility: hidden !important;
    }
    
    /* Esconder o botão de 'Manage App' no iPhone */
    button[title="Manage app"], .stAppDeployButton { display: none !important; }
    
    /* Layout para iPhone 15 */
    .stApp { background-color: #000b14; color: #00f2fe; font-family: 'Courier New', monospace; }
    
    .map-container {
        border: 2px solid #00f2fe;
        border-radius: 10px;
        overflow: hidden;
        margin-bottom: 10px;
    }

    .main-panel {
        background: rgba(0, 20, 35, 0.8);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(0, 242, 254, 0.3);
        border-radius: 15px;
        padding: 15px;
    }

    .stButton>button {
        background: rgba(0, 242, 254, 0.1) !important;
        color: #00f2fe !important;
        border: 1px solid #00f2fe !important;
        width: 100%; font-weight: bold;
    }
    </style>
    """, unsafe_allow_html=True)

if 'auth' not in st.session_state: st.session_state.auth = False
if 'logs' not in st.session_state: st.session_state.logs = ["SISTEMA OPERACIONAL"]
if 'radar' not in st.session_state: st.session_state.radar = False

def add_log(msg):
    st.session_state.logs.insert(0, f"» {time.strftime('%H:%M:%S')} | {msg}")

# --- LOGIN ---
if not st.session_state.auth:
    st.markdown("<div style='height: 10vh;'></div>", unsafe_allow_html=True)
    st.markdown("<center><img src='https://upload.wikimedia.org/wikipedia/commons/2/25/Seal_of_the_Central_Intelligence_Agency.svg' width='100'></center>", unsafe_allow_html=True)
    st.markdown("<h3 style='text-align: center; color: #00f2fe; letter-spacing: 5px;'>CIA LOGIN</h3>", unsafe_allow_html=True)
    with st.container():
        st.markdown('<div class="main-panel">', unsafe_allow_html=True)
        pw = st.text_input("PIN", type="password")
        if st.button("LOGIN") or pw == "0000":
            if pw == "0000":
                st.session_state.auth = True
                st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
    st.stop()

# --- DASHBOARD HUD ---
st.markdown("<p style='text-align: center; font-size: 10px; opacity: 0.6;'>MAP_UPLINK: ACTIVE | CAMPOS_RJ</p>", unsafe_allow_html=True)

# Mapa em Tempo Real (Campos, RJ)
m = folium.Map(location=[-21.7545, -41.3245], zoom_start=14, tiles="CartoDB dark_matter", zoom_control=False)
folium.CircleMarker([-21.7545, -41.3245], radius=10, color="#00f2fe", fill=True).add_to(m)

st.markdown('<div class="map-container">', unsafe_allow_html=True)
folium_static(m, width=330, height=200)
st.markdown('</div>', unsafe_allow_html=True)

st.markdown('<div class="main-panel">', unsafe_allow_html=True)
opcao = st.selectbox("WATCHLIST", DATABASE_PLACAS)
target = st.text_input("ID", value="" if opcao == "CUSTOM (DIGITAR)" else opcao).upper()

if st.button("ON/OFF RADAR"):
    st.session_state.radar = not st.session_state.radar
    add_log(f"RADAR {'LIGADO' if st.session_state.radar else 'DESLIGADO'}")
st.markdown('</div>', unsafe_allow_html=True)

# Scanner
img = st.camera_input("")

if st.session_state.radar and img and target:
    b64 = base64.b64encode(img.getvalue()).decode('utf-8')
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"
    payload = {"contents": [{"parts": [{"text": "Return plate or NULL."}, {"inline_data": {"mime_type": "image/jpeg", "data": b64}}]}]}
    
    try:
        res = requests.post(url, json=payload).json()
        det = res['candidates'][0]['content']['parts'][0]['text'].strip().upper()
        if det != "NULL":
            add_log(f"VISTO: {det}")
            if target in det:
                add_log("🚨 ALVO ENCONTRADO 🚨")
                st.balloons()
    except:
        add_log("ERRO DE SINAL")
    time.sleep(2)
    st.rerun()

st.markdown(f'<div style="background:black; color:#00f2fe; padding:10px; font-size:10px; border-left:3px solid #00f2fe;">{"<br>".join(st.session_state.logs[:3])}</div>', unsafe_allow_html=True)
