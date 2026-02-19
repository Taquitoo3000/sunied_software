import pandas as pd
import numpy as np
import pyodbc
import re
from datetime import datetime
from docxtpl import DocxTemplate
import os
from pathlib import Path

# Cambiar al directorio del script
os.chdir(Path(__file__).parent)

año = 2026
auth_incon = 41
hecho_incon = 114
plantilla = "semanal_plantilla.docx"
MESES_ROMANOS = {
    1: "I", 2: "II", 3: "III", 4: "IV", 5: "V", 6: "VI",
    7: "VII", 8: "VIII", 9: "IX", 10: "X", 11: "XI", 12: "XII"
}
now = datetime.now()
fecha = f"{now.day:02d}/{MESES_ROMANOS[now.month]}/{now.year}"

print("UPLOADING ACCESS...")
archivo_access = 'D:/concentrado 2000-2026.mdb'
conn_str = (
    r'DRIVER={Microsoft Access Driver (*.mdb, *.accdb)};'
    r'DBQ=' + archivo_access + ';'
)
conn = pyodbc.connect(conn_str)
quejas = pd.read_sql("SELECT * FROM [Quejas]", conn)
expediente = pd.read_sql("SELECT * FROM [Expediente]", conn)
recomendaciones = pd.read_sql("SELECT * FROM [Recomendaciones]", conn)
norecomendaciones = pd.read_sql("SELECT * FROM [NoRecomendaciones]", conn)
conn.close()
print("LOADED ACCESS")

# Merge Quejas and Expediente
df = pd.merge(
    quejas,
    expediente,
    on='Expediente',
    how='inner',
    suffixes=('', '_expediente')
)
df = df[df['Expediente'].str.contains(f'/{año}', na=False)]
df['DireccionMunicipal'] = df['DireccionMunicipal'].str.replace(
    'Dirección de Tránsito Municipal', 
    'Dependencia Municipal de Seguridad Pública', 
    case=False, 
    regex=True
)
df = df.sort_values(['FechaInicio', 'Expediente'])
df = df.reset_index(drop=True)

# Drop duplicates with unique Expediente
columnas = [
    'Expediente', 
    'SubProcu', 
    'FechaInicio', 
    'LugarProcedencia', 
    'Recepcion', 
    'Conclusión', 
    'F_Conclusion', 
    'Organismo emisor', 
    'Alias_Conclusión', 
    'Alias_expediente', 
    'GrupoVulnerable_expediente'
]
df2 = df[columnas].drop_duplicates()

# VERIFICAR ESTRUCTURA
col_direccion = 'DireccionMunicipal'
col_dependencia = 'Dependencia'
col_municipio = 'Municipio'
pd.set_option('display.max_colwidth', 30)
print("=" * 60)
print("DATASET: Ficha-001-Expedientes (df)") 
print(f"Dimensiones: {df.shape[0]} filas x {df.shape[1]} columnas")
print("=" * 60)
print("DATASET: Ficha-001-Expedientes2 (df2)")
print(f"Dimensiones: {df2.shape[0]} filas x {df2.shape[1]} columnas")

conteo = df2['Recepcion'].value_counts()
conteo = conteo.get('Oficiosa', 0)
iniciados = df2.shape[0]
oficiosos = conteo
print ("="*35)
print (f"Expedientes Iniciados en {año}: {iniciados}")
print (f"Expedientes Oficiosos en {año}: {oficiosos}")
print ("="*35)

# Subprocuradurías
print("Subprocuradurías")
conteo = df2['SubProcu'].value_counts().head(10)
print(conteo.to_string())
print("=" * 60)
subs_df = conteo.reset_index()
subs_df.columns = ['nombre', 'conteo']
tabla_subs = [
    {"nombre": str(idx), "conteo": str(val)}
    for idx, val in zip(subs_df.index, subs_df.iloc[:, 0])
]

# Autoridades
conteo = df[['Expediente', 'DireccionMunicipal', 'Municipio']].drop_duplicates()
conteo = conteo[conteo['Municipio'].str.lower() != 'indeterminado']
conteo = conteo.dropna(subset=['Municipio'])
conteo = conteo['DireccionMunicipal'].value_counts().head(7)
conteo = conteo.sort_values(ascending=False)
print("Autoridades Más Señaladas")
print(conteo.to_string())
print("=" * 60)
autoridades_df = conteo.reset_index()
autoridades_df.columns = ['nombre', 'conteo']
tabla_autoridades = [
    {"nombre": str(row['nombre']), "conteo": str(row['conteo'])}
    for _, row in autoridades_df.iterrows()
]

