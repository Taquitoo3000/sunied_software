import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import requests

def render(conn):
    st.markdown("""
    <div class="dashboard-header">
        <h1 style="margin:0; font-size:28px;">Unidad de Estadística</h1>
        <p style="color:#7E05FF; opacity:0.9; margin:5px 0 0 0; font-size:16px;">
            Dashboard Interactivo de Gestión de Quejas
        </p>
    </div>
    """, unsafe_allow_html=True)
    with st.spinner("Cargando datos desde MySQL..."):
        df, df2 = cargar_datos(conn)
 
    # ── SIDEBAR / FILTROS ──────────────────────
    with st.sidebar:
        st.header("🔍 Filtros")
 
        año_min = int(df['Año'].min())
        año_max = int(df['Año'].max())
        rango_anios = st.slider(
            "Rango de Años",
            min_value=año_min, max_value=año_max,
            value=(año_min, año_max)
        )
 
        opciones_subprocu = ['Todas'] + sorted(df['SubProcu'].dropna().unique().tolist())
        subprocu_sel = st.selectbox("Subprocuraduría", opciones_subprocu)
 
    # ── FILTRADO ───────────────────────────────
    mask  = df['Año'].between(rango_anios[0], rango_anios[1])
    mask2 = df2['Año'].between(rango_anios[0], rango_anios[1])
 
    df_f  = df [mask].copy()
    df2_f = df2[mask2].copy()
 
    if subprocu_sel != 'Todas':
        df_f  = df_f [df_f ['SubProcu'] == subprocu_sel]
        df2_f = df2_f[df2_f['SubProcu'] == subprocu_sel]
 
    # ── MÉTRICAS ───────────────────────────────
    total      = len(df_f)
    concluidos = df_f['F_Conclusion'].notna().sum()
    tasa       = f"{(concluidos/total*100):.1f}%" if total > 0 else "0%"
    tiempo_p   = df_f.loc[df_f['F_Conclusion'].notna(), 'TiempoDias'].mean()
    tiempo_str = f"{tiempo_p:.0f} días" if pd.notna(tiempo_p) else "N/A"
    en_tramite = df_f['F_Conclusion'].isna().sum()
 
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("📁 Total Expedientes", f"{total:,}")
    col2.metric("✅ Tasa Conclusión",   tasa)
    col3.metric("⏱️ Tiempo Promedio",   tiempo_str)
    col4.metric("🔄 En Trámite",        f"{en_tramite:,}")
 
    st.divider()
 
    # ── FILA 1: Evolución + Conclusiones ──────
    c1, c2 = st.columns(2)
    with c1:
        st.plotly_chart(fig_evolucion(df_f),    width='stretch')
    with c2:
        st.plotly_chart(fig_conclusiones(df_f), width='stretch')
 
    # ── FILA 2: Eficiencia + Grupos ───────────
    c3, c4 = st.columns(2)
    with c3:
        st.plotly_chart(fig_eficiencia(df_f), width='stretch')
    with c4:
        if 'DireccionMunicipal' in df2_f.columns and 'Dependencia' in df2_f.columns:
            st.plotly_chart(fig_grupos_vulnerables(df2_f), width='stretch')
        else:
            st.info("Columnas DireccionMunicipal / Dependencia no disponibles en df2.")
 
    # ── MAPA DE CALOR ─────────────────────────
    st.plotly_chart(fig_mapa_calor(df_f, rango_anios), width='stretch')
 
    # ── MAPA GEOGRÁFICO ───────────────────────
    mapa = fig_mapa_geografico(df_f)
    if mapa:
        st.plotly_chart(mapa, width='stretch')
    else:
        st.warning("No se encontraron ubicaciones con coordenadas en los datos filtrados.")

