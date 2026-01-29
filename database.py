import pyodbc
import streamlit as st
from datetime import datetime
import pandas as pd
import pymysql

@st.cache_resource
def get_connection():
    try:
        conn = pyodbc.connect(
            'DRIVER={ODBC Driver 17 for SQL Server};'
            f'SERVER={st.secrets["DB_SERVER"]};'
            f'DATABASE={st.secrets["DB_NAME"]};'
            'Trusted_Connection=yes;'
        )
        return conn
    except Exception as e:
        st.error(f"Error: {str(e)[:100]}")  # Mostrar solo parte del error
        return None
    
@st.cache_resource
def get_connection_access():
    try:
        archivo_access = 'D:/concentrado 2000-2026.mdb'
        conn_str = (
            r'DRIVER={Microsoft Access Driver (*.mdb, *.accdb)};'
            r'DBQ=' + archivo_access + ';'
        )
        conn = pyodbc.connect(conn_str)
        return conn
    except Exception as e:
        st.error(f"Error: {str(e)[:100]}")  # Mostrar solo parte del error
        return None
    
@st.cache_resource
def get_connection_mysql():
    """
    Establece conexión a MySQL
    """
    try:
        conn = pymysql.connect(
            host=st.secrets["DB_HOST"],  # o st.secrets["DB_SERVER"]
            database=st.secrets["DB_NAME"],
            user=st.secrets["DB_USER"],
            password=st.secrets["DB_PASSWORD"],
            port=int(st.secrets.get("DB_PORT", 3306)),  # Puerto por defecto 3306
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor  # Para obtener resultados como diccionarios
        )
        return conn
    except pymysql.Error as e:
        st.error(f"Error de conexión MySQL: {str(e)}")
        return None
    except KeyError as e:
        st.error(f"Falta variable en secrets: {e}")
        return None
    except Exception as e:
        st.error(f"Error inesperado: {str(e)[:200]}")
        return None

@st.cache_data(ttl=300)  # Cache por 5 minutos
def cargar_catalogos(_conn):
    catalogos = {}
    
    try:
        catalogos['municipios'] = pd.read_sql(
            "SELECT DISTINCT Municipio FROM Quejas WHERE Municipio IS NOT NULL ORDER BY Municipio", 
            _conn
        )['Municipio'].tolist()
        catalogos['procedencia'] = pd.read_sql(
            "SELECT DISTINCT LugarProcedencia FROM Quejas WHERE LugarProcedencia IS NOT NULL ORDER BY LugarProcedencia", 
            _conn
        )['LugarProcedencia'].tolist()
        catalogos['ciudadhechos'] = pd.read_sql(
            "SELECT DISTINCT CiudadDeLosHechos FROM Quejas WHERE CiudadDeLosHechos IS NOT NULL ORDER BY CiudadDeLosHechos", 
            _conn
        )['CiudadDeLosHechos'].tolist()
        catalogos['recepcion'] = pd.read_sql(
            "SELECT DISTINCT Recepcion FROM Quejas WHERE Recepcion IS NOT NULL ORDER BY Recepcion", 
            _conn
        )['Recepcion'].tolist()
        catalogos['hechos'] = pd.read_sql(
            "SELECT DISTINCT Hecho FROM Quejas WHERE Hecho IS NOT NULL AND YEAR(FechaInicio)>2023 ORDER BY Hecho", 
            _conn
        )['Hecho'].tolist()
        catalogos['hechosNR'] = pd.read_sql(
            "SELECT DISTINCT Hecho FROM NoRecomendaciones WHERE Hecho IS NOT NULL ORDER BY Hecho", 
            _conn
        )['Hecho'].tolist()
        catalogos['sub'] = pd.read_sql(
            "SELECT DISTINCT Subprocu FROM Quejas WHERE Subprocu IS NOT NULL ORDER BY Subprocu", 
            _conn
        )['Subprocu'].tolist()
        catalogos['dependencias'] = pd.read_sql(
            "SELECT DISTINCT Dependencia FROM Quejas WHERE Dependencia IS NOT NULL ORDER BY Dependencia", 
            _conn
        )['Dependencia'].tolist()
        catalogos['grupovulnerable'] = pd.read_sql(
            "SELECT DISTINCT Grupo FROM Catalogo_Interseccionalidad WHERE Grupo IS NOT NULL ORDER BY Grupo", 
            _conn
        )['Grupo'].tolist()
        catalogos['organismoemisor'] = pd.read_sql(
            "SELECT DISTINCT Organismo FROM Catalogo_Organismo_Emisor WHERE Organismo IS NOT NULL ORDER BY Organismo", 
            _conn
        )['Organismo'].tolist()
        catalogos['DireccionMunicipal'] = pd.read_sql(
            "SELECT DISTINCT DireccionMunicipal FROM Quejas WHERE DireccionMunicipal IS NOT NULL ORDER BY DireccionMunicipal", 
            _conn
        )['DireccionMunicipal'].tolist()
        catalogos['AliasDependencia'] = pd.read_sql(
            "SELECT DISTINCT AliasDependencia FROM Quejas WHERE AliasDependencia IS NOT NULL ORDER BY AliasDependencia", 
            _conn
        )['AliasDependencia'].tolist()
        catalogos['AliasDependenciaActuallizado'] = pd.read_sql(
            "SELECT DISTINCT AliasDependenciaActuallizado FROM Quejas WHERE AliasDependenciaActuallizado IS NOT NULL ORDER BY AliasDependenciaActuallizado", 
            _conn
        )['AliasDependenciaActuallizado'].tolist()
        catalogos['TipoDependencia'] = ['Autónomo','Poder del Estado']
        catalogos['AliasDependenciaAuxiliar'] = ['Seguridad Penitenciaria']
        catalogos['Escolaridad'] = pd.read_sql(
            "SELECT DISTINCT Escolaridad FROM Quejosos_Ampliado WHERE Escolaridad IS NOT NULL ORDER BY Escolaridad", 
            _conn
        )['Escolaridad'].tolist()
        catalogos['Status'] = pd.read_sql(
            "SELECT DISTINCT Conclusión FROM Expediente WHERE Conclusión IS NOT NULL ORDER BY Conclusión", 
            _conn
        )['Conclusión'].tolist()
        catalogos['Alias_Status'] = pd.read_sql(
            "SELECT DISTINCT Alias_Conclusión FROM Expediente WHERE Alias_Conclusión IS NOT NULL ORDER BY Alias_Conclusión", 
            _conn
        )['Alias_Conclusión'].tolist()
        
    except Exception as e:
        st.error(f"Error cargando catálogos: {e}")
        # Valores por defecto vacíos
        catalogos['municipios'] = []
        catalogos['hechos'] = []
        catalogos['dependencias'] = []
    
    return catalogos