# main.py
import streamlit as st
from database import get_connection, cargar_catalogos, get_connection_mysql, get_connection_access
from components.sidebar import render_sidebar
from functions import home, buscar, nueva_queja, ver_todos, status, nueva_NR
import subprocess
import time

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
    if 'ir_a' not in st.session_state:
        st.session_state.ir_a = ""
    if 'expediente_editar' not in st.session_state:
        st.session_state.expediente_editar = ""
    if 'buscar_clicked' not in st.session_state:
        st.session_state.buscar_clicked = False
    if 'sidebar_rendered' not in st.session_state:
        st.session_state.sidebar_rendered = False

# Función principal
def main():
    load_css()
    init_session_state()
    
    # Conexión a BD
    #conn = get_connection()
    #conn = get_connection_mysql()
    conn = get_connection_access()
    if not conn:
        st.error("No se pudo conectar a la base de datos")
        st.stop()
    
    # Cargar catálogos
    catalogos = cargar_catalogos(conn)
    
    # Renderizar sidebar
    opcion_seleccionada = render_sidebar()
    
    # Renderizar contenido según opción

    # Guardar la opción en session_state
    st.session_state.opcion_actual = opcion_seleccionada
    
    # Enrutamiento de páginas
    if opcion_seleccionada == "🏠 Inicio":
        home.render()
    elif opcion_seleccionada == "🔍 Buscar Expediente":
        buscar.render(conn, catalogos)
    elif opcion_seleccionada == "➕ Nueva Queja":
        nueva_queja.render(conn, catalogos)
    elif opcion_seleccionada == "➕ Nueva Recomendación":
        st.markdown("En construcción...")
    elif opcion_seleccionada == "➕ Nueva No Recomendación":
        nueva_NR.render(conn, catalogos)
    elif opcion_seleccionada == "🔄 Editar Expediente":
        st.markdown("En construcción...")
    elif opcion_seleccionada == "🔄 Modificar Estatus":
        status.render(conn, catalogos)
    elif opcion_seleccionada == "📊 Ver Todos":
        ver_todos.render(conn, catalogos)
    
    # Footer
    render_footer()

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