def cargar_datos(conn):
    quejas = pd.read_sql("SELECT * FROM Quejas", conn)
    expediente = pd.read_sql("SELECT * FROM Expediente", conn)
    
    # Merge
    df = pd.merge(quejas, expediente, on='Expediente', how='inner', suffixes=('', '_expediente'))
    columnas_duplicadas = [col for col in df.columns if col.endswith('_expediente')]
    if columnas_duplicadas:
        df = df.drop(columns=columnas_duplicadas)
    df2=df
    columnas = [
    'Expediente', 
    'SubProcu', 
    'FechaInicio', 
    'LugarProcedencia', 
    'Recepcion', 
    'Conclusión', 
    'F_Conclusion', 
    'GrupoVulnerable'
    ]
    columnas_finales = [col for col in columnas if col in df.columns]
    df = df[columnas_finales].drop_duplicates()

    # Ajustar fechas
    df['FechaInicio'] = pd.to_datetime(df['FechaInicio'], errors='coerce')
    df['F_Conclusion'] = pd.to_datetime(df['F_Conclusion'], errors='coerce')
    df['Año'] = df['FechaInicio'].dt.year
    df['Mes'] = df['FechaInicio'].dt.month
    df = df[df['Año'].between(2000, 2030)]
    df = df.sort_values(['FechaInicio', 'Expediente'])
    df = df.reset_index(drop=True)
    df2['FechaInicio'] = pd.to_datetime(df2['FechaInicio'], errors='coerce')
    df2['Año'] = df2['FechaInicio'].dt.year
    df2['Mes'] = df2['FechaInicio'].dt.month
    df2 = df2[df2['Año'].between(2000, 2030)]
    df2 = df2.sort_values(['FechaInicio', 'Expediente'])
    df2 = df2.reset_index(drop=True)

    # Calcular tiempos
    mask_concluidos = df['F_Conclusion'].notna() & df['FechaInicio'].notna()
    df.loc[mask_concluidos, 'TiempoDias'] = (
        df.loc[mask_concluidos, 'F_Conclusion'] - df.loc[mask_concluidos, 'FechaInicio']
    ).dt.days
        
    return df,df2

