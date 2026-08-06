"""
Índice de prioridad de expedientes (triage de casos activos)
==============================================================

Calcula un puntaje 0-100 por expediente combinando:
  - Grupo vulnerable                          (peso 30%)
  - Tipo de violencia (texto)                 (peso 25%)
  - Hecho Violatorio                          (peso 25%)
  - Autoridad señalada (Dependencia+Alias)    (peso 10%)
  - Lugar de procedencia (concentración)      (peso 10%)

Uso:
    import pandas as pd
    from indice_prioridad import calcular_indice_prioridad

    df = pd.read_sql(query, conn)          # tu consulta original
    df = calcular_indice_prioridad(df)
    df.sort_values("prioridad_score", ascending=False).head(20)

El script está diseñado para que ajustes los diccionarios de pesos
y palabras clave sin tocar la lógica de cálculo.
"""

import re
import unicodedata
import pandas as pd
import numpy as np

# ---------------------------------------------------------------------------
# 1. CONFIGURACIÓN — AJUSTA AQUÍ SEGÚN TU CRITERIO INSTITUCIONAL
# ---------------------------------------------------------------------------

PESOS = {
    "grupo_vulnerable": 0.30,
    "tipo_violencia": 0.25,
    "hecho": 0.25,
    "autoridad": 0.10,
    "lugar": 0.10,
}

# --- Grupo vulnerable: score 0-10 (10 = máxima prioridad) ---
# Usa minúsculas sin acentos; el matching es "contains", no exacto.
SCORES_GRUPO_VULNERABLE = {
    "01": 8,   # Personas con Discapacidad
    "02": 7,   # Adultos mayores
    "03": 10,  # Menores
    "04": 5,   # Estudiantes
    "05": 7,   # Población Migrante
    "06": 8,   # Mujeres
    "07": 7,   # Víctimas de Delitos
    "08": 10,  # Presuntas personas desaparecidas
    "09": 8,   # Personas Privadas de su Libertad
    "10": 8,   # Periodistas
    "11": 8,   # Defensores civiles de derechos humanos (incl. Colectivos)
    "12": 5,   # Pob. Afectada Derechos Laborales/Ambientales/Económicos/Culturales
    "13": 7,   # Población Indígena
    "14": 6,   # Minorías nacionales o religiosas
    "15": 7,   # OSIG
    "16": 7,   # Personas en Situación de Calle
    "17": 10,  # Presuntas víctimas de trata de personas
    "18": 10,  # Presuntas víctimas de Tortura
    "19": 9,   # Presuntas víctimas de Tratos crueles, inhumanos o degradantes
    "20": 6,   # Población Afromexicana
    "21": 7,   # Personas con VIH
}
SCORE_GRUPO_DEFAULT = 4  # si no matchea nada / "ninguno" / vacío

# --- Ámbito / modalidad de violencia: score 0-10 ---
SCORES_TIPO_VIOLENCIA = {
    "sexual": 10,
    "feminicid": 10,
    "obstetric": 9,
    "institucional": 8,
    "fisica": 8,
    "familiar": 7,
    "digital": 6, "mediatic": 6,
    "psicologic": 6, "emocional": 6,
    "economic": 5, "patrimonial": 5,
    "laboral": 5,
    "comunitaria": 5,
    "escolar": 6,
    "politica": 6,
}
SCORE_TIPO_DEFAULT = 4

