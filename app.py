import streamlit as st
import requests
import os
import time

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(
    page_title="PlanterBot - FCHDA",
    page_icon="🌵",
    layout="centered",
    initial_sidebar_state="expanded"
)

# Estilos CSS (Personalizados)
st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    h1 {color: #2E7D32; text-align: center;}
    .stButton button {
        width: 100%;
        border-radius: 10px;
        border: 1px solid #4CAF50;
        color: #4CAF50;
        background-color: transparent;
    }
    .stButton button:hover {
        background-color: #4CAF50;
        color: white;
        border: 1px solid #4CAF50;
    }
    </style>
""", unsafe_allow_html=True)

# --- CARGAR BASE DE DATOS ---
def cargar_informacion():
    if os.path.exists('informacion.txt'):
        with open('informacion.txt', 'r', encoding='utf-8') as f: return f.read()
    elif os.path.exists('Informacion.txt'):
        with open('Informacion.txt', 'r', encoding='utf-8') as f: return f.read()
    return "No se encontró la información."

conocimiento = cargar_informacion()

# --- API KEY ---
if "GEMINI_API_KEY" in st.secrets:
    api_key = st.secrets["GEMINI_API_KEY"]
else:
    api_key = st.sidebar.text_input("Ingresa tu API Key:", type="password")

# --- LÓGICA INTELIGENTE (Bypass) ---
def obtener_modelo_valido(api_key):
    url = f"https://generativelanguage.googleapis.com/v1beta/models?key={api_key}"
    try:
        resp = requests.get(url)
        if resp.status_code == 200:
            data = resp.json()
            candidatos = [m['name'] for m in data.get('models', []) if 'generateContent' in m.get('supportedGenerationMethods', [])]
            for c in candidatos:
                if 'gemini-1.5-flash' in c: return c
            if candidatos: return candidatos[0]
    except:
        pass
    return "models/gemini-pro"

def consultar_ia(pregunta):
    if not api_key: return "⚠️ Necesito una API Key para funcionar."
    
    modelo = obtener_modelo_valido(api_key)
    url = f"https://generativelanguage.googleapis.com/v1beta/{modelo}:generateContent?key={api_key}"
    headers = {'Content-Type': 'application/json'}
    
    prompt = f"""
    Eres PlanterBot, el asistente virtual del Centro Interno de la Facultad (FCHDA - UAGRM).
    Tu personalidad es amable, motivadora y eficiente.
    
    Reglas:
    1. Usa SOLO la siguiente información oficial.
    2. Si no sabes la respuesta, di: "No tengo ese dato oficial. Contacta al Centro Interno."
    3. Sé breve y usa listas.
    4. Usa emojis verdes (🌵, 🍃, ✅).

    INFORMACIÓN OFICIAL:
    {conocimiento}
    
    PREGUNTA: {pregunta}
    """
    
    data = {"contents": [{"parts": [{"text": prompt}]}]}
    
    try:
        response = requests.post(url, headers=headers, json=data)
        if response.status_code == 200:
            return response.json()['candidates'][0]['content']['parts'][0]['text']
        else:
            return "Tuve un pequeño error de conexión. Intenta de nuevo."
    except Exception as e:
        return f"Error: {str(e)}"

# --- INTERFAZ GRÁFICA ---

# 1. HEADER
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    # AQUI CAMBIAMOS A .PNG
    if os.path.exists("logo.png"):
        st.image("logo.png", use_container_width=True)
    else:
        st.header("🌵 PlanterBot")

st.markdown("<h3 style='text-align: center; color: gray;'>Tu guía en la Facultad de Ciencias del Hábitat</h3>", unsafe_allow_html=True)
st.divider()

# 2. BARRA LATERAL
with st.sidebar:
    # AQUI CAMBIAMOS A .PNG
    if os.path.exists("logo.png"):
        st.image("logo.png", width=100)
    else:
        st.write("🌵")
        
    st.write("### 🛠️ Herramientas")
    if st.button("🗑️ Borrar Conversación"):
        st.session_state.mensajes = []
        st.rerun()
    st.write("---")
    st.write("### 📞 Contacto Oficial")
    st.info("**Celular/WhatsApp:**\n73676005 (Andrés Valencia)\n\n📍 **Ubicación:**\nCentro Interno - FCHDA")

# 3. CHAT
if "mensajes" not in st.session_state:
    st.session_state.mensajes = []

# Avatar del bot (.PNG)
avatar_bot = "logo.png" if os.path.exists("logo.png") else "🌵"

for m in st.session_state.mensajes:
    with st.chat_message(m["role"], avatar=avatar_bot if m["role"] == "assistant" else None):
        st.markdown(m["content"])

# 4. SUGERENCIAS RÁPIDAS (Si está vacío)
if len(st.session_state.mensajes) == 0:
    st.write("Selecciona una opción rápida:")
    cols = st.columns(2)
    with cols[0]:
        if st.button("🎓 Requisitos Titulación"):
            st.session_state.mensajes.append({"role": "user", "content": "Requisitos para titulación"})
            st.rerun()
        if st.button("📅 Calendario 2026"):
            st.session_state.mensajes.append({"role": "user", "content": "Calendario académico 2026"})
            st.rerun()
    with cols[1]:
        if st.button("💰 Becas"):
            st.session_state.mensajes.append({"role": "user", "content": "Qué becas hay disponibles?"})
            st.rerun()
        if st.button("📋 Trámites"):
            st.session_state.mensajes.append({"role": "user", "content": "Lista de trámites disponibles"})
            st.rerun()

# 5. INPUT
if prompt := st.chat_input("Escribe tu duda aquí..."):
    st.session_state.mensajes.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    
    with st.chat_message("assistant", avatar=avatar_bot):
        with st.spinner("Consultando... 🍃"):
            resp = consultar_ia(prompt)
            st.markdown(resp)
    
    st.session_state.mensajes.append({"role": "assistant", "content": resp})