# ─────────────────────────────────────────────
# COORDENADAS
# ─────────────────────────────────────────────
COORDENADAS = {
    # ── Municipios de Guanajuato ──────────────────────────────────────────
    'León':                          [21.1250, -101.6860],
    'Celaya':                        [20.5234, -100.8157],
    'San Miguel de Allende':         [20.9144, -100.7450],
    'Salvatierra':                   [20.2134, -100.8802],
    'Irapuato':                      [20.6896, -101.3540],
    'Yuriria':                       [20.2100, -101.1328],
    'Silao':                         [20.9437, -101.4270],
    'Dolores Hidalgo C.I.N.':        [21.1564, -100.9345],
    'Villagrán':                     [20.5153, -100.9972],
    'Tarandacuao':                   [20.0000, -100.5167],
    'Valle de Santiago':             [20.3928, -101.1917],
    'Guanajuato':                    [21.0190, -101.2574],
    'Pueblo Nuevo':                  [20.5436, -101.3714],
    'Salamanca':                     [20.5706, -101.1975],
    'Cortazar':                      [20.4833, -100.9667],
    'Apaseo el Grande':              [20.5458, -100.6861],
    'Acámbaro':                      [20.0300, -100.7222],
    'Comonfort':                     [20.7222, -100.7597],
    'San Luis de la Paz':            [21.2986, -100.5167],
    'Moroleón':                      [20.1278, -101.1917],
    'San Felipe':                    [21.4781, -101.2156],
    'San Francisco del Rincón':      [21.0183, -101.8550],
    'San José Iturbide':             [21.0014, -100.3842],
    'Apaseo el Alto':                [20.4583, -100.6208],
    'Xichú':                         [21.3000, -100.0583],
    'Coroneo':                       [20.2000, -100.3667],
    'Pénjamo':                       [20.4314, -101.7228],
    'Victoria':                      [21.2111, -100.2139],
    'Tarimoro':                      [20.2889, -100.7583],
    'Huanímaro':                     [20.3683, -101.4997],
    'Purísima del Rincón':           [21.0344, -101.8700],
    'Tierra Blanca':                 [21.1000, -100.1583],
    'Jerécuaro':                     [20.1556, -100.5083],
    'Cuerámaro':                     [20.6250, -101.6736],
    'Abasolo':                       [20.4494, -101.5303],
    'Santiago Maravatío':            [20.1739, -101.0000],
    'Santa Cruz de Juventino Rosas': [20.6433, -100.9928],
    'Santa Catarina':                [21.1411, -100.0694],
    'Atarjea':                       [21.2667,  -99.7167],
    'Ocampo':                        [21.6472, -101.4792],
    'Uriangato':                     [20.1400, -101.1717],
    'Jaral del Progreso':            [20.3714, -101.0611],
    'San Diego de la Unión':         [21.4667, -100.8750],
    'Doctor Mora':                   [21.1411, -100.3194],
    'Manuel Doblado':                [20.7289, -101.9525],
    'Romita':                        [20.8711, -101.5169],
 
    # ── Estados de la República ───────────────────────────────────────────
    'Estado de Querétaro':           [20.5881, -100.3881],
    'ESTADO DE MÉXICO':              [19.4969,  -99.7233],
    'Estado de Michoacán':           [19.5665, -101.7068],
    'Estado de Jalisco':             [20.6595, -103.3494],
    'Estado de Ciudad de México':    [19.4326,  -99.1332],
    'Estado de Sinaloa':             [25.1721, -107.4795],
    'Estado de Tamaulipas':          [24.2669,  -98.8363],
    'Estado de Guerrero':            [17.5734,  -99.9580],
    'Estado de Nuevo León':          [25.5922, -100.2840],
    'Estado de Coahuila':            [27.0587, -101.7068],
    'Estado de Aguascalientes':      [21.8853, -102.2916],
    'Estado de Zacatecas':           [22.7709, -102.5832],
    'Estado de Morelos':             [18.6813,  -99.1013],
    'Estado de Durango':             [24.0277, -104.6532],
    'Estado de Nayarit':             [21.7514, -104.8455],
    'Estado de San Luis Potosí':     [22.1565, -100.9855],
    'Estado de Veracruz':            [19.1738,  -96.1342],
    'Estado de Baja California':     [32.6245, -115.4523],
    'Estado de Hidalgo':             [20.0911,  -98.7624],
    'Estado de Sonora':              [29.2972, -110.3309],
    'Estado de Chihuahua':           [28.6330, -106.0691],
    'Estado de Chiapas':             [16.7569,  -93.1292],
    'Estado de Oaxaca':              [17.0732,  -96.7266],
    'Estado de Tabasco':             [17.8409,  -92.6189],
    'Estado de Yucatán':             [20.9801,  -89.6234],
 
    # ── Autoridades de otros estados ─────────────────────────────────────
    'AUTORIDADES DE PUEBLA':         [19.0414,  -98.2063],
    'Autoridades del Estado de México': [19.4969, -99.7233],
    'AUTORIDADES DE GUERRERO':       [17.5734,  -99.9580],
    'Autoridades de Querétaro':      [20.5881, -100.3881],
    'Autoridades de Ciudad de México': [19.4326, -99.1332],
    'Autoridades de Durango':        [24.0277, -104.6532],
    'Autoridades de Jalisco':        [20.6595, -103.3494],
    'Autoridades de Coahuila':       [27.0587, -101.7068],
    'Autoridades de Oaxaca':         [17.0732,  -96.7266],
    'Autoridades de Michoacán':      [19.5665, -101.7068],
    'Autoridades de Chiapas':        [16.7569,  -93.1292],
    'Autoridades de Veracruz':       [19.1738,  -96.1342],
    'Autoridades de Hidalgo':        [20.0911,  -98.7624],
    'Autoridades de Sonora':         [29.2972, -110.3309],
    'Autoridades de Nayarit':        [21.7514, -104.8455],
 
    # ── Otros países ─────────────────────────────────────────────────────
    'Otro País Honduras':            [14.0818,  -87.2068],
    'Otro País Honduras y El Salvador': [14.0818, -87.2068],
    'Otro País Estados Unidos':      [39.8283,  -98.5795],
    'Otro País Guatemala':           [14.6349,  -90.5069],
    'Otro País Colombia':            [ 4.5709,  -74.2973],
 
    # ── Sin coordenada ────────────────────────────────────────────────────
    'Otro País':                     None,
    'Indeterminado':                 None,
    'null':                          None,
}
 
