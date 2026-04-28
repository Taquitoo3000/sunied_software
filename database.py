import streamlit as st
from datetime import datetime
import pandas as pd
from sqlalchemy import create_engine, text
    
@st.cache_resource
def get_connection_mysql():
    """
    Establece conexión a MySQL
    """
    try:
        engine = create_engine(
            f"mysql+pymysql://{st.secrets['DB_USER']}:{st.secrets['DB_PASS']}"
            f"@{st.secrets['DB_SERVER']}:{st.secrets.get('DB_PORT', 3306)}"
            f"/{st.secrets['DB_NAME']}?charset=utf8mb4"
        )
        return engine
    except KeyError as e:
        st.error(f"Falta variable en secrets: {e}")
        return None
    except Exception as e:
        st.error(f"Error inesperado: {str(e)[:200]}")
        return None

@st.cache_data(ttl=300)  # Cache por 5 minutos
def cargar_catalogos(_engine):
    catalogos = {}
    
    def leer(query, col):
        return pd.read_sql(query, _engine)[col].tolist()
 
    try:
        catalogos['municipios']                  = leer("SELECT DISTINCT Municipio FROM Quejas WHERE Municipio IS NOT NULL ORDER BY Municipio", 'Municipio')
        catalogos['procedencia']                 = leer("SELECT DISTINCT LugarProcedencia FROM Quejas WHERE LugarProcedencia IS NOT NULL ORDER BY LugarProcedencia", 'LugarProcedencia')
        catalogos['ciudadhechos']                = leer("SELECT DISTINCT CiudadDeLosHechos FROM Quejas WHERE CiudadDeLosHechos IS NOT NULL ORDER BY CiudadDeLosHechos", 'CiudadDeLosHechos')
        catalogos['recepcion']                   = leer("SELECT DISTINCT Recepcion FROM Quejas WHERE Recepcion IS NOT NULL ORDER BY Recepcion", 'Recepcion')
        catalogos['hechos']                      = leer("SELECT DISTINCT Hecho FROM Quejas WHERE Hecho IS NOT NULL AND YEAR(FechaInicio)>2023 ORDER BY Hecho", 'Hecho')
        catalogos['hechosNR']                    = leer("SELECT DISTINCT Hecho FROM NoRecomendaciones WHERE Hecho IS NOT NULL AND YEAR(Fecha_NR)>2024 ORDER BY Hecho", 'Hecho')
        catalogos['hechosR']                     = leer("SELECT DISTINCT Causa FROM Recomendaciones WHERE Causa IS NOT NULL AND YEAR(FechaRecom)>2024 ORDER BY Causa", 'Causa')
        catalogos['sub']                         = leer("SELECT DISTINCT Subprocu FROM Quejas WHERE Subprocu IS NOT NULL ORDER BY Subprocu", 'Subprocu')
        catalogos['dependencias']                = leer("SELECT DISTINCT Dependencia FROM Quejas WHERE Dependencia IS NOT NULL ORDER BY Dependencia", 'Dependencia')
        catalogos['dependenciasNR']              = leer("SELECT DISTINCT Dependencia FROM NoRecomendaciones WHERE Dependencia IS NOT NULL AND YEAR(Fecha_NR)>2024 ORDER BY Dependencia", 'Dependencia')
        catalogos['autoridadR']                  = leer("SELECT DISTINCT Autoridad FROM Recomendaciones WHERE Autoridad IS NOT NULL AND YEAR(FechaRecom)>2024 ORDER BY Autoridad", 'Autoridad')
        catalogos['grupovulnerable']             = leer("SELECT DISTINCT Grupo FROM Catalogo_Interseccionalidad WHERE Grupo IS NOT NULL ORDER BY Grupo", 'Grupo')
        catalogos['organismoemisor']             = leer("SELECT DISTINCT Organismo FROM Catalogo_Organismo_Emisor WHERE Organismo IS NOT NULL ORDER BY Organismo", 'Organismo')
        catalogos['DireccionMunicipal']          = leer("SELECT DISTINCT DireccionMunicipal FROM Quejas WHERE DireccionMunicipal IS NOT NULL ORDER BY DireccionMunicipal", 'DireccionMunicipal')
        catalogos['AliasDependencia']            = leer("SELECT DISTINCT AliasDependencia FROM Quejas WHERE AliasDependencia IS NOT NULL ORDER BY AliasDependencia", 'AliasDependencia')
        catalogos['AliasDependenciaActuallizado']= leer("SELECT DISTINCT AliasDependenciaActuallizado FROM Quejas WHERE AliasDependenciaActuallizado IS NOT NULL ORDER BY AliasDependenciaActuallizado", 'AliasDependenciaActuallizado')
        catalogos['TipoDependencia']             = ['Autónomo', 'Poder del Estado']
        catalogos['AliasDependenciaAuxiliar']    = ['Seguridad Penitenciaria']
        catalogos['Escolaridad']                 = leer("SELECT DISTINCT Escolaridad FROM Quejosos_Ampliado WHERE Escolaridad IS NOT NULL ORDER BY Escolaridad", 'Escolaridad')
        catalogos['Status']                      = leer("SELECT DISTINCT Conclusión FROM Expediente WHERE Conclusión IS NOT NULL ORDER BY Conclusión", 'Conclusión')
        catalogos['Alias_Status']                = leer("SELECT DISTINCT Alias_Conclusión FROM Expediente WHERE Alias_Conclusión IS NOT NULL ORDER BY Alias_Conclusión", 'Alias_Conclusión')
        catalogos['TipoViolencia']               = leer("SELECT DISTINCT `Tipo De Violencia` FROM Expediente WHERE `Tipo De Violencia` IS NOT NULL ORDER BY `Tipo De Violencia`", 'Tipo De Violencia')
        catalogos['AmbitoViolencia']             = leer("SELECT DISTINCT AmbitoModalidadViolencia FROM Expediente WHERE AmbitoModalidadViolencia IS NOT NULL ORDER BY AmbitoModalidadViolencia", 'AmbitoModalidadViolencia')
 
    except Exception as e:
        st.error(f"Error cargando catálogos: {e}")
        catalogos.setdefault('municipios', [])
        catalogos.setdefault('hechos', [])
        catalogos.setdefault('dependencias', [])
 
    return catalogos

