# main.py
import uuid
import streamlit as st
from components import suny
from database import cargar_catalogos, get_connection_mysql, log_event
from components.sidebar import render_sidebar
from functions import home, buscar, reports, status, nueva_NR, editar, nueva_R, dashboard
from streamlit_float import float_init, float_parent
from datetime import datetime
from streamlit.runtime.scriptrunner import get_script_run_ctx

# Configuración de página
st.set_page_config(
    page_title="SUNIED",
    page_icon="img/loguito.png",
    layout="wide",
    menu_items={}
)

# CSS personalizado
def load_css():
    with open("style.css", "r", encoding="utf-8") as f:
        css = f.read()
        st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)

# Inicializar estado de sesión
def init_session_state():
    if 'session_id' not in st.session_state:
        st.session_state.session_id = str(uuid.uuid4())
        st.session_state.start_time = datetime.now()

    if 'last_page' not in st.session_state:
        st.session_state.last_page = None
    if 'ir_a' not in st.session_state:
        st.session_state.ir_a = ""
    if 'expediente_editar' not in st.session_state:
        st.session_state.expediente_editar = ""
    if 'buscar_clicked' not in st.session_state:
        st.session_state.buscar_clicked = False
    if 'sidebar_rendered' not in st.session_state:
        st.session_state.sidebar_rendered = False

def get_client_ip():
    try:
        ctx = get_script_run_ctx()
        if ctx and hasattr(ctx, "request") and ctx.request:
            return ctx.request.remote_ip
    except:
        pass
    return "unknown"

# Función principal
def main():
    float_init()
    load_css()
    init_session_state()
    
    # Conexión a BD
    conn = get_connection_mysql()
    if not conn:
        st.error("No se pudo conectar a la base de datos")
        st.stop()

    #ip = get_client_ip()
    usuario_email = st.user.get("email") if st.user else None
    usuario_email = usuario_email or "unknown"

    # Registrar inicio de sesión (solo una vez)
    if "logged" not in st.session_state:
        log_event(
            conn,
            st.session_state.session_id,
            usuario_email,
            "NEW_SESSION",
            None
        )
        st.session_state.logged = True
    
    catalogos = cargar_catalogos(conn)
    opcion_seleccionada = render_sidebar()
    if st.session_state.last_page != opcion_seleccionada:
        log_event(
            conn,
            st.session_state.session_id,
            usuario_email,
            "NAVIGATION",
            opcion_seleccionada.encode('ascii','ignore').decode()
        )
        st.session_state.last_page = opcion_seleccionada

    # Guardar la opción en session_state
    st.session_state.opcion_actual = opcion_seleccionada
    
    # Enrutamiento de páginas
    if opcion_seleccionada == "🏠 Inicio":
        home.render()
    elif opcion_seleccionada == "🔍 Buscar":
        buscar.render(conn, catalogos)
    elif opcion_seleccionada == "➕ Nueva Queja":
        if st.session_state.get('modo_edicion') and st.session_state.get('expediente_editar'):
            editar.render(conn, catalogos, modo_edicion=True, expediente_editar=st.session_state.expediente_editar)
        else:
            editar.render(conn, catalogos, modo_edicion=False)
    elif opcion_seleccionada == "➕ Nueva Recomendación":
        nueva_R.render(conn, catalogos)
    elif opcion_seleccionada == "➕ Nueva No Recomendación":
        nueva_NR.render(conn, catalogos)
    elif opcion_seleccionada == "🔄 Modificar Estatus":
        status.render(conn, catalogos)
    elif opcion_seleccionada == "📊 Reportes":
        reports.render(conn, catalogos)
    elif opcion_seleccionada == "📊 DashBoard":
        dashboard.render(conn)
    
    # Footer
    render_footer()

    with st.container():
        with st.popover("💬 Asistente Suny",type='primary'):
            suny.chat_asistente()
        float_parent(css="position:fixed; bottom: 1rem; left: 70rem; z-index: 1000;")

def render_footer():
    st.markdown("""
    <hr>
    <div style="text-align: center; color: grey; font-size: 0.9em;">
        © 2026 Unidad de Información Estadística y Documental - PRODHEG |
        Desarrollado por <a href="https://taquitoo3000.github.io/isael/" style="color: mediumorchid;">SECtech</a>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()