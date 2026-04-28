import joblib
import pandas as pd

RUTA_MODELO = r"C:\Users\PRODHEG\Desktop\isael\proyectos\machine_learning\prediccion_recom\modelo_recomendaciones.pkl"
RUTA_SCALER = r"C:\Users\PRODHEG\Desktop\isael\proyectos\machine_learning\prediccion_recom\scaler_recomendaciones.pkl"
RUTA_PROMEDIOS = r"C:\Users\PRODHEG\Desktop\isael\proyectos\machine_learning\prediccion_recom\target_encoding_promedios.pkl"
RUTA_COLUMNAS = r"C:\Users\PRODHEG\Desktop\isael\proyectos\machine_learning\prediccion_recom\columnas_modelo.pkl"
# Cargar modelo al iniciar
rf = joblib.load(RUTA_MODELO)
scaler = joblib.load(RUTA_SCALER)
promedios = joblib.load(RUTA_PROMEDIOS)
columnas_modelo = joblib.load(RUTA_COLUMNAS)

def get_expediente(numero: str,conn):
    df_exp = pd.read_sql("SELECT * FROM Expediente WHERE Expediente like %s", conn, params=('%' + numero + '%',))
    df_quejas = pd.read_sql("SELECT * FROM Quejas WHERE Expediente like %s", conn, params=('%' + numero + '%',))
    return df_exp, df_quejas

def preprocesar(df_exp, df_quejas):
    def safe_mode(x):
        m = x.mode()
        return m.iloc[0] if len(m) > 0 else None

    quejas_agg = df_quejas.groupby('Expediente').agg(
        num_autoridades=('DireccionMunicipal', 'nunique'),
        num_hechos=('Hecho', 'nunique'),
        num_dependencias=('Dependencia', 'nunique'),
        dependencia_principal=('Dependencia', safe_mode),
        municipio=('Municipio', safe_mode),
    ).reset_index()

    df = df_exp.merge(quejas_agg, on='Expediente', how='left')

    for col in ['LugarProcedencia', 'dependencia_principal', 'municipio', 'Recepcion']:
        df[col] = df[col].fillna('Desconocido')
    for col in ['num_autoridades', 'num_hechos', 'num_dependencias']:
        df[col] = df[col].fillna(0)

    df['Recepcion'] = df['Recepcion'].str.strip().str.lower()
    df['Recepcion'] = df['Recepcion'].replace({'email': 'correo electrónico', 'fax': 'fax'})
    df['MujerAgraviada'] = df['MujerAgraviada'].astype(int)

    df = pd.get_dummies(df, columns=['SubProcu', 'Recepcion'], drop_first=True)

    media_global = promedios['media_global']
    for col in ['dependencia_principal', 'municipio', 'LugarProcedencia']:
        df[col] = df[col].map(promedios[col]).fillna(media_global)

    for col in columnas_modelo:
        if col not in df.columns:
            df[col] = 0

    return df[columnas_modelo]

def predecir(numero_expediente: str,conn):
    try:
        df_exp, df_quejas = get_expediente(numero_expediente,conn)

        if df_exp.empty:
            return {"error": f"Expediente {numero_expediente} no encontrado"}

        X = preprocesar(df_exp, df_quejas)
        X_scaled = scaler.transform(X)

        probabilidad = rf.predict_proba(X_scaled)[0][1]
        prediccion = rf.predict(X_scaled)[0]

        if probabilidad >= 0.6:
            riesgo = "Alto"
        elif probabilidad >= 0.3:
            riesgo = "Medio"
        else:
            riesgo = "Bajo"

        return {
            "expediente": numero_expediente,
            "probabilidad_recomendacion": round(float(probabilidad) * 100, 1),
            "prediccion": "Recomendación" if prediccion == 1 else "No Recomendación",
            "riesgo": riesgo
        }

    except Exception as e:
        return {"error": str(e)}