# pages/home.py
import streamlit as st

def render():
    if not st.session_state.autenticado:
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
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
            st.subheader("Software de la Unidad de Información Estadística y Documental - PRODHEG",text_alignment='center')
            st.markdown("---")
            user = st.selectbox(
                "**Usuario:**",
                options= [
                    'Secretaría General',
                    'Subprocuraduría A',
                    'Subprocuraduría B',
                    'Subprocuraduría C',
                    'Subprocuraduría D',
                    'Subprocuraduría E',
                ],
                index=None,
                key='sel_miembro'
            )
            if user == 'Secretaría General':
                sg_pass=st.text_input("Contraseña", type="password")
            if st.button("Ingresar", width='stretch',disabled=(user is None), type='primary'):
                if user == 'Secretaría General':
                    if sg_pass == st.secrets['SG_PASS']:
                        st.session_state.autenticado = True
                        st.session_state.usuario = user
                        st.rerun()
                    else:
                        st.error("Contraseña incorrecta")
                elif user:
                    st.session_state.autenticado = True
                    st.session_state.usuario = user
                    st.rerun()
        st.stop()  # Esto evita que se cargue el resto de la app
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
    st.subheader("Software de la Unidad de Información Estadística y Documental - PRODHEG",text_alignment='center')
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