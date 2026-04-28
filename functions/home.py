# pages/home.py
import streamlit as st

def render():
    """Renderiza la página de inicio"""
    st.title("SUNIED v4.0")
    st.subheader("Software de la Unidad de Información Estadística y Documental - PRODHEG")
    st.markdown("---")
    st.header("Bienvenido")
    st.markdown("""
    Este sistema permite la gestión de expedientes de quejas de la 
    **Unidad de Información Estadística y Documental - PRODHEG**.

    ### Funcionalidades disponibles:
    - 🔍 **Buscar**: Consultas puntuales como expediente, personas, autoridades, etc.
    - ➕ **Nuevos Registros**: Registra nuevos registros en el sistema como quejas, resoluciones
    - 🔄 **Modifica Estatus**: Cambia el estatus de cualquier expediente y su fecha que entra en vigor
    - 📊 **Reportes**: Visualiza los registros y genera reportes estadísticos
    """)
    st.session_state.buscar_clicked = False