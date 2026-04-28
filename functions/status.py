# pages/modificar_estatus.py
import streamlit as st
import pandas as pd
from datetime import datetime
import plotly.express as px
from sqlalchemy import text

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
                    q.`Organismo emisor`,
                    q.`Tipo De Violencia`,
                    q.`AmbitoModalidadViolencia`,
                    q.Notas,
                    q.Notificado
                FROM Expediente q
                WHERE q.Expediente LIKE %(exp)s
                """
                df = pd.read_sql_query(query, conn, params={'exp': f"%{expediente_buscar}%"})
                
                if not df.empty:
                    st.success(f"✅ Expediente encontrado: {df['Expediente'].iloc[0]}")
                    
                    # Mostrar información actual
                    with st.expander("📋 Información Actual del Expediente", expanded=True):
                        st.metric("Expediente", df['Expediente'].iloc[0])
                        estatus_actual = df['Conclusión'].iloc[0] if df['Conclusión'].iloc[0] else "Sin estatus"
                        st.metric("Estatus Actual", estatus_actual)
                        st.metric("Desglose", df['Alias_Conclusión'].iloc[0] if df['Alias_Conclusión'].iloc[0] else "Sin estatus")
                        col_met1, col_met2 = st.columns(2)
                        with col_met1:
                            st.metric("Fecha de Entrada a SG", df['F_EntradaSG'].iloc[0].strftime("%d/%m/%Y") if pd.notnull(df['F_EntradaSG'].iloc[0]) else "N/A")
                            st.metric("Fecha de Conclusión", df['F_Conclusion'].iloc[0].strftime("%d/%m/%Y") if pd.notnull(df['F_Conclusion'].iloc[0]) else "N/A")
                            st.metric("Grupo Vulnerable", df['GrupoVulnerable'].iloc[0])
                            st.metric("Notas", df['Notas'].iloc[0])
                        with col_met2:
                            st.metric("Organismo Emisor", df['Organismo emisor'].iloc[0])
                            st.metric("Notificado", "Sí" if df['Notificado'].iloc[0] else "No")
                            st.metric("Tipo de Violencia", df['Tipo De Violencia'].iloc[0])
                            st.metric("Ámbito/Modalidad de Violencia", df['AmbitoModalidadViolencia'].iloc[0])
                    
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
                                value=None,
                                help="Fecha en que se concluyó el expediente"
                            )

                            grupo_vulnerable = st.selectbox(
                                "Grupo Vulnerable",
                                options=[""] + opciones_gv,
                                index=0
                            )
                            organismo_emisor = st.selectbox(
                                "Organismo Emisor",
                                options=[""] + catalogos.get('organismoemisor', []),
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
                                value=None,
                                help="Fecha en que entró a Secretaría General"
                            )
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
                                    
                                    # Preparar datos
                                    params = {
                                        "estatus": nuevo_estatus,
                                        "desglose": desglose,
                                        "fecha_conclusion": None,
                                        "fecha_entrada": None,
                                        "grupo_vulnerable": grupo_vulnerable if grupo_vulnerable else None,
                                        "organismo_emisor": organismo_emisor if organismo_emisor else None,
                                        "tipo_violencia": tipo_violencia if tipo_violencia else None,
                                        "ambito_violencia": ambito_violencia if ambito_violencia else None,
                                        "expediente": df['Expediente'].iloc[0]
                                    }
                                    
                                    # Si hay fecha de conclusión, convertirla
                                    if fecha_conclusion:
                                        try:
                                            #fecha_conclusion = datetime.strptime(fecha_conclusion, "%d/%m/%Y").date()
                                            #params.append(fecha_conv)
                                            params['fecha_conclusion'] = fecha_conclusion
                                        except:
                                            params['fecha_conclusion'] = None
                                    else:
                                        params['fecha_conclusion'] = None
                                    # Si hay fecha de SG, convertirla
                                    if fecha_entrada:
                                        try:
                                            #fecha_entrada = datetime.strptime(fecha_entrada, "%d/%m/%Y").date()
                                            #params.append(fecha_conv)
                                            params['fecha_entrada'] = fecha_entrada
                                        except:
                                            params['fecha_entrada'] = None
                                    else:
                                        params['fecha_entrada'] = None
                                    
                                    # Actualizar en la base de datos
                                    with conn.begin() as conn2:
                                        conn2.execute(text("""
                                            UPDATE Expediente 
                                            SET Conclusión = :estatus,  
                                                Alias_Conclusión = :desglose,
                                                F_Conclusion = :fecha_conclusion,
                                                F_EntradaSG = :fecha_entrada,
                                                GrupoVulnerable = :grupo_vulnerable,
                                                `Organismo emisor` = :organismo_emisor,
                                                `Tipo De Violencia` = :tipo_violencia,
                                                `AmbitoModalidadViolencia` = :ambito_violencia
                                            WHERE Expediente = :expediente
                                        """), params)

                                    st.success("✅ Estatus actualizado exitosamente!")
                                    st.balloons()
                                    
                                except Exception as e:
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
                
                # Aplicar filtros de fecha
                if fecha_desde and fecha_desde.strip():
                    fecha_desde_dt = datetime.strptime(fecha_desde, "%d/%m/%Y")
                
                if fecha_hasta and fecha_hasta.strip():
                    fecha_hasta_dt = datetime.strptime(fecha_hasta, "%d/%m/%Y")

                query = """
                SELECT 
                    Conclusión,
                    COUNT(*) as Cantidad
                FROM Expediente
                WHERE 1=1
                    AND F_Conclusion >= :fecha_desde_dt
                    AND F_Conclusion <= :fecha_hasta_dt
                GROUP BY Conclusión
                ORDER BY COUNT(*) DESC
                """

                #df_reporte = pd.read_sql_query(query, conn, params=params)
                # Ejecutar query con cursor
                df_reporte = pd.read_sql_query(text(query), conn, params={
                    'fecha_desde_dt': fecha_desde_dt,
                    'fecha_hasta_dt': fecha_hasta_dt
                })

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