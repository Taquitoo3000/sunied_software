# components/sidebar.py
import streamlit as st
import base64
from datetime import datetime

def render_sidebar():
    with st.sidebar:
        # Logo
        with open("img/logo_horizontal.png", "rb") as img_file:
            b64_logo = base64.b64encode(img_file.read()).decode()
        st.markdown(
            f"""
            <a href="https://unied-prodheg.vercel.app/" target="_self">
                <img src="data:image/png;base64,{b64_logo}" width=300 style="cursor:pointer;">
            </a>
            """,
            unsafe_allow_html=True
        )
        
        st.header("Menú")
        
        # Determinar opción seleccionada
        opciones_menu = [
            "🏠 Inicio",
            "🔍 Buscar",
            "➕ Nueva Queja",
            "➕ Nueva Recomendación",
            "➕ Nueva No Recomendación",
            "🔄 Modificar Estatus",
            "📊 Reportes"]
        if st.session_state.get('ir_a') == "buscar":
            opcion_seleccionada = 1
        elif st.session_state.get('ir_a') == "nueva":
            opcion_seleccionada = 2
        elif st.session_state.get('ir_a') == "editar":
            opcion_seleccionada = 2
        elif st.session_state.get('ir_a') == "nueva_R":
            opcion_seleccionada = 3
        elif st.session_state.get('ir_a') == "nueva_NR":
            opcion_seleccionada = 4
        elif st.session_state.get('ir_a') == "estatus":
            opcion_seleccionada = 5
        elif st.session_state.get('ir_a') == "todas":
            opcion_seleccionada = 6
        else:
            opcion_seleccionada = 0
            
        opcion = st.radio(
            "Menú:",
            opciones_menu,
            index=opcion_seleccionada,
            label_visibility="collapsed"
        )

        st.divider()
        st.caption(f"Actualizado: {datetime.now().strftime('%d/%m/%Y %H:%M')}")
        
        return opcion