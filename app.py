import streamlit as st
import google.generativeai as genai

st.title("🛠️ Diagnóstico de PlanterBot")

# Chequeo de API Key
if "GEMINI_API_KEY" in st.secrets:
    api_key = st.secrets["GEMINI_API_KEY"]
    st.success("✅ API Key detectada en Secrets.")
    
    try:
        genai.configure(api_key=api_key)
        st.write("📡 Consultando a Google qué modelos tienes disponibles...")
        
        # Listar modelos
        modelos = genai.list_models()
        encontrado = False
        
        for m in modelos:
            if 'gemini' in m.name:
                st.info(f"Modelo disponible: {m.name}")
                encontrado = True
        
        if not encontrado:
            st.error("❌ Google responde, pero no ve ningún modelo Gemini. Tu API Key podría ser de un proyecto antiguo o sin permisos.")
            
    except Exception as e:
        st.error(f"❌ Error de conexión: {e}")
        st.write("Posible causa: La librería 'google-generativeai' está desactualizada. Revisa requirements.txt")

else:
    st.error("⚠️ No se encontró la GEMINI_API_KEY en los Secrets.")
