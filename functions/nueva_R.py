import streamlit as st
from datetime import datetime
from database import cargar_catalogos
import pandas as pd

def render(conn, catalogos):
    st.header("➕ Registrar Nueva Recomendación")
    st.markdown("---")
    # Formulario en pestañas para mejor organización
    tab1, tab2 = st.tabs(["📋 Información Básica", "🏛️ Autoridad Señalada"])
    
    with tab1:  # Información Básica
        col1, col2 = st.columns(2)
        
        with col1:
            # Si venimos de agregar a expediente existente
            expediente_default = st.session_state.get('expediente_editar', '')
            expediente = st.text_input(
                "Número de Expediente *",
                value=expediente_default,
                placeholder="Ej: 0123/2024-A",
                help="Formato: Número/Año-Sub"
            )
            
            fecha_r = st.date_input(
                "Fecha de Resolución *",
                value=datetime.now().date(),
                format="DD/MM/YYYY"
            )
            
            subprocu = st.selectbox(
                "Subprocuraduría *",
                options=catalogos['sub'],
                index=None
            )
        
        with col2:
            numero = st.number_input(
                "Número de Recomendaciones *",
                min_value=1,
                step=1,
                help="Número de Recomendaciones emitidas"
            )
            recom_text = st.text_area(
                "Recomendación(es)",
                placeholder="Redacte las recomendaciones",
                height=150,
                max_chars=2000
            )
            observaciones = st.text_area(
                "Observaciones",
                placeholder="ACUMULADO AL ####/####-[A-Z]",
                height=120,
                max_chars=250
            )
    
    with tab2:  # Autoporidad Señalada
        st.markdown("### 🏛️ Autoridades y Hechos Denunciados")
        st.markdown("Puede agregar múltiples autoridades y hechos para este expediente.")
        
        # Inicializar lista en session_state si no existe
        if 'autoridades_lista' not in st.session_state:
            st.session_state.autoridades_lista = []
        
        # Contenedor para las autoridades
        autoridades_container = st.container()
        
        with autoridades_container:
            # Mostrar autoridades existentes
            if st.session_state.autoridades_lista:
                st.markdown("**Autoridades agregadas:**")
                for i, auth in enumerate(st.session_state.autoridades_lista):
                    col1, col2, col3, col4 = st.columns([3, 3, 3, 1])
                    with col1:
                        st.markdown(f"**Quejoso:** {auth['quejoso']}")
                    with col2:
                        st.markdown(f"**Autoridad:** {auth['autoridad']}")
                    with col3:
                        st.markdown(f"**Hecho:** {auth['hecho']}")
                    with col4:
                        if st.button("❌", key=f"eliminar__auth{i}"):
                            del st.session_state.autoridades_lista[i]
                            st.rerun()
            
            # Separador
            st.divider()
            quejoso = st.text_input(
                "Nombre del(los) Quejoso(s) *",
                placeholder="Nombre(s) de la(s) persona(s) involucrada(s)"
            )
            autoridad = st.text_input(
                "Dirigida a *",
                placeholder="Nombre de la autoridad a la que se dirige la recomendación",
                max_chars=255
            )
            dependencia = st.selectbox(
                "Dependencia *",
                options=catalogos['autoridadR'],
                index=None,
                placeholder="Seleccione la dependencia"
            )
            hecho = st.selectbox(
                "Hecho Denunciado *",
                options=catalogos['hechosR'],
                index=None,
                placeholder="Seleccione tipo de hecho"
            )
        col_add1, col_add2, col_add3 = st.columns([1, 2, 1])
        with col_add2:
            if st.button("➕ Agregar Autoridad", use_container_width=True):
                # Validar campos obligatorios
                if all([autoridad, dependencia, hecho]):
                    
                    nueva_entrada = {
                        'quejoso': quejoso,
                        'autoridad': autoridad,
                        'dependencia': dependencia,
                        'hecho': hecho
                    }
                    
                    st.session_state.autoridades_lista.append(nueva_entrada)
                    st.rerun()
                else:
                    st.error("Complete todos los campos obligatorios para agregar la autoridad")

    # Validación y botones (fuera de las pestañas)
    st.divider()
    st.markdown("### 📝 Validación y Envío")
    
    # Mostrar resumen de campos obligatorios
    campos_obligatorios = {
        "Expediente": expediente,
        "Fecha de Resolución": fecha_r,
        "Subprocuraduría": subprocu,
        "Quejoso": quejoso,
        "Autoridad": autoridad,
        "Hecho": hecho,
        "NumR": numero,
        "Dependencia": dependencia
    }
    
    faltantes = [campo for campo, valor in campos_obligatorios.items() if not valor]
    
    # Botones de acción
    col_btn1, col_btn2 = st.columns(2)
    
    with col_btn1:
        if st.button("📝 Guardar Recomendación", type="primary", use_container_width=True, key="btn_guardar_completo"):
            if not faltantes:
                with st.spinner("Guardando en todas las tablas..."):
                    try:
                        # 1. Insertar en tabla NoRecomendaciones
                        datos_basicos = (
                            expediente,
                            fecha_r,
                            subprocu,
                            observaciones if observaciones else None,
                            numero,
                            quejoso
                        )
                        datos = (
                            expediente,
                            fecha_r,
                            quejoso,
                            autoridad,
                            hecho,
                            numero,
                            dependencia if dependencia else None,
                            subprocu,
                            observaciones if observaciones else None,
                        )
                        cursor = conn.cursor()
                        if st.session_state.autoridades_lista:
                            for auth in st.session_state.autoridades_lista:
                                cursor.execute("""
                                    INSERT INTO ImportarRecomendaciones 
                                    (Expediente, FechaRecom, Quejoso, Autoridad, [Dirigida a], Causa,
                                    Respuesta,NumRecom, DSP,
                                    Recomendacion, SubProcu, Observaciones)
                                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?,?,?)
                                """, (
                                    expediente,
                                    fecha_r,
                                    auth['quejoso'],
                                    auth['dependencia'],
                                    auth['autoridad'],
                                    auth['hecho'],
                                    'Sin Cumplimiento',
                                    numero,
                                    0,
                                    recom_text,
                                    subprocu,
                                    observaciones if observaciones else None
                                ))
                        
                        conn.commit()
                        
                        st.success("✅ Resolución guardada exitosamente!")
                        st.balloons()
                        # Limpiar cache de catálogos
                        cargar_catalogos.clear()
                        # Limpiar estado
                        st.session_state.expediente_editar = ""
                        st.balloons()
                        # Opción: limpiar formulario o redirigir
                        #rerun()
                    except Exception as e:
                        conn.rollback()
                        st.error(f"❌ Error al guardar: {str(e)[:200]}")
            else:
                st.error("Complete todos los campos obligatorios (*)")
    
    with col_btn2:
        if st.button("🔄 Limpiar Formulario", use_container_width=True, key="btn_limpiar_completo"):
            # 1. Limpiar la lista de autoridades
            st.session_state.autoridades_lista = []
            
            # 2. Limpiar el expediente de edición
            if 'expediente_editar' in st.session_state:
                del st.session_state.expediente_editar
            
            # 3. Usar st.query_params para forzar una recarga completa
            # Esto es más efectivo que st.rerun() para limpiar widgets
            st.query_params.clear()
            
            # 4. Recargar
            st.rerun()