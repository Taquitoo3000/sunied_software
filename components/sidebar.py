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
        st.badge(f"**{st.session_state.usuario}**",
                 icon=':material/account_circle:',
                 color='violet')
        contenedor_filtros = st.container()
        st.header("Menú")

        opciones_sg = [
            "🏠 Inicio",
            "🔍 Buscar",
            "➕ Nueva Queja",
            "➕ Nueva Recomendación",
            "➕ Nueva No Recomendación",
            "🔄 Modificar Estatus",
            "📄 Reportes",
            "📊 DashBoard"
        ]
        opciones_sub = [
            "🏠 Inicio",
            "🔍 Buscar",
            "➕ Nueva Queja",
            "📄 Reportes",
            "📊 DashBoard"
        ]

        # Lista de opciones según el rol del usuario
        if st.session_state.usuario == 'Secretaría General':
            opciones_menu = opciones_sg
        else: 
            opciones_menu = opciones_sub
 
        # Mapa de "ir_a" -> opción del menú (en texto, no en índice)
        ir_a_map = {
            "buscar": "🔍 Buscar",
            "nueva": "➕ Nueva Queja",
            "editar": "➕ Nueva Queja",
            "nueva_R": "➕ Nueva Recomendación",
            "nueva_NR": "➕ Nueva No Recomendación",
            "estatus": "🔄 Modificar Estatus",
            "todas": "📄 Reportes",
            "dashboard": "📊 DashBoard",
        }
 
        # Si hay una navegación programática pendiente, forzamos el valor
        # del widget ANTES de crearlo, pero solo si esa opción existe en
        # el menú del rol actual (evita ValueError con opciones_sub,
        # que no tiene Recomendación/No Recomendación/Estatus).
        ir_a_actual = st.session_state.get('ir_a')
        destino = ir_a_map.get(ir_a_actual)
        if destino in opciones_menu:
            st.session_state['menu_radio'] = destino
        # Siempre limpiamos ir_a, aunque el destino no exista en este
        # menú, para que no se quede "pegado" y vuelva a interferir
        # con la navegación manual del usuario más adelante.
        if ir_a_actual is not None:
            st.session_state.ir_a = ""
 
        opcion = st.radio(
            "Menú:",
            opciones_menu,
            key="menu_radio",
            label_visibility="collapsed"
        )

        st.divider()
        st.caption(f"Actualizado: {datetime.now().strftime('%d/%m/%Y %H:%M')}")
        
        return opcion, contenedor_filtros