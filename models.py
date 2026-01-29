import pandas as pd
from datetime import datetime
import pyodbc

def insertar_queja_completa(_conn, datos):
    """
    Inserta una queja con todos los campos
    
    Args:
        _conn: Conexión a BD
        datos: Tupla con 20 valores en este orden:
            0: Expediente
            1: FechaInicio
            2: Dependencia
            3: Municipio
            4: LugarProcedencia
            5: Hecho
            6: Recepcion
            7: Personas
            8: Subprocu
            9: Observaciones
            10: Autoridad
            11: GrupoVulnerable
            12: MujerAgraviada (bit: 1 o 0)
            13: OrganismoEmisor
            14: DireccionMunicipal
            15: AliasDependencia
            16: AliasDependenciaActuallizado
            17: TipoDependencia
            18: AliasDependenciaAuxiliar
            19: CiudadDeLosHechos
    """
    cursor = _conn.cursor()
    try:
        cursor.execute("""
            INSERT INTO Quejas (
                Expediente, FechaInicio, Dependencia, Municipio, 
                LugarProcedencia, Hecho, Recepcion, Personas, Subprocu,
                Observaciones, Autoridad, GrupoVulnerable, MujerAgraviada,
                [Organismo emisor], DireccionMunicipal, AliasDependencia,
                AliasDependenciaActuallizado, TipoDependencia, 
                AliasDependenciaAuxiliar, CiudadDeLosHechos
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, datos)
        
        _conn.commit()
        return True, "✅ Queja registrada exitosamente con todos los campos"
        
    except pyodbc.Error as e:
        _conn.rollback()
        error_msg = str(e)
        
        # Manejo de errores comunes
        if "violation of PRIMARY KEY constraint" in error_msg:
            return False, "❌ Error: El número de expediente ya existe"
        elif "String or binary data would be truncated" in error_msg:
            return False, "❌ Error: Algún campo excede el tamaño máximo permitido"
        else:
            return False, f"❌ Error en la base de datos: {error_msg[:100]}"
            
    except Exception as e:
        _conn.rollback()
        return False, f"❌ Error inesperado: {str(e)[:100]}"
        
    finally:
        cursor.close()
