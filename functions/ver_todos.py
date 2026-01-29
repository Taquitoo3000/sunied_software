import streamlit as st
import pandas as pd
import io
from datetime import datetime
from queries import buscar_expedientes

def render(conn, catalogos):
    st.header("📊 Todos los Registros")
    st.markdown("---")
        
    with st.spinner("Cargando datos..."):
        df_todos = buscar_expedientes(conn)
    
    if not df_todos.empty:
        # Filtros
        col_filt1, col_filt2, col_filt3 = st.columns(3)
        with col_filt1:
            filtro_exp = st.text_input("Filtrar por expediente:", key="filtro_exp")
        with col_filt2:
            filtro_mun = st.selectbox(
                "Filtrar por municipio:",
                options=["Todos"] + catalogos['municipios'],
                key="filtro_mun"
            )
        with col_filt3:
            filtro_dep = st.selectbox(
                "Filtrar por dependencia:",
                options=["Todos"] + catalogos['dependencias'],
                key="filtro_dep"
            )
        
        # Aplicar filtros
        df_filtrado = df_todos.copy()
        if filtro_exp:
            df_filtrado = df_filtrado[df_filtrado['Expediente'].str.contains(filtro_exp, na=False, case=False)]
        if filtro_mun != "Todos":
            df_filtrado = df_filtrado[df_filtrado['Municipio'] == filtro_mun]
        if filtro_dep != "Todos":
            df_filtrado = df_filtrado[df_filtrado['Dependencia'] == filtro_dep]
        
        # Mostrar
        st.dataframe(
            df_filtrado,
            use_container_width=True,
            hide_index=True,
            column_config={
                'Expediente': st.column_config.TextColumn("Expediente", width="medium"),
                'FechaInicio': st.column_config.TextColumn("Fecha", width="small"),
                'Municipio': st.column_config.TextColumn("Municipio", width="medium"),
                'Hecho': st.column_config.TextColumn("Hecho", width="large"),
                'Dependencia': st.column_config.TextColumn("Dependencia", width="medium"),
                'Observaciones': st.column_config.TextColumn("Observaciones", width="large")
            }
        )
        
        # Estadísticas
        st.divider()
        col_stats1, col_stats2, col_stats3 = st.columns(3)
        with col_stats1:
            st.metric("Total registros", len(df_todos))
        with col_stats2:
            st.metric("Filtrados", len(df_filtrado))
        with col_stats3:
            if len(df_filtrado) > 0:
                hecho_comun = df_filtrado['Hecho'].mode()
                if not hecho_comun.empty:
                    st.metric("Hecho más común", hecho_comun.iloc[0])
        
        # Botón para exportar
        if st.button("📥 Exportar a Excel", use_container_width=True, key="btn_exportar"):
            import io
            # Crear buffer en memoria
            output = io.BytesIO()
            # Escribir Excel al buffer
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                df_filtrado.to_excel(writer, index=False, sheet_name='Quejas')
    
            excel_bytes = output.getvalue()
            # Botón de descarga
            st.download_button(
                label="📥 Descargar Excel",
                data=excel_bytes,
                file_name=f"quejas_{datetime.now().strftime('%d%m%Y_%H%M')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True,
                key="btn_descargar_excel"
            )
    else:
        st.info("No hay registros disponibles")