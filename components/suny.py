from google import genai
import streamlit as st
import time

system_prompt="""
    Your name is Suny. You're the assistant for the Software de la Unidad de Información Estadística y Documental.
    1. Database en MS Access and program runing on localhost.
    2. Modulos: Inicio, Buscar, Nueva Queja, Nueva Recomendación, Nueva No Recomendación, Modificar Estatus, Reportes.
    Responde de forma clara y concisa, enfocándote en la información que el usuario necesita.
    a. En Buscar puede hacer busquedas individuales por expediente, quejoso, autoridad o por palabra clave en toda la db.
    b. Para editar una queja puede ir a Buscar, buscar el expediente, y ahí le saldrá la opción de editar. Solo se puede editar en esa sección.
    c. En Modificar Estatus puede cambiar el estatus de un expediente y su clasificacion de interseccionalidad, pero no editar el resto de información.
    d. En Reportes puede generar tablas de los registros:
        - una tabla general con filtros en estatus, fehcas, municipio y autoridad
        - una grafica de estatus de expedientes
        - generar el reporte semanal de la numeralia
        - una busqueda con querys diseñadas por el programador en la db de SIPRODHEG, que es la base de datos general del PRODHEG con información de todas las áreas, no solo de quejas.
        - un reporte de predicciones de recomendaciones usando un modelo de ML entrenado con los datos históricos.
    """

def chat_asistente():
    st.write("### Hola, soy Suny")
    client = genai.Client(api_key=st.secrets["API_KEY"])
    #model = genai.GenerativeModel(
    #    model_name='gemini-2.5-flash',
    #    system_instruction=system_prompt
    #)

    if "messages" not in st.session_state:
        st.session_state.messages = []

    chat_placeholder = st.container(height=300)

    # Mostrar historial
    with chat_placeholder:
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

    # Entrada de texto ÚNICA
    # Al estar dentro del popover, usa una key específica
    if prompt := st.chat_input("¿En qué puedo ayudarte?", key="chat_suny_input"):
        # 1. Guardar y mostrar mensaje del usuario
        st.session_state.messages.append({"role": "user", "content": prompt})
        with chat_placeholder:
            with st.chat_message("user"):
                st.markdown(prompt)

        # 2. Generar respuesta
        with chat_placeholder:
            with st.chat_message("assistant"):
                message_placeholder = st.empty()
                try:
                    with st.spinner("Pensando..."):
                        seccion = st.session_state.get('opcion_actual')
                        full_prompt = f"[El usuario está en la sección: {seccion}] {prompt}"
                        response = client.models.generate_content_stream(
                            model="gemini-2.5-flash",
                            contents=full_prompt,
                            config={
                                "system_instruction": system_prompt,
                                "temperature": 0.7
                            }
                        )
                        full_response = ""

                        # Mostrar respuesta en tiempo real
                        for chunk in response:
                            # En la nueva librería, el texto suele estar en chunk.text
                            if chunk.text:
                                full_response += chunk.text
                                message_placeholder.markdown(full_response + "▌")
                                time.sleep(0.01)
                        
                        # 3. Guardar respuesta en historial
                        message_placeholder.markdown(full_response) # Respuesta final sin cursor
                        st.session_state.messages.append({"role": "assistant", "content": full_response})
                except Exception as e:
                    if "429" in str(e):
                        st.error("⚠️ Suny está un poco saturada. Por favor, espera un minuto antes de volver a preguntar.")
                    else:
                        st.error(f"¡Ups! Tuve un pequeño problema técnico: {e}")