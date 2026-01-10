import streamlit as st
import google.generativeai as genai
import os

# 1. CONFIGURACIÓN DE LA PÁGINA
st.set_page_config(
    page_title="PlanterBot UAGRM",
    page_icon="🌵",
    layout="centered"
)

st.title("🌵 PlanterBot - Centro Interno")
st.write("Bienvenido. Soy tu asistente virtual para trámites y dudas de la Facultad.")

# 2. CARGAR LA BASE DE CONOCIMIENTO
def cargar_informacion():
    # Intentamos leer informacion.txt (minúscula)
    archivo = 'informacion.txt'
    if os.path.exists(archivo):
        with open(archivo, 'r', encoding='utf-8') as f:
            return f.read()
    else:
        st.error("⚠️ Error: No se encuentra el archivo 'informacion.txt'.")
        return ""

conocimiento = cargar_informacion()

# 3. CONFIGURACIÓN DE LA API KEY
if "GEMINI_API_KEY" in st.secrets:
    api_key = st.secrets["GEMINI_API_KEY"]
else:
    with st.sidebar:
        api_key = st.text_input("Ingresa tu Gemini API Key:", type="password")

# 4. FUNCIÓN PARA HABLAR CON GEMINI
def obtener_respuesta(pregunta):
    if not api_key:
        return "⚠️ Por favor ingresa una API Key válida."
    
    try:
        genai.configure(api_key=api_key)
        
        # AQUÍ ESTÁ EL CAMBIO: Usamos el modelo que apareció en tu lista diagnóstica
        model = genai.GenerativeModel('gemini-2.0-flash')
        
        prompt_sistema = f"""
        Actúa como 'PlanterBot', el asistente oficial del Centro Interno de la Facultad de Ciencias del Hábitat (UAGRM).
        Tu tono debe ser amable, útil, motivador y universitario. Usa emojis como 🌵, 📚, 🎓.
        
        INSTRUCCIONES:
        1. Responde basándote ÚNICAMENTE en el siguiente texto de referencia.
        2. Si la respuesta no está en el texto, di: "No tengo información oficial sobre ese tema por el momento. Contacta a Andrés Valencia al 73676005."
        3. Sé breve y directo.
        
        TEXTO DE REFERENCIA:
        {conocimiento}
        
        PREGUNTA DEL ESTUDIANTE:
        {pregunta}
        """
        
        response = model.generate_content(prompt_sistema)
        return response.text
    except Exception as e:
        return f"Ocurrió un error técnico: {str(e)}"

# 5. INTERFAZ DE CHAT
if "mensajes" not in st.session_state:
    st.session_state.mensajes = []

for mensaje in st.session_state.mensajes:
    with st.chat_message(mensaje["role"]):
        st.markdown(mensaje["content"])

if pregunta_usuario := st.chat_input("Escribe tu duda aquí..."):
    st.session_state.mensajes.append({"role": "user", "content": pregunta_usuario})
    with st.chat_message("user"):
        st.markdown(pregunta_usuario)

    with st.chat_message("assistant"):
        with st.spinner("PlanterBot está pensando... 🌵"):
            respuesta = obtener_respuesta(pregunta_usuario)
            st.markdown(respuesta)
            
    st.session_state.mensajes.append({"role": "assistant", "content": respuesta})
