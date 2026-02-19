import pandas as pd
import streamlit as st

def buscar_expedientes(_conn, numero_expediente=None):
    try:
        query = """
            SELECT 
                q.Expediente,
                q.FechaInicio,
                e.Conclusión,
                e.F_Conclusion,
                q.Municipio,
                q.Hecho,
                q.Dependencia
            FROM Quejas AS q
            INNER JOIN Expediente AS e ON q.Expediente = e.Expediente
        """
        
        params = []
        if numero_expediente:
            query += " WHERE q.Expediente LIKE ?"
            params.append(f"%{numero_expediente}%")
        
        query += " ORDER BY q.Expediente, q.FechaInicio DESC"

        df = pd.read_sql(query, _conn, params=params)

        if 'FechaInicio' in df.columns:
            df['FechaInicio'] = pd.to_datetime(df['FechaInicio']).dt.strftime('%d/%m/%Y')
        if 'F_Conclusion' in df.columns:
            df['F_Conclusion'] = pd.to_datetime(df['F_Conclusion']).dt.strftime('%d/%m/%Y')
        
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
        """
        
        params = []
        if nombre_expediente:
            query += " WHERE qa.Nombre LIKE ?"
            params.append(f"%{nombre_expediente}%")
        
        query += " ORDER BY q.Expediente, q.FechaInicio DESC"

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
                q.DireccionMunicipal
            FROM (Quejas AS q
                INNER JOIN Expediente AS e ON q.Expediente = e.Expediente)
        """
        
        params = []
        if nombre_autoridad:
            query += " WHERE q.DireccionMunicipal LIKE ?"
            params.append(f"%{nombre_autoridad}%")
        
        query += " ORDER BY q.Expediente, q.FechaInicio DESC"

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
            WHERE Expediente = ?
            ORDER BY FechaInicio DESC
        """
        return pd.read_sql(query, _conn, params=[expediente])
    except Exception as e:
        st.error(f"Error cargando detalles: {e}")
        return pd.DataFrame()