# Municipios con más señalamientos
municipio = df.groupby(['Expediente', 'DireccionMunicipal', 'Municipio'])['Dependencia'].count().reset_index(name='CuentaDeDependencia')
municipio = municipio[~municipio['Municipio'].str.startswith('indet', na=False)]
municipio = municipio.dropna(subset=['Municipio'])
municipio = municipio.sort_values('CuentaDeDependencia', ascending=False)
municipio = municipio['Municipio'].value_counts().reset_index()
municipio.columns = ['Municipio', 'CuentaDeMunicipio']
exclusion = ['Estatal', 'Federal', 'Indeterminado']
municipio = municipio[
    (~municipio['Municipio'].isin(exclusion)) &
    (~municipio['Municipio'].str.startswith('autoridad', na=False))
].head(7)
tabla_municipios = [
    {"nombre": str(row['Municipio']), "conteo": str(row['CuentaDeMunicipio'])}
    for _, row in municipio.iterrows()
]

# Autoridades Municipales
conteo = df[['Expediente', 'DireccionMunicipal', 'Municipio']].drop_duplicates()
conteo = conteo[conteo['Municipio'].str.lower() != 'indeterminado']
conteo = conteo.dropna(subset=['Municipio'])
conteo = conteo[
    (conteo[col_municipio] != 'Estatal') & 
    (conteo[col_municipio] != 'Federal') & 
    ~conteo[col_municipio].str.startswith('autoridad', na=False) &
    ~conteo[col_municipio].str.startswith('Indet', na=False) &
    ~conteo[col_municipio].str.startswith('null', na=False) &
    conteo[col_municipio].notna()
]
conteo = conteo['DireccionMunicipal'].value_counts().head(7).reset_index()
conteo.columns = ['nombre', 'conteo']
tabla_autoridades_municipales = [
    {"nombre": str(row['nombre']), "conteo": str(row['conteo'])}
    for _, row in conteo.iterrows()
]

# Autoridades Federales
conteo = df[['Expediente', 'DireccionMunicipal', 'Municipio']].drop_duplicates()
conteo = conteo[conteo['Municipio'].str.lower() != 'indeterminado']
conteo = conteo.dropna(subset=['Municipio'])
conteo = conteo[conteo['Municipio'] == 'Federal']
conteo = conteo['DireccionMunicipal'].value_counts().head(8).reset_index()
conteo.columns = ['nombre', 'conteo']
tabla_autoridades_federales = [
    {"nombre": str(row['nombre']), "conteo": str(row['conteo'])}
    for _, row in conteo.iterrows()
]

# Hechos en Quejas
conteo = df[['Expediente','Hecho']].sort_values('Expediente').drop_duplicates()
conteo = conteo['Hecho'].str.lower().value_counts().head(8).reset_index()
conteo.columns = ['nombre', 'conteo']
tabla_hechos = [
    {"nombre": str(row['nombre']), "conteo": str(row['conteo'])}
    for _, row in conteo.iterrows()
]

