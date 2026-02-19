import streamlit as st
import pandas as pd
from queries import buscar_expedientes, buscar_persona, buscar_autoridad

def render(conn, catalogos):
    st.header("🔍 Búsqueda")
    st.markdown("---")
    
    tab1, tab2, tab3 = st.tabs(["📋 Expediente", "👥 Personas", "🏛️ Autoridades"])
    
    with tab1: # Expediente
        col_search1, col_search2 = st.columns([3, 1])
        with col_search1:
            numero_buscar = st.text_input(
                "Número de expediente:",
                placeholder="Ej: 0123/2024-A",
                key="busqueda_principal",
                value=""  # Limpiar valor
            )
        with col_search2:
            st.write("")
            st.write("")
            if st.button("Buscar", type="primary", use_container_width=True, key="btn_buscar_accion"):
                st.session_state.buscar_clicked = True
        
        # Resultados
        if st.session_state.buscar_clicked or numero_buscar:
            with st.spinner("Buscando..."):
                resultados = buscar_expedientes(conn, numero_buscar)
            
            if not resultados.empty:
                st.success(f"📊 {len(resultados)} registros encontrados")
                
                # Agrupar por expediente
                for expediente in resultados['Expediente'].unique():
                    with st.expander(f"📄 Expediente: **{expediente}**", expanded=False):
                        datos = resultados[resultados['Expediente'] == expediente]
                        
                        # Resumen
                        col_res1, col_res2, col_res3 , col_res4 = st.columns(4)
                        with col_res1:
                            st.metric("Registros", len(datos))
                        with col_res2:
                            st.metric("Fecha de Inicio", datos['FechaInicio'].iloc[0])
                        with col_res3:
                            st.metric("Municipio", datos['Municipio'].iloc[0])
                        with col_res4:
                            st.metric("Estatus", datos['Conclusión'].iloc[0])
                        
                        # Detalles
                        st.dataframe(
                            datos[['Hecho', 'Dependencia']],
                            use_container_width=True,
                            hide_index=True,
                            column_config={
                                'Hecho': 'Hecho Denunciado',
                                'Dependencia': 'Dependencia Señalada',
                            }
                        )
                        
                        # Cuando encuentres un expediente para editar
                        if st.button("✏️ Editar Queja", key=f"editar_{expediente}"):
                            st.session_state.modo_edicion = True
                            st.session_state.expediente_editar = expediente
                            st.session_state.ir_a = "editar"
                            
                            # Limpiar listas previas para evitar arrastrar datos
                            if 'autoridades_lista' in st.session_state:
                                del st.session_state.autoridades_lista
                            if 'personas_lista' in st.session_state:
                                del st.session_state.personas_lista
                            
                            # Limpiar flags de carga
                            if 'autoridades_cargadas_' + expediente in st.session_state:
                                del st.session_state['autoridades_cargadas_' + expediente]
                            if 'personas_cargadas_' + expediente in st.session_state:
                                del st.session_state['personas_cargadas_' + expediente]
                            
                            st.rerun()
            else:
                st.info("No se encontraron resultados")

    with tab2: # Persona
        col_search1, col_search2 = st.columns([3, 1])
        with col_search1:
            nombre_buscar = st.text_input(
                "Nombre:",
                key="busqueda_persona",
                value=""  # Limpiar valor
            )
        with col_search2:
            st.write("")
            st.write("")
            if st.button("Buscar", type="primary", use_container_width=True, key="btn_buscar_persona"):
                st.session_state.buscar_clicked = True
        
        # Resultados
        if st.session_state.buscar_clicked or nombre_buscar:
            with st.spinner("Buscando..."):
                resultados = buscar_persona(conn, nombre_buscar)
            
            if not resultados.empty:
                st.success(f"📊 {len(resultados)} registros encontrados")
                
                resultados['Nombre']=resultados['Nombre'].str.upper()
                resultados['Nombre'] = resultados['Nombre'].str.strip()
                resultados['Nombre'] = resultados['Nombre'].str.replace(r'\s+', ' ', regex=True)
                resultados['Nombre'] = resultados['Nombre'].str.replace(r'[.,;:]', '', regex=True)

                # Agrupar por nombre
                for nombre in resultados['Nombre'].unique():
                    with st.expander(f"📄 Nombre: **{nombre}**", expanded=False):
                        datos = resultados[resultados['Nombre'] == nombre]
                        
                        # Resumen
                        col_res1, col_res2, col_res3 , col_res4 = st.columns(4)
                        with col_res1:
                            st.metric("Registros", len(datos))
                        
                        # Detalles
                        st.dataframe(
                            datos[['Expediente','FechaInicio','Conclusión', 'F_Conclusion','Hecho', 'Dependencia']],
                            use_container_width=True,
                            hide_index=True,
                            column_config={
                                'Expediente': 'Expediente',
                                'FechaInicio': 'Fecha de Inicio',
                                'Conclusión': 'Estatus',
                                'F_Conclusion': 'Fecha de Conclusión',
                                'Hecho': 'Hecho Denunciado',
                                'Dependencia': 'Dependencia Señalada',
                            }
                        )
                        
            else:
                st.info("No se encontraron resultados")

    with tab3: # Autoridad
        col_search1, col_search2 = st.columns([3, 1])
        with col_search1:
            autoridad_buscar = st.text_input(
                "Nombre de autoridad:",
                key="busqueda_autoridad",
                value=""  # Limpiar valor
            )
        with col_search2:
            st.write("")
            st.write("")
            if st.button("Buscar", type="primary", use_container_width=True, key="btn_buscar_autoridad"):
                st.session_state.buscar_clicked = True
        
        # Resultados
        if st.session_state.buscar_clicked or autoridad_buscar:
            with st.spinner("Buscando..."):
                resultados = buscar_autoridad(conn, autoridad_buscar)

            if not resultados.empty:
                st.success(f"📊 {len(resultados)} registros encontrados")

                # Agrupar por autoridad
                for autoridad in resultados['DireccionMunicipal'].unique():
                    with st.expander(f"📄 Autoridad: **{autoridad}**", expanded=False):
                        datos = resultados[resultados['DireccionMunicipal'] == autoridad]
                        
                        # Resumen
                        col_res1, col_res2, col_res3 , col_res4 = st.columns(4)
                        with col_res1:
                            st.metric("Registros", len(datos))
                        
                        # Detalles
                        st.dataframe(
                            datos[['Expediente','FechaInicio','Conclusión','Hecho', 'F_Conclusion']],
                            use_container_width=True,
                            hide_index=True,
                            column_config={
                                'Expediente': 'Expediente',
                                'FechaInicio': 'Fecha de Inicio',
                                'Conclusión': 'Estatus',
                                'Hecho': 'Hecho Denunciado',
                                'F_Conclusion': 'Fecha de Conclusión',
                            }
                        )