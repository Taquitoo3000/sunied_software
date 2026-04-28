import joblib
import pandas as pd
from pathlib import Path
from datetime import datetime

# ─── CONFIGURACIÓN ───────────────────────────────────────────────────────────
BASE_DIR = Path(__file__).parent.parent.parent
RUTA = BASE_DIR / "components" / "models"
RUTA_MODELO = RUTA / "modelo_recomendaciones.pkl"
RUTA_SCALER = RUTA / "scaler_recomendaciones.pkl"
RUTA_PROMEDIOS = RUTA / "target_encoding_promedios.pkl"
RUTA_COLUMNAS = RUTA / "columnas_modelo.pkl"
def oraculo_reporte(conn):
    # ─── 2. CARGAR DATOS NUEVOS ───────────────────────────────────────────────────
    df_exp = pd.read_sql("SELECT * FROM Expediente WHERE F_Conclusion IS NULL", conn)
    df_quejas = pd.read_sql("SELECT * FROM Quejas", conn)
    df_motivos = pd.read_sql("SELECT * FROM Quejas_Motivos", conn)

    # ─── 3. PREPROCESAMIENTO ─────────────────────────────────────────────────────
    def safe_mode(x):
        m = x.mode()
        return m.iloc[0] if len(m) > 0 else None

    # Agregar info de quejas
    df_quejas_agg = df_quejas.groupby('Expediente').agg(
        num_autoridades=('DireccionMunicipal', 'nunique'),
        num_hechos=('Hecho', 'nunique'),
        num_dependencias=('Dependencia', 'nunique'),
        dependencia_principal=('Dependencia', safe_mode),
        municipio=('Municipio', safe_mode),
    ).reset_index()

    df_motivos_agg = df_motivos.groupby('Expediente').agg(
        num_motivos=('Motivo', 'nunique'),
    ).reset_index()

    df = df_exp.merge(df_quejas_agg, on='Expediente', how='left')
    df = df.merge(df_motivos_agg, on='Expediente', how='left')

    # Seleccionar features
    features = ['SubProcu', 'LugarProcedencia', 'Recepcion', 'MujerAgraviada',
                'num_autoridades', 'num_hechos', 'num_dependencias',
                'dependencia_principal', 'municipio', 'num_motivos']

    df_pred = df[['Expediente'] + features].copy()

    # Imputar nulos
    for col in ['LugarProcedencia', 'dependencia_principal', 'municipio', 'Recepcion']:
        df_pred[col] = df_pred[col].fillna('Desconocido')
    for col in ['num_autoridades', 'num_hechos', 'num_dependencias', 'num_motivos']:
        df_pred[col] = df_pred[col].fillna(df_pred[col].median())

    # Normalizar Recepcion
    df_pred['Recepcion'] = df_pred['Recepcion'].str.strip().str.lower()
    df_pred['Recepcion'] = df_pred['Recepcion'].replace({'email': 'correo electrónico', 'fax': 'fax'})

    # Convertir MujerAgraviada a int
    df_pred['MujerAgraviada'] = df_pred['MujerAgraviada'].astype(int)

    # One-Hot Encoding
    df_pred = pd.get_dummies(df_pred, columns=['SubProcu', 'Recepcion'], drop_first=True)

    # Target Encoding con promedios del modelo original
    # Cargar promedios guardados
    promedios = joblib.load(f'{RUTA_PROMEDIOS}')
    for col in ['dependencia_principal', 'municipio', 'LugarProcedencia']:
        media_global = promedios['media_global']
        df_pred[col] = df_pred[col].map(promedios[col]).fillna(media_global)

    # ─── 4. ALINEAR COLUMNAS CON EL MODELO ───────────────────────────────────────
    # Cargar columnas del modelo entrenado
    columnas_modelo = joblib.load(f'{RUTA_COLUMNAS}')

    # Agregar columnas faltantes con 0
    for col in columnas_modelo:
        if col not in df_pred.columns:
            df_pred[col] = 0

    # Mantener solo las columnas del modelo en el mismo orden
    X_nuevo = df_pred[columnas_modelo]

    # ─── 5. PREDECIR ─────────────────────────────────────────────────────────────
    rf = joblib.load(RUTA_MODELO)
    scaler = joblib.load(RUTA_SCALER)

    X_scaled = scaler.transform(X_nuevo)
    probabilidades = rf.predict_proba(X_scaled)[:, 1]
    predicciones = rf.predict(X_scaled)

    # ─── 6. GENERAR REPORTE ───────────────────────────────────────────────────────
    df_reporte = df[['Expediente']].copy()

    df_reporte['probabilidad'] = (probabilidades * 100).round(1)
    df_reporte['prediccion'] = predicciones
    df_reporte['prediccion'] = df_reporte['prediccion'].map({1: 'Recomendación', 0: 'No Recomendación'})
    df_reporte['riesgo'] = pd.cut(probabilidades,
                                bins=[0, 0.3, 0.6, 1.0],
                                labels=['Bajo', 'Medio', 'Alto'])

    df_reporte = df_reporte.sort_values('probabilidad', ascending=False)

    return df_reporte