# Conclusiones
df_filtrado = expediente.copy()
filtro_indeterminado = df_filtrado['Conclusión'] != "INDETERMINADO"
filtro_no_nulos = df_filtrado['Conclusión'].notna()
fecha_inicio = pd.to_datetime(f'{año-1}-12-31')
filtro_fechas = (df_filtrado['F_Conclusion'] > fecha_inicio)
df_filtrado = df_filtrado[filtro_indeterminado & filtro_no_nulos & filtro_fechas]
salidas = df_filtrado['Conclusión'].value_counts().sum()
df_filtrado = expediente.copy()
mapeo_categorias = {
    # No Admisión
    'No admisión por desistimiento': 'No Admisión',
    'No admisión por extemporaneidad': 'No Admisión',
    'No admisión por falta de materia': 'No Admisión',
    'No admisión por falta de materia (desinterés)': 'No Admisión',
    'No admisión por tratarse de asunto entre particulares': 'No Admisión',

    # Incompetencia
    'No admisión por incompetencia': 'Incompetencia',
    'No admisión por incompetencia (asunto jurisdiccional)': 'Incompetencia',
    'No admisión por incompetencia asunto jurisdiccional (remitido al Consejo del Poder Judicial)': 'Incompetencia',
    'No admisión por incompetencia, remitido a la CNDH': 'Incompetencia',
    'No admisión por incompetencia, remitido a otra autoridad': 'Incompetencia',
    
    # Sobreseimiento por conciliación
    'Sobreseimiento por solución en el trámite (conciliación)': 'Sobreseimiento por conciliación',
    'Sobreseimiento por solución en el trámite': 'Sobreseimiento por conciliación',
    
    # Sobreseimiento por falta de materia
    'Sobreseimiento por falta de materia': 'Sobreseimiento por falta de materia',
    'Sobreseimiento por falta de materia (desinterés)': 'Sobreseimiento por falta de materia',
    
    # Resolución de fondo
    'Recomendación': 'Resolución de fondo',
    'No Recomendación': 'Resolución de fondo',
    
    # Acumulación
    'Sobreseimiento por acumulación': 'Acumulación',
    
    # Sobreseimiento por desistimiento
    'Sobreseimiento por desistimiento': 'Sobreseimiento por desistimiento',
}
filtro_indeterminado = df_filtrado['Alias_Conclusión'] != "INDETERMINADO"
filtro_no_nulos = df_filtrado['Alias_Conclusión'].notna()
fecha_inicio = pd.to_datetime(f'{año-1}-12-31')
filtro_fechas = (df_filtrado['F_Conclusion'] > fecha_inicio)
df_filtrado = df_filtrado[filtro_indeterminado & filtro_no_nulos & filtro_fechas]
conclusiones = df_filtrado['Alias_Conclusión'].replace(mapeo_categorias).value_counts().reset_index()
conclusiones.columns = ['nombre', 'conteo']
tabla_salidas = [
    {"nombre": str(row['nombre']), "conteo": str(row['conteo'])}
    for _, row in conclusiones.iterrows()
]

# Resoluciones
recomendaciones['FechaRecom'] = pd.to_datetime(recomendaciones['FechaRecom'], errors='coerce')
recom = recomendaciones[recomendaciones['FechaRecom'].dt.year == año]
recom = recom[~recom['Observaciones'].str.contains('acumula', case=False, na=False)]
recom2 = recom[['Expediente', 'FechaRecom']].drop_duplicates()
total_recom = int(recom.shape[0])
norecomendaciones['Fecha_NR'] = pd.to_datetime(norecomendaciones['Fecha_NR'], errors='coerce')
norec = norecomendaciones[norecomendaciones['Fecha_NR'].dt.year == año]
norec = norec[~norec['Observaciones'].str.contains('acumula', case=False, na=False)]
norec2 = norec.drop_duplicates(subset=['Expediente', 'Fecha_NR'], keep='first')
total_norec = int(norec2.shape[0])
resoluciones = total_recom + total_norec

# Autoridades en Recomendaciones (sin acumulados)
recom = recomendaciones[recomendaciones['FechaRecom'].dt.year == año]
recom = recom[~recom['Observaciones'].str.contains('acumula', case=False, na=False)]
recom = recom[['Expediente', 'FechaRecom', 'Autoridad']].drop_duplicates()
cuenta=recom['Autoridad'].value_counts().head(7).reset_index()
cuenta.columns = ['nombre', 'conteo']
tabla_recom_autoridades = [
    {"nombre": str(row['nombre']), "conteo": str(row['conteo'])}
    for _, row in cuenta.iterrows()
]