# --- Hecho: palabras clave de gravedad, score 0-10 ---
SCORES_HECHO = {
    # 01 — Derecho a la vida
    "01.1": 10,  # Desaparición forzada
    "01.2": 10,  # Ejecución extrajudicial, arbitraria o sumaria
    "01.3": 10,  # Genocidio
    "01.4": 9,   # Omisión en la investigación de violaciones al derecho a la vida
    "01.5": 9,   # Otra violación al derecho a la vida
    # 02 — Integridad y seguridad personal
    "02.1": 10,  # Tortura
    "02.2": 9,   # Tratos crueles, inhumanos o degradantes
    "02.3": 9,   # Omisión protección esclavitud/servidumbre/trata de esclavos
    "02.4": 10,  # Omisión protección trata de personas / explotación sexual
    "02.5": 8,   # Omisión de brindar medidas efectivas de protección
    "02.6": 8,   # Otra violación integridad y seguridad
    # 03 — Igualdad y no discriminación
    "03.1": 5, "03.2": 6, "03.3": 6, "03.4": 6, "03.5": 5,
    "03.6": 6, "03.7": 6, "03.8": 6, "03.9": 5,
    # 04 — Seguridad jurídica y libertad personal
    "04.01": 5, "04.02": 5, "04.03": 4, "04.04": 6, "04.05": 7,
    "04.06": 6, "04.07": 6, "04.08": 5, "04.09": 6, "04.10": 5,
    "04.11": 8,  # Detención arbitraria
    "04.12": 8,  # Incomunicación o aislamiento
    "04.13": 6, "04.14": 5, "04.15": 5,
    "04.16": 4, "04.17": 6,
    "04.18": 7,  # Prolongación de plazos de prisión preventiva
    "04.19": 8,  # Retención ilegal
    "04.20": 6, "04.21": 6, "04.22": 6, "04.23": 4, "04.24": 4, "04.25": 5,
    # 05 — Derechos civiles / libertad de circulación
    "05.01": 6, "05.02": 5, "05.03": 4, "05.04": 5, "05.05": 5,
    "05.06": 8,  # Desplazamiento forzado de personas
    "05.07": 5, "05.08": 5, "05.09": 4, "05.10": 4, "05.11": 5,
    "05.12": 4, "05.13": 4,
    # 06 — Derechos políticos
    "06.1": 5, "06.2": 4, "06.3": 4, "06.4": 4,
    # 07 — Derechos económicos y sociales
    "07.1": 5, "07.2": 5, "07.3": 6, "07.4": 6, "07.5": 5, "07.6": 5,
    # 08 — Derechos laborales
    "08.1": 4, "08.2": 4, "08.3": 5, "08.4": 5, "08.5": 4,
    "08.6": 4, "08.7": 4, "08.8": 4, "08.9": 4,
    # 09 — Derecho a la salud
    "09.1": 8,  # Abandono del/la paciente
    "09.2": 8,  # Negligencia médica
    "09.3": 8,  # Omisión de prestación de atención médica
    "09.4": 7, "09.5": 6,
    "09.6": 7, "09.7": 6,
    # 10 — Salud sexual y reproductiva
    "10.1": 9,  # Esterilización forzada
    "10.2": 7, "10.3": 8, "10.4": 6, "10.5": 6,
    "10.6": 8,  # Transgresión a la libertad sexual
    "10.7": 6,
    # 11 — Educación y derechos culturales
    "11.1": 5, "11.2": 4, "11.3": 3, "11.4": 3, "11.5": 3, "11.6": 4,
    # 12 — Derechos de tercera generación
    "12.1": 3, "12.2": 2, "12.3": 3, "12.4": 3,
    # 13 — Derechos de las mujeres
    "13.1": 5, "13.2": 5,
    "13.3": 9,  # Omisión de protección contra violencia/maltrato físico/sexual
    "13.4": 6, "13.5": 5, "13.6": 6,
    # 14 — Derechos de niñas, niños y adolescentes
    "14.1": 9,  # Interés superior de la niñez
    "14.2": 8,
    "14.3": 9,  # Medidas de protección de niñas y niños
    "14.4": 9,  # Medidas de protección NNA migrantes no acompañados
    "14.5": 6, "14.6": 5, "14.7": 7,
    # 15 — Derechos de personas adultas mayores
    "15.1": 6, "15.2": 7,
    "15.3": 9,  # Derecho a vivir sin violencia y maltrato
    "15.4": 6,
    # 16 — Derechos de personas migrantes
    "16.1": 8,  # Principio de no devolución
    "16.2": 7,
    "16.3": 8,  # Deportación ilegal
    "16.4": 6,
    "16.5": 9,  # Omisión protección contra violencia/amenaza a migrantes
    "16.6": 5, "16.7": 6,
    # 17 — Derechos de personas con discapacidad
    "17.1": 8,  # Institucionalización forzada
    "17.2": 5, "17.3": 5, "17.4": 5,
    "17.5": 6, "17.6": 6,
    # 18 — Derechos de personas con VIH/Sida
    "18.1": 8,  # Detención/aislamiento/segregación por VIH
    "18.2": 7, "18.3": 7, "18.4": 6, "18.5": 5, "18.6": 6,
    # 19 — Derechos de periodistas y defensores de DDHH
    "19.1": 7, "19.2": 6, "19.3": 6, "19.4": 7, "19.5": 6, "19.6": 7,
    # 20 — Derechos de pueblos y personas indígenas
    "20.1": 6, "20.2": 6, "20.3": 5, "20.4": 6,
    # 21 — Derechos de personas privadas de su libertad
    "21.1": 7, "21.2": 6, "21.3": 5, "21.4": 6, "21.5": 6, "21.6": 6,
}
SCORE_HECHO_DEFAULT = 3

