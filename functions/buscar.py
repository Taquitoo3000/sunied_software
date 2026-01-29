import streamlit as st
import pandas as pd
from queries import buscar_expedientes

def render(conn, catalogos):
    st.header("🔍 Búsqueda de Expedientes")
    st.markdown("---")
    
    # Búsqueda
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
                    
                    # Botón para agregar nuevo hecho
                    if st.button(f"Agregar hecho a {expediente}", type="primary",
                                key=f"add_{expediente}",
                                use_container_width=True):
                        st.session_state.expediente_editar = expediente
                        st.session_state.ir_a = "nueva"
                        st.rerun()
        else:
            st.info("No se encontraron resultados")