# Hechos en Recomendaciones (sin acumulados)
recom = recomendaciones[recomendaciones['FechaRecom'].dt.year == año].copy()
recom = recom[~recom['Observaciones'].str.contains('acumula', case=False, na=False)]
mapeo_recom = pd.read_excel('mapeo_hechos_recomendaciones.xlsx') # mapeo para corregir hechos en recomendaciones
recom_dict = dict(zip(mapeo_recom['Causa'].str.lower().str.strip(), mapeo_recom['Causa Corregida']))
# Limpiar y normalizar
recom['Causa_Limpia'] = recom['Causa'].str.lower().str.strip().fillna('')
recom['Causa Corregida'] = recom['Causa_Limpia'].replace(recom_dict)
recom['Causa Corregida'] = recom['Causa Corregida'].fillna(recom['Causa_Limpia'])
def separar_hechos(texto):
    if pd.isna(texto):
        return []
    # Separar por " | " o "|"
    texto_str = str(texto)
    separadores = [' | ', '|']
    for sep in separadores:
        if sep in texto_str:
            return [hecho.strip() for hecho in texto_str.split(sep) if hecho.strip()]
    # Si no encuentra separadores, devolver como lista de un elemento
    return [texto_str.strip()] if texto_str.strip() else []
recom['Hechos_Separados'] = recom['Causa Corregida'].apply(separar_hechos)
# Calcular estadísticas de hechos múltiples
recom['Cantidad_Hechos'] = recom['Hechos_Separados'].apply(len)
multiples = recom[recom['Cantidad_Hechos'] > 1]
print(f"Registros Totales: {len(recom)}")
print(f"Registros con hechos múltiples: {len(multiples)}")
print(f"Hechos totales (separados): {recom['Cantidad_Hechos'].sum()}")
# 5. CONTAR HECHOS INDIVIDUALMENTE (con expansión)
# Crear lista expandida de todos los hechos
todos_los_hechos = []
for idx, row in recom.iterrows():
    for hecho in row['Hechos_Separados']:
        todos_los_hechos.append({
            'Expediente': row['Expediente'],
            'Hecho': hecho,
        })
# Convertir a DataFrame
df_hechos_expandidos = pd.DataFrame(todos_los_hechos)
# 6. AGRUPAR Y CONTAR
resultado = (
    df_hechos_expandidos
    .groupby('Hecho')
    .agg({
        'Expediente': 'count',
    })
    .rename(columns={'Expediente': 'CuentaDeHecho'})
    .sort_values('CuentaDeHecho', ascending=False)
    .reset_index()
    .rename(columns={'Hecho': 'Causa Corregida'})
)
resultado.head(7).reset_index()
tabla_recom_hechos = [
    {"nombre": str(row['Causa Corregida']), "conteo": str(row['CuentaDeHecho'])}
    for _, row in resultado.head(7).iterrows()
]

# Autoridades Estatales
conteo = df[['Expediente', 'DireccionMunicipal', 'Municipio']].drop_duplicates()
conteo = conteo[conteo['Municipio'].str.lower() != 'indeterminado']
conteo = conteo.dropna(subset=['Municipio'])
conteo = conteo[conteo['Municipio'] == 'Estatal']
conteo = conteo[conteo['DireccionMunicipal'].str.contains('- per',na=False, case=False)]
conteo = conteo['DireccionMunicipal'].value_counts().reset_index().head(6)
conteo.columns = ['nombre', 'conteo']
tabla_autoridades_estatales = [
    {"nombre": str(row['nombre']), "conteo": str(row['conteo'])}
    for _, row in conteo.iterrows()
]

# Municipios con más señalamientos a DSP
conteo = df[df['Dependencia'].str.upper().str.startswith('DSP', na=False)][['Expediente', 'Municipio', 'DireccionMunicipal']].drop_duplicates()
conteo=conteo.groupby('Municipio').size().reset_index(name='CuentaDeMunicipio')
conteo = conteo[~conteo['Municipio'].str.startswith('indet', na=False)]
conteo = conteo.dropna(subset=['Municipio'])
conteo = conteo.sort_values('CuentaDeMunicipio', ascending=False)
conteo = conteo[~conteo['Municipio'].isin(exclusion)].head(7)
tabla_municipios_dsp = [
    {"nombre": str(row['Municipio']), "conteo": str(row['CuentaDeMunicipio'])}
    for _, row in conteo.iterrows()
]

