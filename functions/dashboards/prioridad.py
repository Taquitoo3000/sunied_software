import pandas as pd
import plotly.express as px
import streamlit as st
from functions.dashboards.indice_prioridad import calcular_indice_prioridad, PESOS as PESOS_ACTUALES

COLOR_NIVEL = {
    "Urgente": "#b91c1c",
    "Alta": "#ea580c",
    "Media": "#ca8a04",
    "Baja": "#16a34a",
}
ORDEN_NIVEL = ["Urgente", "Alta", "Media", "Baja"]

# ---------------------------------------------------------------------------
# Carga de datos
# ---------------------------------------------------------------------------

def cargar_data(conn):
    query = """
        select
            e.Expediente,
            e.Subprocu,
            q.FechaInicio,
            c.Inegi as Hecho,
            q.DireccionMunicipal,
            q.Dependencia,
            q.AliasDependencia,
            e.GrupoVulnerable,
            e.Recepcion,
            q.LugarProcedencia,
            e.`Organismo emisor`,
            e.`Tipo de Violencia`,
            e.AmbitoModalidadViolencia,
            qs.Nombre,
            qs.Sexo,
            qs.Escolaridad,
            qs.Estado_Civil
        from Expediente as e
            left join Quejas as q on q.Expediente=e.Expediente
            left join Quejosos_Ampliado as qs on qs.Expediente=e.Expediente
            left join Catalogo_Hechos as c on q.Hecho=c.Hecho
        where
            e.F_Conclusion is null
    """
    df = pd.read_sql(query, conn).drop_duplicates()
    if "FechaInicio" in df.columns:
        df["FechaInicio"] = pd.to_datetime(df["FechaInicio"], errors="coerce")
    return df


