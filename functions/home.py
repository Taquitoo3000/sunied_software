# pages/home.py
import streamlit as st

def render():
    st.markdown("""
        <div style="
            background: #8055AB;
            padding: 0px;
            border-radius: 12px;
            margin-bottom: 0px;
            text-align: center;
        ">
            <h1 style="color: white; margin: 0;">SUNIED Lite v1.0</h1>
        </div>
    """, unsafe_allow_html=True)
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
    - 📄 **Reportes**: Visualiza los registros y filtra campos
    - 📊 **Dashboards**: Muestra estadísticas y visualizaciones de los datos de forma clara
    """)
    st.session_state.buscar_clicked = False