# Oficiosas
conteo = df[df['Recepcion'].str.contains('Oficiosa', case=False, na=False)][['Expediente', 'FechaInicio', 'DireccionMunicipal', 'F_Conclusion']].drop_duplicates().sort_values('FechaInicio')
conteo = conteo[['Expediente', 'FechaInicio', 'DireccionMunicipal', 'F_Conclusion']].drop_duplicates().sort_values('FechaInicio')
conteo.columns = ['Expediente', 'FechaInicio','DireccionMunicipal','F_Conclusion']
tabla_oficiosas = [
    {"expediente": str(row['Expediente']),
     "fecha": pd.to_datetime(row['FechaInicio']).strftime('%d/%m/%Y') if pd.notna(row['FechaInicio']) else "",
     "autoridad": str(row['DireccionMunicipal']),
     "f_conclusion": pd.to_datetime(row['F_Conclusion']).strftime('%d/%m/%Y') if pd.notna(row['F_Conclusion']) else ""}
    for _, row in conteo.iterrows()
]

# Periodistas
conteo = df[df['GrupoVulnerable_expediente'].str.contains('10', case=False, na=False)]['Expediente'].drop_duplicates()
period = conteo.shape[0]
if period == 0:
    period = "0"
conteo = df[df['GrupoVulnerable_expediente'].str.contains('10', case=False, na=False)][['Expediente', 'FechaInicio', 'DireccionMunicipal', 'F_Conclusion']].drop_duplicates().sort_values('FechaInicio')
conteo = conteo[['Expediente', 'FechaInicio', 'DireccionMunicipal', 'F_Conclusion']].drop_duplicates().sort_values('FechaInicio')
conteo.columns = ['Expediente', 'FechaInicio','DireccionMunicipal','F_Conclusion']
tabla_periodistas = [
    {"expediente": str(row['Expediente']),
     "fecha": pd.to_datetime(row['FechaInicio']).strftime('%d/%m/%Y') if pd.notna(row['FechaInicio']) else "",
     "autoridad": str(row['DireccionMunicipal']),
     "f_conclusion": pd.to_datetime(row['F_Conclusion']).strftime('%d/%m/%Y') if pd.notna(row['F_Conclusion']) else ""}
    for _, row in conteo.iterrows()
]

# Defensores de Derechos Humanos
conteo = df[df['GrupoVulnerable_expediente'].str.contains('11', case=False, na=False)]['Expediente'].drop_duplicates()
defensor = conteo.shape[0]
if defensor == 0:
    defensor = "0"
conteo = df[df['GrupoVulnerable_expediente'].str.contains('11', case=False, na=False)]
conteo = conteo[['Expediente', 'FechaInicio', 'DireccionMunicipal', 'F_Conclusion']].drop_duplicates().sort_values('FechaInicio')
conteo.columns = ['Expediente', 'FechaInicio','DireccionMunicipal','F_Conclusion']
tabla_defensores = [
    {"expediente": str(row['Expediente']), "fecha": str(row['FechaInicio']), "autoridad": str(row['DireccionMunicipal']), "f_conclusion": str(row['F_Conclusion'])}
    for _, row in conteo.iterrows()
]

context = {
    # Metadatos
    "año": año,
    "date": fecha,
    "auth_incon": auth_incon,
    "hecho_incon": hecho_incon,
    "period": period,
    "defen": defensor,

    # Cifras generales
    "iniciados": iniciados,
    "oficiosos": oficiosos,
    "salidas": salidas,

    # Resoluciones
    "resoluciones": resoluciones,
    "recom": total_recom,
    "norec": total_norec,

    # Tablas
    "tabla_subs": tabla_subs,
    "tabla_autoridades": tabla_autoridades,
    "tabla_municipios": tabla_municipios,
    "tabla_autoridades_municipales": tabla_autoridades_municipales,
    "tabla_autoridades_federales": tabla_autoridades_federales,
    "tabla_hechos": tabla_hechos,
    "tabla_salidas": tabla_salidas,
    "tabla_recom_autoridades": tabla_recom_autoridades,
    "tabla_recom_hechos": tabla_recom_hechos,
    "tabla_autoridades_estatales": tabla_autoridades_estatales,
    "tabla_municipios_dsp": tabla_municipios_dsp,
    "tabla_oficiosas": tabla_oficiosas,
    "tabla_periodistas": tabla_periodistas
}

print(f"Generando reporte semanal {fecha}...")
doc = DocxTemplate(plantilla)
doc.render(context)
nombre_archivo = f'semanal_{datetime.now().strftime("%d-%m-%y")}.docx'
doc.save(f'{nombre_archivo}')
print(f"✓ Guardado: {nombre_archivo}")