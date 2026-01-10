import streamlit as st
import requests
import json
import os

# 1. CONFIGURACIÓN
st.set_page_config(page_title="PlanterBot UAGRM", page_icon="🌵")
st.title("🌵 PlanterBot - Centro Interno")

# 2. CARGAR INFO
def cargar_informacion():
    archivo = 'informacion.txt'
    if os.path.exists(archivo):
        with open(archivo, 'r', encoding='utf-8') as f:
            return f.read()
    return "No se encontró información."

conocimiento = cargar_informacion()

# 3. API KEY
if "GEMINI_API_KEY" in st.secrets:
    api_key = st.secrets["GEMINI_API_KEY"]
else:
    api_key = st.sidebar.text_input("API Key", type="password")

# 4. FUNCIÓN "MANUAL" (BYPASS)
def consultar_gemini_manual(pregunta):
    if not api_key:
        return "Falta la API Key."
    
    # URL directa de Google (Usamos 1.5 Flash que es gratis y rápido)
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
    
    headers = {'Content-Type': 'application/json'}
    
    prompt = f"""
    Eres PlanterBot, asistente de la FCHDA - UAGRM.
    Usa SOLO esta información para responder:
    {conocimiento}
    
    Pregunta: {pregunta}
    """
    
    data = {
        "contents": [{"parts": [{"text": prompt}]}]
    }
    
    try:
        # Hacemos la llamada directa
        response = requests.post(url, headers=headers, json=data)
        
        if response.status_code == 200:
            return response.json()['candidates'][0]['content']['parts'][0]['text']
        else:
            return f"Error de Google ({response.status_code}): {response.text}"
            
    except Exception as e:
        return f"Error de conexión: {str(e)}"

# 5. CHAT
if "mensajes" not in st.session_state:
    st.session_state.mensajes = []

for m in st.session_state.mensajes:
    with st.chat_message(m["role"]):
        st.markdown(m["content"])

if pregunta := st.chat_input("Duda sobre trámites..."):
    st.session_state.mensajes.append({"role": "user", "content": pregunta})
    with st.chat_message("user"):
        st.markdown(pregunta)
        
    with st.chat_message("assistant"):
        resp = consultar_gemini_manual(pregunta)
        st.markdown(resp)
        st.session_state.mensajes.append({"role": "assistant", "content": resp})