MUNICIPIOS_GTO = {
    'León', 'Celaya', 'San Miguel de Allende', 'Salvatierra', 'Irapuato',
    'Yuriria', 'Silao', 'Dolores Hidalgo C.I.N.', 'Villagrán', 'Tarandacuao',
    'Valle de Santiago', 'Guanajuato', 'Pueblo Nuevo', 'Salamanca', 'Cortazar',
    'Apaseo el Grande', 'Acámbaro', 'Comonfort', 'San Luis de la Paz', 'Moroleón',
    'San Felipe', 'San Francisco del Rincón', 'San José Iturbide', 'Apaseo el Alto',
    'Xichú', 'Coroneo', 'Pénjamo', 'Victoria', 'Tarimoro', 'Huanímaro',
    'Purísima del Rincón', 'Tierra Blanca', 'Jerécuaro', 'Cuerámaro', 'Abasolo',
    'Santiago Maravatío', 'Santa Cruz de Juventino Rosas', 'Santa Catarina',
    'Atarjea', 'Ocampo', 'Uriangato', 'Jaral del Progreso', 'San Diego de la Unión',
    'Doctor Mora', 'Manuel Doblado', 'Romita',
}

def fig_evolucion(df_f):
    df_f = df_f.copy()
    df_f['AñoMes'] = df_f['FechaInicio'].dt.to_period('M')
    mensual = df_f.groupby('AñoMes').size().reset_index(name='Expedientes')
    mensual['Fecha'] = mensual['AñoMes'].dt.to_timestamp()
    fig = px.line(mensual, x='Fecha', y='Expedientes',
                  title='Evolución Temporal de Expedientes Recibidos',
                  template='plotly_white')
    fig.update_layout(xaxis_title="Fecha", yaxis_title="Número de Expedientes", hovermode='x unified')
    return fig
 
 
def fig_conclusiones(df_f):
    conteo = df_f['Conclusión'].value_counts()
    fig = px.pie(values=conteo.values, names=conteo.index,
                 title='Distribución de Tipos de Conclusión', template='plotly_white')
    fig.update_traces(textposition='inside', textinfo='percent+label')
    return fig
 
 
def fig_eficiencia(df_f):
    ef = df_f.groupby('SubProcu').agg(
        Expedientes=('Expediente', 'count'),
        TiempoDias=('TiempoDias', 'mean')
    ).reset_index()
    fig = px.bar(ef, x='SubProcu', y='TiempoDias',
                 title='Tiempo Promedio de Conclusión por Zona',
                 template='plotly_white', color='TiempoDias',
                 color_continuous_scale='Viridis')
    fig.update_layout(xaxis_title="Subprocuraduría", yaxis_title="Tiempo Promedio (días)")
    return fig
 
 
def fig_grupos_vulnerables(df2_f):
    d = df2_f.copy()
    d = d[d['DireccionMunicipal'].notna()]
    d = d[~d['DireccionMunicipal'].isin(['null', ''])]
    d = d.drop_duplicates(subset=['Expediente', 'Hecho', 'Dependencia'])
    grupos = d['Dependencia'].value_counts().head(10).reset_index()
    grupos.columns = ['Ciudad', 'Cantidad']
    fig = px.bar(grupos, x='Cantidad', y='Ciudad', orientation='h',
                 title='Procedencia de los Expedientes', template='plotly_white',
                 color='Cantidad', color_continuous_scale='Blues')
    fig.update_layout(xaxis_title="Número de Expedientes", yaxis_title="Ciudad")
    return fig
 
 
