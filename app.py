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

# 2. CARGAR LA BASE DE CONOCIMIENTO (Tu archivo de texto)
def cargar_informacion():
    archivo = 'informacion.txt'
    if os.path.exists(archivo):
        with open(archivo, 'r', encoding='utf-8') as f:
            return f.read()
    else:
        st.error("⚠️ Error: No se encuentra el archivo 'informacion.txt'. Asegúrate de subirlo a GitHub.")
        return ""

conocimiento = cargar_informacion()

# 3. CONFIGURACIÓN DE LA API KEY (Secreto)
# Esto busca la clave en los "Secretos" de Streamlit o en la barra lateral
if "GEMINI_API_KEY" in st.secrets:
    api_key = st.secrets["GEMINI_API_KEY"]
else:
    # Si lo corres en tu compu local, te pedirá la clave aquí
    with st.sidebar:
        api_key = st.text_input("Ingresa tu Gemini API Key:", type="password")
        st.warning("Si ves esto en la web, falta configurar el 'Secret' en Streamlit.")

# 4. FUNCIÓN PARA HABLAR CON GEMINI
def obtener_respuesta(pregunta):
    if not api_key:
        return "⚠️ Por favor ingresa una API Key válida para continuar."
    
    try:
        genai.configure(api_key=api_key)
        # Usamos el modelo Flash que es rápido y gratuito
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        # Estas son las instrucciones de personalidad del Bot
        prompt_sistema = f"""
        Actúa como 'PlanterBot', el asistente oficial del Centro Interno de la Facultad de Ciencias del Hábitat (UAGRM).
        Tu tono debe ser amable, útil, motivador y universitario. Usa emojis como 🌵, 📚, 🎓.
        
        INSTRUCCIONES CLAVE:
        1. Responde basándote ÚNICAMENTE en el siguiente texto de referencia.
        2. Si la respuesta no está en el texto, di educadamente: "No tengo información oficial sobre ese tema por el momento. Por favor contacta directamente a Andrés Valencia al 73676005."
        3. Sé directo y claro con los requisitos y costos.
        
        TEXTO DE REFERENCIA:
        {conocimiento}
        
        PREGUNTA DEL ESTUDIANTE:
        {pregunta}
        """
        
        response = model.generate_content(prompt_sistema)
        return response.text
    except Exception as e:
        return f"Ocurrió un error al conectar con la IA: {str(e)}"

# 5. INTERFAZ DE CHAT (Historial)
if "mensajes" not in st.session_state:
    st.session_state.mensajes = []

# Mostrar mensajes anteriores
for mensaje in st.session_state.mensajes:
    with st.chat_message(mensaje["role"]):
        st.markdown(mensaje["content"])

# 6. CAPTURAR NUEVA PREGUNTA
if pregunta_usuario := st.chat_input("Escribe tu duda aquí... (Ej: ¿Requisitos para titulación?)"):
    # Mostrar lo que escribió el usuario
    st.session_state.mensajes.append({"role": "user", "content": pregunta_usuario})
    with st.chat_message("user"):
        st.markdown(pregunta_usuario)

    # Generar respuesta del bot
    with st.chat_message("assistant"):
        with st.spinner("Buscando información... 🌵"):
            respuesta = obtener_respuesta(pregunta_usuario)
            st.markdown(respuesta)
            
    # Guardar respuesta en historial
    st.session_state.mensajes.append({"role": "assistant", "content": respuesta})