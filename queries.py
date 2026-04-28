import pandas as pd
import streamlit as st
from sqlalchemy import text

def busqueda_general(conn, texto):
    try:
        if not texto or not texto.strip():
            return pd.DataFrame()

        resultados = []
        tablas = ['Quejas', 'Expediente', 'Quejas_Motivos', 'Quejosos_Ampliado']

        for tabla in tablas:
            # Obtener columnas
            columnas_result = conn.execute(text(f"SHOW COLUMNS FROM `{tabla}`"))
            columnas = [row[0] for row in columnas_result]

            # Una query por tabla con OR
            condiciones = " OR ".join([f"`{col}` LIKE :p{i}" for i, col in enumerate(columnas)])
            params = {f"p{i}": f"%{texto}%" for i in range(len(columnas))}

            resultado = conn.execute(text(f"SELECT * FROM `{tabla}` WHERE {condiciones}"), params)
            filas = resultado.fetchall()

            if filas:
                col_names = list(resultado.keys())
                df = pd.DataFrame(filas, columns=col_names).drop_duplicates()
                df.insert(0, "_tabla", tabla)
                resultados.append(df)

        return pd.concat(resultados, ignore_index=True) if resultados else pd.DataFrame()

    except Exception as e:
        st.error(f"Error en búsqueda: {e}")
        return pd.DataFrame()

def buscar_expedientes(_conn, numero_expediente=None):
    try:
        if numero_expediente:
            query = """
                SELECT 
                    q.Expediente, q.FechaInicio, e.Conclusión, e.F_Conclusion,
                    q.Municipio, q.Hecho, q.DireccionMunicipal, q.Dependencia
                FROM Quejas AS q
                INNER JOIN Expediente AS e ON q.Expediente = e.Expediente
                WHERE q.Expediente LIKE %s
                ORDER BY q.Expediente, q.FechaInicio DESC
            """
            params = (f'%{numero_expediente}%',)
        else:
            query = """
                SELECT 
                    q.Expediente, q.FechaInicio, e.Conclusión, e.F_Conclusion,
                    q.Municipio, q.Hecho, q.DireccionMunicipal, q.Dependencia
                FROM Quejas AS q
                INNER JOIN Expediente AS e ON q.Expediente = e.Expediente
                ORDER BY q.Expediente, q.FechaInicio DESC
            """
            params = None
        df = pd.read_sql(query, _conn, params=params)

        df['FechaInicio'] = pd.to_datetime(df['FechaInicio'], errors='coerce')
        df['F_Conclusion'] = pd.to_datetime(df['F_Conclusion'], errors='coerce')

        return df
    except Exception as e:
        st.error(f"Error en búsqueda: {e}")
        return pd.DataFrame()  # DataFrame vacío en caso de error

def buscar_persona(_conn, nombre_expediente=None):
    try:
        query = """
            SELECT 
                qa.Nombre,
                q.Expediente,
                q.FechaInicio,
                e.Conclusión,
                e.F_Conclusion,
                q.Hecho,
                q.Dependencia
            FROM (Quejas AS q
                INNER JOIN Expediente AS e ON q.Expediente = e.Expediente)
                LEFT JOIN Quejosos_Ampliado AS qa ON q.Expediente = qa.Expediente
            WHERE qa.Nombre LIKE %(nombre)s
            ORDER BY q.Expediente, q.FechaInicio DESC
        """

        params = {'nombre': f'%{nombre_expediente}%'}
        df = pd.read_sql(query, _conn, params=params)

        if 'FechaInicio' in df.columns:
            df['FechaInicio'] = pd.to_datetime(df['FechaInicio']).dt.strftime('%d/%m/%Y')
        if 'F_Conclusion' in df.columns:
            df['F_Conclusion'] = pd.to_datetime(df['F_Conclusion']).dt.strftime('%d/%m/%Y')
        
        return df
    except Exception as e:
        st.error(f"Error en búsqueda: {e}")
        return pd.DataFrame()  # DataFrame vacío en caso de error

def buscar_autoridad(_conn, nombre_autoridad=None):
    try:
        query = """
            SELECT 
                q.Expediente,
                q.FechaInicio,
                e.Conclusión,
                e.F_Conclusion,
                q.Hecho,
                q.Autoridad,
                q.DireccionMunicipal
            FROM (Quejas AS q
                INNER JOIN Expediente AS e ON q.Expediente = e.Expediente)
            WHERE q.Autoridad LIKE %(autoridad)s
            ORDER BY q.Expediente, q.FechaInicio DESC
        """
        
        params = {'autoridad': f'%{nombre_autoridad}%'}
        df = pd.read_sql(query, _conn, params=params)

        if 'FechaInicio' in df.columns:
            df['FechaInicio'] = pd.to_datetime(df['FechaInicio']).dt.strftime('%d/%m/%Y')
        if 'F_Conclusion' in df.columns:
            df['F_Conclusion'] = pd.to_datetime(df['F_Conclusion']).dt.strftime('%d/%m/%Y')
        
        return df
    except Exception as e:
        st.error(f"Error en búsqueda: {e}")
        return pd.DataFrame()  # DataFrame vacío en caso de error

def ver_detalle_expediente(_conn, expediente):  # Agrega _conn
    try:
        query = """
            SELECT 
                *
            FROM Quejas
            WHERE Expediente = %(expediente)s
            ORDER BY FechaInicio DESC
        """
        return pd.read_sql(query, _conn, params={'expediente': expediente})
    except Exception as e:
        st.error(f"Error cargando detalles: {e}")
        return pd.DataFrame()
    
def busqueda_personalizada(_conn,name):
    try:
        file=name
        ruta_completa=rf"C:\Users\PRODHEG\Desktop\isael\sql_querys\{file}"
        encodings = ['utf-8', 'utf-8-sig', 'latin-1', 'cp1252', 'iso-8859-1']
        query = None
        for encoding in encodings:
            try:
                with open(ruta_completa, 'r', encoding=encoding) as f:
                    query = f.read()
                    break  # Si funciona, salir del loop
            except (UnicodeDecodeError, LookupError):
                continue
        #df = pd.read_sql_query(query, _conn)
        # Usar cursor directamente
        cursor = _conn.cursor()
        cursor.execute(query)
        
        # Obtener nombres de columnas
        columns = [column[0] for column in cursor.description]
        
        # Obtener datos
        data = cursor.fetchall()
        
        # Crear DataFrame manualmente
        df = pd.DataFrame.from_records(data, columns=columns)
        
        cursor.close()
        return df
    except Exception as e:
        st.error(f"Error en búsqueda: {e}")
        return pd.DataFrame()  # DataFrame vacío en caso de error