def fig_mapa_calor(df_f, rango_anios):
    años   = list(range(rango_anios[0], rango_anios[1] + 1))
    meses  = list(range(1, 13))
    matriz = np.zeros((len(meses), len(años)))
    for i, año in enumerate(años):
        for j, mes in enumerate(meses):
            matriz[j, i] = ((df_f['FechaInicio'].dt.year == año) &
                            (df_f['FechaInicio'].dt.month == mes)).sum()
    nombres_meses = ['Ene','Feb','Mar','Abr','May','Jun','Jul','Ago','Sep','Oct','Nov','Dic']
    fig = px.imshow(matriz, x=años, y=nombres_meses,
                    labels=dict(x="Año", y="Mes", color="Expedientes"),
                    title='Expedientes por Mes y Año', aspect="auto",
                    color_continuous_scale='Viridis')
    return fig
 
 
@st.cache_data(ttl=3600)
def obtener_geojson_guanajuato():
    url = "https://raw.githubusercontent.com/angelnmara/geojson/master/mexicoHigh.json"
    r   = requests.get(url, timeout=10)
    gj  = r.json()
    feature = next(f for f in gj['features'] if 'Guanajuato' in f['properties'].get('name',''))
    return {"type": "FeatureCollection", "features": [feature]}
 
 
def extraer_lats_lons(geojson):
    lats, lons = [], []
    for feature in geojson['features']:
        geom = feature['geometry']
        rings = []
        if geom['type'] == 'Polygon':
            rings = geom['coordinates']
        elif geom['type'] == 'MultiPolygon':
            rings = [ring for poly in geom['coordinates'] for ring in poly]
        for ring in rings:
            lons += [p[0] for p in ring] + [None]
            lats += [p[1] for p in ring] + [None]
    return lats, lons
 
 
def fig_mapa_geografico(df_f):
    if 'LugarProcedencia' not in df_f.columns:
        return None
 
    d = df_f.copy()
    d['LugarLimpio'] = d['LugarProcedencia'].fillna('Indeterminado')
    conteo = d['LugarLimpio'].value_counts().reset_index()
    conteo.columns = ['Lugar', 'Expedientes']
 
    def coords(lugar):
        c = COORDENADAS.get(str(lugar).strip())
        return (c[0], c[1]) if c else (None, None)
 
    res = conteo['Lugar'].apply(coords)
    conteo['lat'] = res.apply(lambda x: x[0])
    conteo['lon'] = res.apply(lambda x: x[1])
    conteo = conteo[conteo['lat'].notna() & conteo['lon'].notna()]
 
    if conteo.empty:
        return None
 
    conteo['Tipo'] = conteo['Lugar'].apply(
        lambda x: 'Guanajuato' if x in MUNICIPIOS_GTO else 'Otro Estado'
    )
 
    gj_gto     = obtener_geojson_guanajuato()
    lats_gto, lons_gto = extraer_lats_lons(gj_gto)
 
    fig = go.Figure()
    fig.add_trace(go.Scattermapbox(
        lat=lats_gto, lon=lons_gto, mode='lines',
        fill='toself', fillcolor='rgba(0,0,255,0.15)',
        line=dict(color='blue', width=2),
        name='Guanajuato', hoverinfo='skip'
    ))
 
    scatter = px.scatter_mapbox(
        conteo, lat='lat', lon='lon',
        size='Expedientes', color='Tipo',
        hover_name='Lugar', hover_data={'Expedientes': True, 'Tipo': False},
        size_max=30,
        color_discrete_map={'Guanajuato': 'red', 'Otro Estado': 'blue'}
    )
    for trace in scatter.data:
        fig.add_trace(trace)
 
    fig.update_layout(
        mapbox_style="open-street-map",
        mapbox=dict(center={"lat": 21.0, "lon": -101.0}, zoom=6),
        margin={"r": 0, "t": 40, "l": 0, "b": 0},
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        title='🗺️ Distribución Geográfica de Expedientes',
        coloraxis_showscale=False
    )
    return fig