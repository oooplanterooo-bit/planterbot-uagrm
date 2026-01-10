import streamlit as st
import requests
import json
import os

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="PlanterBot UAGRM", page_icon="🌵")
st.title("🌵 PlanterBot - Centro Interno")

# --- CARGAR INFORMACIÓN ---
def cargar_informacion():
    # Intentamos leer el archivo (probamos minúscula y Mayúscula por si acaso)
    if os.path.exists('informacion.txt'):
        with open('informacion.txt', 'r', encoding='utf-8') as f: return f.read()
    elif os.path.exists('Informacion.txt'):
        with open('Informacion.txt', 'r', encoding='utf-8') as f: return f.read()
    return "No se encontró la base de datos."

conocimiento = cargar_informacion()

# --- API KEY ---
if "GEMINI_API_KEY" in st.secrets:
    api_key = st.secrets["GEMINI_API_KEY"]
else:
    api_key = st.sidebar.text_input("Tu API Key", type="password")

# --- FUNCIÓN INTELIGENTE (Auto-Select) ---
def obtener_modelo_valido(api_key):
    """Pregunta a Google qué modelos tienes y elige el mejor disponible."""
    url_lista = f"https://generativelanguage.googleapis.com/v1beta/models?key={api_key}"
    try:
        resp = requests.get(url_lista)
        if resp.status_code == 200:
            modelos = resp.json().get('models', [])
            # Buscamos modelos que sirvan para generar texto (generateContent)
            # Priorizamos versiones "pro" o "flash" estables
            candidatos = []
            for m in modelos:
                if 'generateContent' in m.get('supportedGenerationMethods', []):
                    candidatos.append(m['name']) # Guarda ej: models/gemini-pro
            
            # Si encontramos alguno, devolvemos el primero
            if candidatos:
                # Preferencia: si está gemini-1.5-flash lo usamos, si no, el que sea
                for c in candidatos:
                    if 'gemini-1.5-flash' in c: return c
                return candidatos[0] # El primero que sirva
    except:
        pass
    return "models/gemini-pro" # Fallback por defecto

# --- FUNCIÓN DE RESPUESTA ---
def consultar_gemini_smart(pregunta):
    if not api_key: return "Falta la API Key."
    
    # 1. Detectamos el modelo automáticamente
    nombre_modelo = obtener_modelo_valido(api_key)
    
    # 2. Construimos la URL con el modelo exacto que Google nos dio
    url = f"https://generativelanguage.googleapis.com/v1beta/{nombre_modelo}:generateContent?key={api_key}"
    headers = {'Content-Type': 'application/json'}
    
    prompt = f"""
    Eres PlanterBot, asistente de la Facultad. 
    Responde usando SOLO esta información:
    {conocimiento}
    
    Pregunta: {pregunta}
    """
    
    data = {"contents": [{"parts": [{"text": prompt}]}]}
    
    try:
        response = requests.post(url, headers=headers, json=data)
        if response.status_code == 200:
            return response.json()['candidates'][0]['content']['parts'][0]['text']
        else:
            return f"⚠️ Error ({response.status_code}) usando el modelo '{nombre_modelo}': {response.text}"
    except Exception as e:
        return f"Error de conexión: {str(e)}"

# --- CHAT ---
if "mensajes" not in st.session_state: st.session_state.mensajes = []

for m in st.session_state.mensajes:
    with st.chat_message(m["role"]): st.markdown(m["content"])

if preg := st.chat_input("Escribe tu duda..."):
    st.session_state.mensajes.append({"role": "user", "content": preg})
    with st.chat_message("user"): st.markdown(preg)
    
    with st.chat_message("assistant"):
        with st.spinner("Buscando..."):
            resp = consultar_gemini_smart(preg)
            st.markdown(resp)
            st.session_state.mensajes.append({"role": "assistant", "content": resp})