def cargar_datos_queja(engine, expediente):
    with engine.connect() as conn:
        # Datos basicos
        result = conn.execute(text("""
            SELECT DISTINCT 
                e.Expediente, q.FechaInicio, q.LugarProcedencia, e.Recepcion, 
                e.Personas, e.Subprocu, q.Observaciones, e.GrupoVulnerable, 
                e.MujerAgraviada, e.`Organismo emisor`, q.CiudadDeLosHechos
            FROM Expediente as e
                    left join Quejas as q on q.Expediente=e.Expediente
            WHERE e.Expediente = :expediente
            group by e.Expediente, q.FechaInicio, q.LugarProcedencia, e.Recepcion, 
                e.Personas, e.Subprocu, q.Observaciones, e.GrupoVulnerable, 
                e.MujerAgraviada, e.`Organismo emisor`, q.CiudadDeLosHechos
        """), {'expediente': expediente})
        datos_basicos = result.fetchone()
        if not datos_basicos:
            return None
        
        # Cargar motivo/resumen
        result = conn.execute(text("""
            SELECT Motivo 
            FROM Quejas_Motivos 
            WHERE Expediente = :expediente
        """), {'expediente': expediente})
        motivo_row = result.fetchone()
        motivo = motivo_row[0] if motivo_row else ""
        
        # Cargar autoridades
        result =    conn.execute(text("""
            SELECT DISTINCT 
                Autoridad, Municipio, Dependencia, DireccionMunicipal, 
                Hecho, AliasDependencia, AliasDependenciaActuallizado, 
                AliasDependenciaAuxiliar, TipoDependencia
            FROM Quejas 
            WHERE Expediente = :expediente AND Autoridad IS NOT NULL
        """), {'expediente': expediente})
        autoridades = [
            {
                'autoridad':          row[0],
                'municipio':          row[1],
                'dependencia':        row[2],
                'direccion_municipal':row[3],
                'hecho':              row[4],
                'alias_dependencia':  row[5],
                'alias_actualizado':  row[6],
                'alias_auxiliar':     row[7],
                'tipo_dependencia':   row[8],
            }
            for row in result.fetchall()
        ]
        
        # Cargar personas
        result = conn.execute(text("""
            SELECT 
                Nombre, `Quejoso/Agraviado`, Actividad, Sexo, 
                Edad, EdadNumero, CalidadPenal, Subprocu, 
                `Ocupación-Nivel`, Victima_Tipo, Fecha_Nacimiento, 
                Nacionalidad, Curp, LugarNacimiento_Pais, LugarNacimiento_Entidad, 
                LugarNacimiento_Mucipio, LugarNacimiento_Poblacion, `Sabe Leer`, 
                Escolaridad, Estado_Civil, Calle, Numero_ext, 
                Numero_int, CodigoPostal, Colonia, Domicilio_Localidad, 
                Domicilio_Municipio, Domicilio_Entidad, Telefono
            FROM Quejosos_Ampliado 
            WHERE Expediente = :expediente
        """), {'expediente': expediente})
        
        personas = [
            {
                'nombre': row[0],
                'quejoso': row[1],
                'ocupacion': row[2],
                'sexo': row[3],
                'edad_nivel': row[4],
                'edad':  row[5],
                'calidad': row[6],
                'ocupacion_nivel': row[9],
                'fecha_nacimiento': row[10],
                'nacionalidad': row[11],
                'curp': row[12],
                'n_pais': row[13],
                'n_estado': row[14],
                'n_municipio': row[15],
                'sabe_leer': bool(row[17]),
                'escolaridad': row[18],
                'estado_civil': row[19],
                'domicilio': row[20],
                'numero_exterior': row[21],
                'numero_interior': row[22],
                'codigo_postal': row[23],
                'colonia': row[24],
                'localidad_domicilio': row[25],
                'municipio_domicilio': row[26],
                'estado_domicilio': row[27],
                'telefono': row[28]
            }
            for row in result.fetchall()
        ]

        return {
            'datos_basicos': datos_basicos,
            'motivo': motivo,
            'autoridades': autoridades,
            'personas': personas
        }

def log_event(conn, session_id, ip, evento, pagina=None):
    try:
        with conn.begin() as connection:
            connection.execute(
                text("""
                    INSERT INTO logs_acceso (session_id, ip, evento, pagina)
                    VALUES (:session_id, :ip, :evento, :pagina)
                """),
                {
                    "session_id": session_id,
                    "ip": ip,
                    "evento": evento,
                    "pagina": pagina
                }
            )
    except Exception as e:
        print(f"Error guardando log: {e}")