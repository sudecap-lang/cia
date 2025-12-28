import streamlit as st
import requests
import base64
import time

# --- PROTOCOLO VISUAL CIA ---
st.set_page_config(page_title="CIA OPS STATION", layout="centered", initial_sidebar_state="collapsed")

st.markdown("""
    <style>
    .stApp { background-color: #020507; color: #1a3a5a; font-family: 'Courier New', monospace; }
    .map-background {
        position: fixed; top: 0; left: 0; width: 100%; height: 100%; opacity: 0.1;
        background-image: url('https://upload.wikimedia.org/wikipedia/commons/e/ec/World_map_blank_without_borders.svg');
        background-size: cover; filter: invert(1) sepia(1) saturate(5) hue-rotate(190deg);
        animation: rotateMap 120s linear infinite; z-index: -1;
    }
    @keyframes rotateMap { from { background-position: 0% 50%; } to { background-position: 100% 50%; } }
    .stTextInput>div>div>input { background-color: #000 !important; color: #4a90e2 !important; border: 1px solid #1a3a5a !important; text-align: center; font-size: 20px; }
    .stButton>button { background-color: #0a1a2a; color: #4a90e2; border: 1px solid #1a3a5a; width: 100%; font-weight: bold; height: 3em; }
    .log-box { background-color: rgba(0,0,0,0.8); border: 1px solid #1a3a5a; padding: 10px; font-size: 11px; color: #1e40af; height: 150px; overflow: hidden; }
    </style>
    <div class="map-background"></div>
    """, unsafe_allow_html=True)

if 'auth' not in st.session_state: st.session_state.auth = False
if 'logs' not in st.session_state: st.session_state.logs = ["SISTEMA INICIALIZADO. AGUARDANDO LOGIN..."]

def add_log(msg):
    st.session_state.logs.insert(0, f"[{time.strftime('%H:%M:%S')}] > {msg}")

# --- TELA DE LOGIN (BASEADA NA SUA PRIMEIRA IMAGEM) ---
if not st.session_state.auth:
    st.markdown("<div style='text-align: center; margin-top: 50px;'><img src='https://upload.wikimedia.org/wikipedia/commons/2/25/Seal_of_the_Central_Intelligence_Agency.svg' width='150'></div>", unsafe_allow_html=True)
    st.markdown("<h1 style='text-align: center; color: #fff; letter-spacing: 5px; font-size: 24px; margin-bottom: 30px;'>CIA LOGIN</h1>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1,3,1])
    with col2:
        agent_id = st.text_input("AGENT ID", placeholder="IDENTIFICAÇÃO")
        password = st.text_input("PASSWORD", type="password", placeholder="SENHA")
        if st.button("ACCESS SYSTEM"):
            if password == "0000":
                st.session_state.auth = True
                add_log(f"AGENTE {agent_id} CONECTADO.")
                st.rerun()
            else:
                st.error("ACESSO NEGADO: CREDENCIAIS INVÁLIDAS")
    st.stop()

# --- INTERFACE TÁTICA PÓS-LOGIN ---
st.markdown("### 🛰️ GLOBAL SURVEILLANCE UPLINK")

with st.sidebar:
    st.title("🛡️ SECURITY CONFIG")
    # AQUI VOCÊ COLA A CHAVE QUE APARECE NA SUA IMAGEM
    api_key = st.text_input("COLE SUA API KEY (AIza...)", type="password")
    target_plate = st.text_input("PLACA ALVO", placeholder="EX: BRA2E19").upper()
    st.divider()
    if st.button("TERMINATE SESSION"):
        st.session_state.auth = False
        st.rerun()

# Scanner de Câmera
cam_input = st.camera_input("OPTICAL SCANNER")

if cam_input and api_key and target_plate:
    add_log("CAPTURA REALIZADA. ENVIANDO PARA ANÁLISE...")
    b64_img = base64.b64encode(cam_input.getvalue()).decode('utf-8')
    
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
    payload = {
        "contents": [{"parts": [
            {"text": "Identify the license plate in this image. Return ONLY the plate text or 'NULL' if not found."},
            {"inline_data": {"mime_type": "image/jpeg", "data": b64_img}}
        ]}]
    }
    
    try:
        res = requests.post(url, json=payload).json()
        detected = res['candidates'][0]['content']['parts'][0]['text'].strip().upper()
        
        if detected != "NULL":
            add_log(f"DETECÇÃO: {detected}")
            if target_plate in detected:
                add_log("🚨 ALVO LOCALIZADO! EMITINDO ALERTA...")
                st.error(f"CONFIRMADO: ALVO {detected} IDENTIFICADO!")
                st.balloons()
            else:
                add_log("PLACA IDENTIFICADA, MAS NÃO CONFERE COM O ALVO.")
        else:
            add_log("NENHUMA PLACA IDENTIFICADA NO FRAME.")
    except:
        add_log("ERRO DE COMUNICAÇÃO COM O SATÉLITE. VERIFIQUE A API KEY.")

# LOGS ESTILO TERMINAL
st.markdown("---")
st.markdown("##### 📜 OPERATIONAL CHRONICLE")
log_html = f"<div class='log-box'>{'<br>'.join(st.session_state.logs[:6])}</div>"
st.markdown(log_html, unsafe_allow_html=True)