def render(conn,contenedor_filtros):
    with st.spinner("Cargando datos..."):
        df_raw = cargar_data(conn)
        df = calcular_indice_prioridad(df_raw)

    # ---------------------------------------------------------------------------
    # Filtros
    # ---------------------------------------------------------------------------
    with contenedor_filtros:
        st.header("⚙️ Filtros")

        subprocus = sorted(df["Subprocu"].dropna().unique().tolist()) if "Subprocu" in df.columns else []
        filtro_subprocu = st.multiselect("Subprocuraduría", subprocus, default=subprocus)
        niveles = st.multiselect("Nivel de prioridad", ORDEN_NIVEL, default=ORDEN_NIVEL)

        if "FechaInicio" in df.columns and df["FechaInicio"].notna().any():
            fmin, fmax = df["FechaInicio"].min(), df["FechaInicio"].max()
            rango_fecha = st.date_input("Rango de fecha (FechaInicio)", [fmin, fmax])
        else:
            rango_fecha = None

    df_f = df.copy()
    if filtro_subprocu:
        df_f = df_f[df_f["Subprocu"].isin(filtro_subprocu)]
    if niveles:
        df_f = df_f[df_f["prioridad_nivel"].isin(niveles)]
    if rango_fecha and len(rango_fecha) == 2:
        ini, fin = pd.to_datetime(rango_fecha[0]), pd.to_datetime(rango_fecha[1])
        df_f = df_f[(df_f["FechaInicio"] >= ini) & (df_f["FechaInicio"] <= fin)]

    # ---------------------------------------------------------------------------
    # KPIs
    # ---------------------------------------------------------------------------
    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Expedientes (filtro)", len(df_f))
    c2.metric("Score promedio", f"{df_f['prioridad_score'].mean():.1f}" if len(df_f) else "—")
    c3.metric("Urgentes", int((df_f["prioridad_nivel"] == "Urgente").sum()))
    c4.metric("Altas", int((df_f["prioridad_nivel"] == "Alta").sum()))
    pct_urgente_alta = (
        (df_f["prioridad_nivel"].isin(["Urgente", "Alta"]).mean() * 100) if len(df_f) else 0
    )
    c5.metric("% Urgente + Alta", f"{pct_urgente_alta:.0f}%")

    st.divider()

    # ---------------------------------------------------------------------------
    # Fila 1: distribución de niveles + serie de tiempo
    # ---------------------------------------------------------------------------

    col_a, col_b = st.columns([1, 2])

    with col_a:
        st.subheader("Distribución por nivel")
        conteo_nivel = (
            df_f["prioridad_nivel"].value_counts().reindex(ORDEN_NIVEL).fillna(0).reset_index()
        )
        conteo_nivel.columns = ["nivel", "cantidad"]
        fig_pie = px.pie(
            conteo_nivel, names="nivel", values="cantidad",
            color="nivel", color_discrete_map=COLOR_NIVEL, hole=0.45,
        )
        fig_pie.update_layout(showlegend=True, margin=dict(t=10, b=10, l=10, r=10))
        st.plotly_chart(fig_pie, width='stretch')

    with col_b:
        st.subheader("Expedientes urgentes/altos en el tiempo")
        if "FechaInicio" in df_f.columns and df_f["FechaInicio"].notna().any():
            serie = df_f.copy()
            serie["mes"] = serie["FechaInicio"].dt.to_period("M").dt.to_timestamp()
            serie_agg = serie.groupby(["mes", "prioridad_nivel"]).size().reset_index(name="cantidad")
            fig_line = px.bar(
                serie_agg, x="mes", y="cantidad", color="prioridad_nivel",
                color_discrete_map=COLOR_NIVEL, category_orders={"prioridad_nivel": ORDEN_NIVEL},
            )
            fig_line.update_layout(margin=dict(t=10, b=10, l=10, r=10), legend_title="")
            st.plotly_chart(fig_line, width='stretch')
        else:
            st.info("No hay columna de fecha disponible en los datos.")

    # ---------------------------------------------------------------------------
    # Fila 2: por subprocuraduría + por grupo vulnerable
    # ---------------------------------------------------------------------------

    col_c, col_d = st.columns(2)

    with col_c:
        st.subheader("Score promedio por Subprocuraduría")
        if "Subprocu" in df_f.columns and len(df_f):
            agg_sub = (
                df_f.groupby("Subprocu")["prioridad_score"]
                .mean().round(1).sort_values(ascending=True).reset_index()
            )
            fig_sub = px.bar(agg_sub, x="prioridad_score", y="Subprocu", orientation="h")
            fig_sub.update_layout(margin=dict(t=10, b=10, l=10, r=10))
            st.plotly_chart(fig_sub, width='stretch')

    with col_d:
        st.subheader("Expedientes por Grupo Vulnerable")
        if "GrupoVulnerable" in df_f.columns and len(df_f):
            agg_grupo = df_f["GrupoVulnerable"].value_counts().head(10).reset_index()
            agg_grupo.columns = ["grupo", "cantidad"]
            fig_grupo = px.bar(agg_grupo.sort_values("cantidad"), x="cantidad", y="grupo", orientation="h")
            fig_grupo.update_layout(margin=dict(t=10, b=10, l=10, r=10))
            st.plotly_chart(fig_grupo, width='stretch')

    # ---------------------------------------------------------------------------
    # Fila 3: hechos más frecuentes + autoridades más señaladas
    # ---------------------------------------------------------------------------

    col_e, col_f = st.columns(2)

    with col_e:
        st.subheader("Hechos violatorios (INEGI) más frecuentes")
        if "Hecho" in df_f.columns and len(df_f):
            agg_hecho = df_f["Hecho"].value_counts().head(10).reset_index()
            agg_hecho.columns = ["hecho", "cantidad"]
            fig_hecho = px.bar(agg_hecho.sort_values("cantidad"), x="cantidad", y="hecho", orientation="h")
            fig_hecho.update_layout(margin=dict(t=10, b=10, l=10, r=10), yaxis_title="")
            st.plotly_chart(fig_hecho, width='stretch')

    with col_f:
        st.subheader("Autoridades más señaladas")
        if "Dependencia" in df_f.columns and len(df_f):
            agg_dep = df_f["Dependencia"].value_counts().head(10).reset_index()
            agg_dep.columns = ["dependencia", "cantidad"]
            fig_dep = px.bar(agg_dep.sort_values("cantidad"), x="cantidad", y="dependencia", orientation="h")
            fig_dep.update_layout(margin=dict(t=10, b=10, l=10, r=10), yaxis_title="")
            st.plotly_chart(fig_dep, width='stretch')

    st.divider()

    # ---------------------------------------------------------------------------
    # Metodología (fórmula en LaTeX)
    # ---------------------------------------------------------------------------

    with st.expander("📐 Metodología del índice de prioridad"):
            st.markdown("El puntaje de prioridad se calcula como una suma ponderada de 5 "
                        "sub-scores (cada uno en escala 0–10), escalada a 0–100:")
            st.latex(r"""
                \text{prioridad\_score} = 10 \times \Big(
                    0.30 \cdot S_{gv} + 0.25 \cdot S_{tv} + 0.25 \cdot S_{h}
                    + 0.10 \cdot S_{a} + 0.10 \cdot S_{l}
                \Big)
            """)
            st.markdown("Donde cada componente $S \\in [0, 10]$ se obtiene por catálogo/código, no por texto libre:")
            st.latex(r"""
                \begin{array}{ll}
                S_{gv} & \text{Grupo vulnerable (catálogo 01–21)} \\
                S_{tv} & \text{Tipo de violencia} \\
                S_{h}  & \text{Hecho — clasificación INEGI de DDHH} \\
                S_{a}  & \text{Autoridad señalada (Dependencia)} \\
                S_{l}  & \text{Lugar de procedencia (concentración por percentil)}
                \end{array}
            """)
            pesos_txt = " + ".join(f"{v:.2f}" for v in PESOS_ACTUALES.values())
            st.caption(f"Pesos actuales: {pesos_txt} = {sum(PESOS_ACTUALES.values()):.2f}")
    st.divider()
    # ---------------------------------------------------------------------------
    # Tabla de expedientes prioritarios
    # ---------------------------------------------------------------------------

    st.subheader("Expedientes ordenados por prioridad")

    columnas_tabla = [
        c for c in [
            "Expediente", "FechaInicio",
            "prioridad_score", "prioridad_nivel",
            "GrupoVulnerable", "Tipo de Violencia",
            "Hecho", "Dependencia", "LugarProcedencia",
        ] if c in df_f.columns
    ]

    st.dataframe(
        df_f.sort_values("prioridad_score", ascending=False)[columnas_tabla],
        width='stretch',
        height=450,
    )

    st.download_button(
        "Descargar expedientes con score (CSV)",
        data=df_f.sort_values("prioridad_score", ascending=False).to_csv(index=False).encode("utf-8-sig"),
        file_name="expedientes_priorizados.csv",
        mime="text/csv",
    )