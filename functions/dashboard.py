import streamlit as st
from functions.dashboards import general, prioridad

MODOS = {
    "general": {
        "icono": "🌐",
        "titulo": "General",
        "descripcion": "Estadísticas generales dinámicas e interactivas de los expedientes de queja. "
                    "Rankings de autoridades y geolocalizaciones.",
    },
    "indice_prioridad": {
        "icono": "🚨",
        "titulo": "Índice de Prioridad",
        "descripcion": "Triage de casos activos según grupo vulnerable, hecho violatorio (INEGI), "
                    "tipo de violencia, autoridad señalada y lugar de procedencia.",
    },
}


def render(conn,contenedor_filtros):
    if "modo_dash" not in st.session_state:
        st.session_state.modo_dash = None

    # ------------------------------------------------------------
    # PASO 1: elegir el modo con tarjetas grandes (si no hay uno elegido)
    # ------------------------------------------------------------
    if st.session_state.modo_dash is None:
        st.header("📊 Dashboards")
        cols = st.columns(3)
        for col, (clave, info) in zip(cols, MODOS.items()):
            with col:
                with st.container(border=True, height='stretch', vertical_alignment='distribute'):
                    st.markdown(f"### {info['icono']}")
                    st.markdown(f"**{info['titulo']}**")
                    st.caption(info["descripcion"])
                    if st.button("Elegir", type="primary",key=f"elegir_dash_{clave}",width='stretch'):
                        st.session_state.modo_dash = clave
                        st.rerun()
        return  # no mostrar nada más hasta que elijan un modo

    # ------------------------------------------------------------
    # PASO 2: mostrar solo la búsqueda elegida
    # ------------------------------------------------------------
    modo = st.session_state.modo_dash
    info = MODOS[modo]

    col_titulo, col_volver = st.columns([5, 1])
    with col_titulo:
        st.markdown(f"### {info['icono']} {info['titulo']}")
        st.caption(info["descripcion"])
    with col_volver:
        st.write("")
        if st.button("↩️ Cambiar", width='stretch'):
            st.session_state.modo_dash = None
            # limpiar resultados anteriores
            for k in ["resultado_busqueda", "texto_buscado"]:
                st.session_state.pop(k, None)
            st.rerun()

    st.markdown("---")

    if modo == "general":
        general.render(conn,contenedor_filtros)
    elif modo == "indice_prioridad":
        prioridad.render(conn,contenedor_filtros)