# --- Autoridad señalada (Dependencia / AliasDependencia): score 0-10 ---
# Autoridades con poder coercitivo/uso de la fuerza pesan más (riesgo de abuso de poder).
SCORES_AUTORIDAD = {
    "policia": 9, "seguridad publica": 9, "guardia nacional": 9,
    "ejercito": 9, "marina": 9, "sedena": 9, "semar": 9,
    "penitenciari": 9, "reinsercion social": 9, "cereso": 9, "centro de internamiento": 9,
    "ministerio publico": 8, "fiscalia": 8,
    "migracion": 7, "instituto nacional de migracion": 7,
    "dif": 6, "salud": 6, "hospital": 6,
    "educacion": 5, "escuela": 5,
    "transito": 6, "trafico": 6,
}
SCORE_AUTORIDAD_DEFAULT = 4


# ---------------------------------------------------------------------------
# 2. UTILIDADES
# ---------------------------------------------------------------------------

def _normalizar(texto):
    """minúsculas, sin acentos, sin espacios extra — para matching robusto."""
    if pd.isna(texto):
        return ""
    texto = str(texto).lower().strip()
    texto = unicodedata.normalize("NFKD", texto)
    texto = "".join(c for c in texto if not unicodedata.combining(c))
    texto = re.sub(r"\s+", " ", texto)
    return texto


def _score_por_keywords(texto, diccionario, default):
    """Devuelve el score MÁXIMO entre todas las keywords que matcheen en el texto."""
    texto_norm = _normalizar(texto)
    if not texto_norm:
        return default
    matches = [score for kw, score in diccionario.items() if kw in texto_norm]
    return max(matches) if matches else default


# ---------------------------------------------------------------------------
# 3. CÁLCULO DE CADA COMPONENTE
# ---------------------------------------------------------------------------

def score_grupo_vulnerable(df, col="GrupoVulnerable"):
    return df[col].apply(lambda x: _score_por_keywords(x, SCORES_GRUPO_VULNERABLE, SCORE_GRUPO_DEFAULT))


def score_tipo_violencia(df, col="Tipo de Violencia"):
    return df[col].apply(lambda x: _score_por_keywords(x, SCORES_TIPO_VIOLENCIA, SCORE_TIPO_DEFAULT))


def score_hecho(df, col="Hecho"):
    return df[col].apply(lambda x: _score_por_keywords(x, SCORES_HECHO, SCORE_HECHO_DEFAULT))


def score_autoridad(df, col_dep="Dependencia", col_alias="AliasDependencia"):
    combinado = df[col_dep].fillna("").astype(str) + " " + df[col_alias].fillna("").astype(str)
    return combinado.apply(lambda x: _score_por_keywords(x, SCORES_AUTORIDAD, SCORE_AUTORIDAD_DEFAULT))


def score_lugar_procedencia(df, col="LugarProcedencia"):
    """
    Score basado en la concentración de quejas por lugar dentro del propio
    dataset (proxy de 'zona caliente'): más quejas históricas en ese lugar
    -> score más alto, escalado 0-10 por percentil.
    """
    lugar_norm = df[col].apply(_normalizar)
    frecuencias = lugar_norm.value_counts()
    if frecuencias.empty:
        return pd.Series(5, index=df.index)  # fallback neutro
    percentiles = frecuencias.rank(pct=True)  # 0-1
    mapa_score = (percentiles * 10).round(1)
    return lugar_norm.map(mapa_score).fillna(5)


# ---------------------------------------------------------------------------
# 4. FUNCIÓN PRINCIPAL
# ---------------------------------------------------------------------------

def calcular_indice_prioridad(df, inplace=False):
    """
    Agrega columnas de score por factor + el score final ponderado (0-100)
    + una etiqueta categórica de prioridad.
    """
    out = df if inplace else df.copy()

    out["score_grupo_vulnerable"] = score_grupo_vulnerable(out)
    out["score_tipo_violencia"] = score_tipo_violencia(out)
    out["score_hecho"] = score_hecho(out)
    out["score_autoridad"] = score_autoridad(out)
    out["score_lugar"] = score_lugar_procedencia(out)

    # Ponderación -> escala 0-100
    out["prioridad_score"] = (
        out["score_grupo_vulnerable"] * PESOS["grupo_vulnerable"]
        + out["score_tipo_violencia"] * PESOS["tipo_violencia"]
        + out["score_hecho"] * PESOS["hecho"]
        + out["score_autoridad"] * PESOS["autoridad"]
        + out["score_lugar"] * PESOS["lugar"]
    ) * 10  # de escala 0-10 a 0-100

    out["prioridad_score"] = out["prioridad_score"].round(1)

    # Categorías de triage — ajusta los cortes a tu volumen de casos
    bins = [-1, 40, 60, 80, 100]
    labels = ["Baja", "Media", "Alta", "Urgente"]
    out["prioridad_nivel"] = pd.cut(out["prioridad_score"], bins=bins, labels=labels)

    return out