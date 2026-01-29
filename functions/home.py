# pages/home.py
import streamlit as st

def render():
    """Renderiza la página de inicio"""
    st.title("SUNIED v1.0 Beta")
    st.subheader("Software de la Unidad de Información Estadística y Documental - PRODHEG")
    st.markdown("---")
    st.header("Bienvenido")
    st.markdown("""
    Este sistema permite la gestión de expedientes de quejas de la 
    **Unidad de Información Estadística y Documental - PRODHEG**.

    ### Funcionalidades disponibles:
    - 🔍 **Buscar Expedientes**: Consulta completa por número de expediente
    - ➕ **Nuevos Registros**: Registra nuevos registros en el sistema como quejas, resoluciones
    - 🔄 **Modifica Estatus**: Cambia el estatus de cualquier expediente y su fecha que entra en vigor
    - 📊 **Ver Todos**: Visualiza todos los registros con filtros
    """)

    # Botones de acción
    '''
    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("🔍 Buscar Expediente", 
                    use_container_width=True, 
                    type="primary",
                    key="btn_buscar_home"):
            st.session_state.ir_a = "buscar"
            st.rerun()

    with col2:
        if st.button("➕ Nueva Queja", 
                    use_container_width=True, 
                    type="primary",
                    key="btn_nueva_home"):
            st.session_state.ir_a = "nueva"
            st.rerun()

    with col3:
        if st.button("📊 Ver Todos", 
                    use_container_width=True, 
                    type="primary",
                    key="btn_todas_home"):
            st.session_state.ir_a = "todas"
            st.rerun()
'''
    st.session_state.buscar_clicked = False