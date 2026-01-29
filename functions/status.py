# pages/modificar_estatus.py
import streamlit as st
import pandas as pd
from datetime import datetime
from queries import buscar_expedientes

def render(conn, catalogos):
    st.header("🔄 Modificar Estatus de Expediente")
    st.markdown("---")
    
    # Tabs para diferentes funcionalidades
    tab1, tab2 = st.tabs(["🔍 Buscar y Modificar", "📈 Reporte de Estatus"])
    
    with tab1:  # Búsqueda individual
        st.subheader("Buscar Expediente para Modificar")
        
        col1, col2 = st.columns([3, 1])
        with col1:
            expediente_buscar = st.text_input(
                "Número de Expediente:",
                placeholder="Ej: 0123/2024-A",
                key="buscar_estatus"
            )
        with col2:
            st.write("")
            st.write("")
            buscar_btn = st.button("🔍 Buscar", use_container_width=True, type="primary")
        
        if buscar_btn and expediente_buscar:
            with st.spinner("Buscando expediente..."):
                # Buscar expediente
                query = """
                SELECT 
                    q.Expediente,
                    q.Conclusión,
                    q.Alias_Conclusión,
                    q.F_Conclusion,
                    q.F_EntradaSG,
                    q.GrupoVulnerable,
                    q.Notas,
                    q.Notificado
                FROM Expediente q
                WHERE q.Expediente LIKE ?
                """
                df = pd.read_sql_query(query, conn, params=[f"%{expediente_buscar}%"])
                
                if not df.empty:
                    st.success(f"✅ Expediente encontrado: {df['Expediente'].iloc[0]}")
                    
                    # Mostrar información actual
                    with st.expander("📋 Información Actual del Expediente", expanded=True):
                        st.metric("Expediente", df['Expediente'].iloc[0])
                        estatus_actual = df['Conclusión'].iloc[0] if df['Conclusión'].iloc[0] else "Sin estatus"
                        st.metric("Estatus Actual", estatus_actual)
                        st.metric("Desglose", df['Alias_Conclusión'].iloc[0] if df['Alias_Conclusión'].iloc[0] else "Sin estatus")
                        st.metric("Fecha de Entrada a SG", df['F_EntradaSG'].iloc[0].strftime("%d/%m/%Y") if pd.notnull(df['F_EntradaSG'].iloc[0]) else "N/A")
                        st.metric("Fecha de Conclusión", df['F_Conclusion'].iloc[0].strftime("%d/%m/%Y") if pd.notnull(df['F_Conclusion'].iloc[0]) else "N/A")
                        st.metric("Grupo Vulnerable", df['GrupoVulnerable'].iloc[0])
                        st.metric("Notas", df['Notas'].iloc[0])
                    
                    # Formulario para modificar estatus
                    st.subheader("📝 Actualizar Estatus")
                    
                    with st.form(key="form_actualizar_estatus"):
                        col_est1, col_est2 = st.columns(2)
                        
                        with col_est1:
                            # Opciones de estatus
                            opciones_estatus = catalogos.get('Status', [])
                            
                            nuevo_estatus = st.selectbox(
                                "Nuevo Estatus *",
                                options=[""] + opciones_estatus,
                                index=0
                            )
                            
                            fecha_conclusion = st.date_input(
                                "Fecha de Conclusión",
                                value=datetime.now(),
                                help="Fecha en que se concluyó el expediente"
                            ).strftime("%d/%m/%Y")
                        
                        with col_est2:
                            desglose = st.selectbox(
                                "Desglose del Estatus",
                                options=[""] + catalogos.get('Alias_Status', []),
                                index=0,
                                help="Selecciona un desglose para el estatus"
                            )
                        
                        # Botón para guardar
                        col_btn1, col_btn2 = st.columns([1, 3])
                        with col_btn1:
                            submitted = st.form_submit_button("💾 Guardar Cambios", type="primary")
                        
                        if submitted:
                            if not nuevo_estatus:
                                st.error("Debe actualizar un estatus")
                            else:
                                try:
                                    cursor = conn.cursor()
                                    
                                    # Preparar datos
                                    params = [nuevo_estatus,desglose]
                                    
                                    # Si hay fecha de conclusión, convertirla
                                    if fecha_conclusion and fecha_conclusion.strip():
                                        try:
                                            fecha_conv = datetime.strptime(fecha_conclusion, "%d/%m/%Y").date()
                                            params.append(fecha_conv)
                                        except:
                                            params.append(None)
                                    else:
                                        params.append(None)
                                    
                                    # Agregar observaciones
                                    params.append(desglose if desglose and desglose.strip() else None)
                                    params.append(df['Expediente'].iloc[0])
                                    
                                    # Actualizar en la base de datos
                                    cursor.execute("""
                                        UPDATE Expediente 
                                        SET Conclusión = ?, 
                                            F_Conclusion = ?, 
                                            Alias_Conclusión = ?
                                        WHERE Expediente = ?
                                    """, params)
                                    
                                    conn.commit()
                                    
                                    st.success("✅ Estatus actualizado exitosamente!")
                                    st.balloons()
                                    st.rerun()
                                    
                                except Exception as e:
                                    conn.rollback()
                                    st.error(f"❌ Error al actualizar: {str(e)}")
                else:
                    st.warning("⚠️ No se encontró el expediente")
    
    with tab2:  # Reportes
        st.subheader("📈 Reporte de Estatus")
        
        # Filtros para el reporte
        col_filt1, col_filt2 = st.columns(2)
        
        with col_filt1:
            fecha_desde = st.text_input("Fecha desde", placeholder="DD/MM/YYYY")
        
        with col_filt2:
            fecha_hasta = st.text_input("Fecha hasta", placeholder="DD/MM/YYYY", 
                                       value=datetime.now().strftime("%d/%m/%Y"))
        
        # Generar reporte
        if st.button("📊 Generar Reporte", type="primary"):
            try:
                query = """
                SELECT 
                    Conclusión,
                    COUNT(*) as Cantidad
                FROM Expediente
                WHERE 1=1
                """
                
                params = []
                
                # Aplicar filtros de fecha
                if fecha_desde and fecha_desde.strip():
                    fecha_desde_dt = datetime.strptime(fecha_desde, "%d/%m/%Y")
                    query += " AND [Fecha de Inicio] >= ?"
                    params.append(fecha_desde_dt)
                
                if fecha_hasta and fecha_hasta.strip():
                    fecha_hasta_dt = datetime.strptime(fecha_hasta, "%d/%m/%Y")
                    query += " AND [Fecha de Inicio] <= ?"
                    params.append(fecha_hasta_dt)
                
                query += " GROUP BY Conclusión ORDER BY Cantidad DESC"
                
                df_reporte = pd.read_sql_query(query, conn, params=params)
                
                if not df_reporte.empty:
                    st.write("### Resumen por Estatus")
                    
                    # Mostrar métricas
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Total Expedientes", df_reporte['Cantidad'].sum())
                    with col2:
                        st.metric("Estatus Diferentes", len(df_reporte))
                    with col3:
                        estatus_comun = df_reporte.iloc[0]['Conclusión'] if len(df_reporte) > 0 else "N/A"
                        st.metric("Estatus Más Común", estatus_comun)
                    
                    # Mostrar tabla
                    st.dataframe(df_reporte, use_container_width=True)
                    
                    # Gráfico
                    st.bar_chart(df_reporte.set_index('Conclusión')['Cantidad'])
                    
                    # Botón para exportar
                    csv = df_reporte.to_csv(index=False).encode('utf-8')
                    st.download_button(
                        label="📥 Descargar Reporte CSV",
                        data=csv,
                        file_name=f"reporte_estatus_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
                        mime="text/csv"
                    )
                else:
                    st.info("No hay datos para el período seleccionado")
                    
            except Exception as e:
                st.error(f"Error al generar reporte: {str(e)}")