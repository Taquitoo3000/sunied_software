# pages/modificar_estatus.py
import streamlit as st
import pandas as pd
from datetime import datetime
from queries import buscar_expedientes
import plotly.express as px

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
        
        if buscar_btn or expediente_buscar:
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
                            opciones_gv = catalogos.get('grupovulnerable', [])
                            opciones_tv = catalogos.get('TipoViolencia', [])
                            opciones_av = catalogos.get('AmbitoViolencia', [])
                            
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

                            grupo_vulnerable = st.selectbox(
                                "Grupo Vulnerable",
                                options=[""] + opciones_gv,
                                index=0
                            )
                        
                        with col_est2:
                            desglose = st.selectbox(
                                "Desglose del Estatus",
                                options=[""] + catalogos.get('Alias_Status', []),
                                index=0,
                                help="Selecciona un desglose para el estatus"
                            )
                            fecha_entrada = st.date_input(
                                "Fecha Entrada a SG",
                                value=datetime.now(),
                                help="Fecha en que entró a Secretaría General"
                            ).strftime("%d/%m/%Y")
                            tipo_violencia = st.selectbox(
                                'Tipo de Violencia',
                                options=[""]+opciones_tv,
                                index=0
                            )
                            ambito_violencia = st.selectbox(
                                'Ambito de Violencia',
                                options=[""]+opciones_av,
                                index=0
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
                                    # Si hay fecha de SG, convertirla
                                    if fecha_entrada and fecha_entrada.strip():
                                        try:
                                            fecha_conv = datetime.strptime(fecha_entrada, "%d/%m/%Y").date()
                                            params.append(fecha_conv)
                                        except:
                                            params.append(None)
                                    else:
                                        params.append(None)
                                    if grupo_vulnerable:
                                        params.append(grupo_vulnerable)
                                    else:
                                        params.append(None)
                                    if tipo_violencia:
                                        params.append(tipo_violencia)
                                    else:
                                        params.append(None)
                                    if ambito_violencia:
                                        params.append(ambito_violencia)
                                    else:
                                        params.append(None)

                                    params.append(df['Expediente'].iloc[0])
                                    
                                    # Actualizar en la base de datos
                                    cursor.execute("""
                                        UPDATE Expediente 
                                        SET Conclusión = ?,  
                                            Alias_Conclusión = ?,
                                            F_Conclusion = ?,
                                            F_EntradaSG = ?,
                                            GrupoVulnerable = ?,
                                            [Tipo De Violencia] = ?,
                                            AmbitoModalidadViolencia = ?
                                        WHERE Expediente = ?
                                    """, params)
                                    
                                    conn.commit()
                                    st.success("✅ Estatus actualizado exitosamente!")
                                    st.balloons()
                                    
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
                cursor = conn.cursor() # este funciona junto con cursor.execute()
                query = """
                SELECT 
                    Conclusión,
                    COUNT(*) as Cantidad
                FROM Expediente
                WHERE 1=1
                """
                
                # Aplicar filtros de fecha
                if fecha_desde and fecha_desde.strip():
                    fecha_desde_dt = datetime.strptime(fecha_desde, "%d/%m/%Y")
                    fecha_str = fecha_desde_dt.strftime("%d/%m/%Y")
                    query += f" AND F_Conclusion >= #{fecha_str}#"
                
                if fecha_hasta and fecha_hasta.strip():
                    fecha_hasta_dt = datetime.strptime(fecha_hasta, "%d/%m/%Y")
                    fecha_str = fecha_hasta_dt.strftime("%d/%m/%Y")
                    query += f" AND F_Conclusion <= #{fecha_str}#"
                
                query += " GROUP BY Conclusión ORDER BY COUNT(*) DESC"

                #df_reporte = pd.read_sql_query(query, conn, params=params)
                # Ejecutar query con cursor
                cursor.execute(query)

                columns = [column[0] for column in cursor.description]
                results = cursor.fetchall()
                df_reporte = pd.DataFrame.from_records(results, columns=columns)
                
                if not df_reporte.empty:
                    st.write("### Resumen por Estatus")
                    
                    # Mostrar métricas
                    col1, col2 = st.columns(2)
                    with col1:
                        st.metric("Total Expedientes", df_reporte['Cantidad'].sum())
                    with col2:
                        estatus_comun = df_reporte.iloc[0]['Conclusión'] if len(df_reporte) > 0 else "N/A"
                        st.metric("Estatus Más Común", estatus_comun)
                    
                    # Mostrar tabla
                    st.dataframe(df_reporte, use_container_width=True)
                    
                    # Gráfico
                    fig = px.pie(df_reporte, values='Cantidad', names='Conclusión')
                    st.plotly_chart(fig, use_container_width=True)
                    
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