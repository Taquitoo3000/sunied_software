import streamlit as st
from datetime import datetime
from database import cargar_catalogos
import pandas as pd

def render(conn, catalogos):
    st.header("➕ Registrar Nueva Queja")
    st.markdown("---")
    # Formulario en pestañas para mejor organización
    tab1, tab2, tab3 = st.tabs(["📋 Información Básica", "🏛️ Autoridad Señalada", "👥 Personas Involucradas"])
    
    with tab1:  # Información Básica
        col1, col2 = st.columns(2)
        
        with col1:
            # Si venimos de agregar a expediente existente
            expediente_default = st.session_state.get('expediente_editar', '')
            expediente = st.text_input(
                "Número de Expediente *",
                value=expediente_default,
                placeholder="Ej: 0123/2024-A",
                help="Formato: Número/Año-Sub"
            )
            
            fecha_inicio = st.date_input(
                "Fecha de Inicio *",
                value=datetime.now().date(),
                format="DD/MM/YYYY"
            )
            
            lugar_procedencia = st.selectbox(
                "Lugar de Procedencia *",
                placeholder="Lugar de procedencia de la queja",
                options=catalogos['procedencia'],
                index=None
            )
            
            ciudad_hechos = st.selectbox(
                "Ciudad de los Hechos *",
                placeholder="Ciudad donde ocurrieron los hechos",
                options=catalogos['ciudadhechos'],
                index=None,
            )
            personas = st.selectbox(
                "Individual o Colectivo *",
                placeholder="Número de personas quejosas",
                options=["Individual", "Colectivo"],
                index=None
            )
            
            subprocu = st.selectbox(
                "Subprocuraduría *",
                options=catalogos['sub'],
                index=None
            )
        
        with col2:
            recepcion = st.selectbox(
                "Recepción *",
                placeholder="Tipo de recepción",
                options=catalogos['recepcion'],
                index=None
            )
            organismo_emisor = st.selectbox(
                "Organismo Emisor",
                placeholder="Organismo que emite la queja",
                options=catalogos['organismoemisor'],
                index=None
            )
            resumen = st.text_area(
                "Resumen de los Hechos *",
                placeholder="Inicia queja por...",
                height=120,
                max_chars=450
            )
            grupo_vulnerable = st.selectbox(
                "Grupo Vulnerable",
                options=catalogos['grupovulnerable'],
                index=None
            )
            mujer_agraviada = st.checkbox(
                "Mujer Agraviada",
                help="Marque si hay una mujer agraviada en el caso"
            )
            observaciones = st.text_area(
                "Observaciones",
                placeholder="Observaciones adicionales sobre el caso (laboral, nota periodistica, tortura, etc.)",
                height=120,
                max_chars=250
            )
    
    with tab2:  # Autoporidad Señalada
        st.markdown("### 🏛️ Autoridades y Hechos Denunciados")
        st.markdown("Puede agregar múltiples autoridades y hechos para este expediente.")
        
        # Inicializar lista en session_state si no existe
        if 'autoridades_lista' not in st.session_state:
            st.session_state.autoridades_lista = []
        
        # Contenedor para las autoridades
        autoridades_container = st.container()
        
        with autoridades_container:
            # Mostrar autoridades existentes
            if st.session_state.autoridades_lista:
                st.markdown("**Autoridades agregadas:**")
                for i, auth in enumerate(st.session_state.autoridades_lista):
                    col1, col2, col3 = st.columns([3, 3, 1])
                    with col1:
                        st.markdown(f"**Autoridad:** {auth['autoridad']}")
                    with col2:
                        st.markdown(f"**Hecho:** {auth['hecho']}")
                    with col3:
                        if st.button("❌", key=f"eliminar__auth{i}"):
                            del st.session_state.autoridades_lista[i]
                            st.rerun()
            
            # Separador
            st.divider()
        
            col1, col2 = st.columns(2)
            with col1:
                autoridad = st.text_input(
                    "Autoridad Señalada *",
                    placeholder="Nombre de la autoridad específica",
                    max_chars=255
                )
                municipio = st.selectbox(
                    "Municipio *",
                    options=catalogos['municipios'],
                    index=None,
                    placeholder="Autoridad de Municipio, Estatal o Federal"
                )
                dependencia = st.selectbox(
                    "Dependencia *",
                    options=catalogos['dependencias'],
                    index=None,
                    placeholder="Seleccione la dependencia"
                )
                direccion_municipal = st.selectbox(
                    "Dirección Municipal *",
                    placeholder="Dirección de la Dependencia",
                    options=catalogos['DireccionMunicipal'],
                    index=None
                )
            
            with col2:
                hecho = st.selectbox(
                    "Hecho Denunciado *",
                    options=catalogos['hechos'],
                    index=None,
                    placeholder="Seleccione tipo de hecho"
                )
                alias_dependencia = st.selectbox(
                    "Alias de Dependencia *",
                    options=catalogos['AliasDependencia'],
                    index=None
                )
                
                alias_actualizado = st.selectbox(
                    "Alias Actualizado *",
                    options=catalogos['AliasDependenciaActuallizado'],
                    index=None
                )
                
                alias_auxiliar = st.selectbox(
                    "Alias Auxiliar",
                    options=catalogos['AliasDependenciaAuxiliar'],
                    index=None
                )
                tipo_dependencia = st.selectbox(
                    "Tipo de Dependencia",
                    options=catalogos['TipoDependencia'],
                    index=None
                )
        col_add1, col_add2, col_add3 = st.columns([1, 2, 1])
        with col_add2:
            if st.button("➕ Agregar Autoridad", use_container_width=True):
                # Validar campos obligatorios
                if all([autoridad, municipio, dependencia, direccion_municipal, hecho, 
                        alias_dependencia, alias_actualizado]):
                    
                    nueva_entrada = {
                        'autoridad': autoridad,
                        'municipio': municipio,
                        'dependencia': dependencia,
                        'direccion_municipal': direccion_municipal,
                        'hecho': hecho,
                        'alias_dependencia': alias_dependencia,
                        'alias_actualizado': alias_actualizado,
                        'alias_auxiliar': alias_auxiliar,
                        'tipo_dependencia': tipo_dependencia
                    }
                    
                    st.session_state.autoridades_lista.append(nueva_entrada)
                    st.rerun()
                else:
                    st.error("Complete todos los campos obligatorios para agregar la autoridad")
        
    with tab3:  # Personas Involucradas
        # Inicializar lista en session_state si no existe
        if 'personas_lista' not in st.session_state:
            st.session_state.personas_lista = []
        
        # Contenedor para las autoridades
        personas_container = st.container()
        
        with personas_container:
            # Mostrar autoridades existentes
            if st.session_state.personas_lista:
                st.markdown("**Personas agregadas:**")
                for i, per in enumerate(st.session_state.personas_lista):
                    col1, col2, col3 = st.columns([3, 3, 1])
                    with col1:
                        st.markdown(f"**Persona:** {per['nombre']}")
                    with col2:
                        st.markdown(f"**Quejoso/Agraviado:** {per['quejoso']}")
                    with col3:
                        if st.button("❌", key=f"eliminar_per_{i}"):
                            del st.session_state.personas_lista[i]
                            st.rerun()
            
            # Separador
            st.divider()
            col1, col2 = st.columns(2)
            
            with col1:
                nombre = st.text_input(
                    "Nombre de la Persona Quejosa",
                    placeholder="Nombre completo de la persona Quejosa",
                    max_chars=255
                )
                quejoso = st.selectbox(
                    "Quejoso o Agraviado",
                    options=["Quejosa", "Agraviada"],
                    index=None,
                )
                sexo = st.selectbox(
                    "Sexo",
                    options=["Hombre", "Mujer", "Hombre OSIG", "Mujer OSIG", "No Binario", "Colectivo", "S/D"],
                    index=None,
                )
                edad_nivel = st.selectbox(
                    "Nivel de Edad",
                    options=["Adulta", "Menor"],
                    index=None,
                )
                edad = st.number_input(
                    "Edad",
                    min_value=0,
                    max_value=120,
                    step=1,
                    help="Edad en años completos"
                )
                fecha_nacimiento = st.text_input(
                    "Fecha de Nacimiento",
                    placeholder="DD/MM/YYYY",
                    value="",
                    help="Formato: DD/MM/YYYY (deje vacío si no determina)"
                )
                ocupacion = st.text_input(
                    "Ocupación",
                    placeholder="Ocupación de la persona quejosa",
                    max_chars=255
                )
                ocupacion_nivel = st.selectbox(
                    "Nivel de Ocupación",
                    options=["Estudiante", "Desempleado", "Trabajo Formal", "Trabajo Informal", "Otro"],
                    index=None,
                )
                sabe_leer = st.checkbox(
                    "Sabe leer y Escribir",
                    help="Marque si la persona sabe leer y escribir",
                    value=True
                )
                escolaridad = st.selectbox(
                    "Escolaridad",
                    options=catalogos['Escolaridad'],
                    index=None,
                )
                estado_civil = st.selectbox(
                    "Estado Civil",
                    options=["S/D","Soltera", "Casada", "Unión Libre", "Divorciada", "Viuda", "Finada"],
                    index=None,
                )
                calidad = st.selectbox(
                    "Calidad Penal",
                    options=["S/D","Víctima Directa", "Víctima Indirecta", "Testigo", "Defensor","Imputado","Ofendido","Procesado","Denunciante","Sentenciado"],
                    index=None,
                )
                curp = st.text_input(
                    "CURP",
                    placeholder="Clave Única de Registro de Población",
                    max_chars=18
                )
                nacionalidad = st.text_input(
                    "Nacionalidad",
                    placeholder="Nacionalidad de la persona quejosa",
                    max_chars=100
                )
            
            with col2:
                st.markdown("**Lugar de Nacimiento:**")
                n_pais = st.text_input(
                    "País",
                    placeholder="País donde nació la persona quejosa",
                    max_chars=100
                )
                n_estado = st.text_input(
                    "Estado",
                    placeholder="Estado donde nació la persona quejosa",
                    max_chars=100
                )
                n_municipio = st.text_input(
                    "Municipio",
                    placeholder="Municipio donde nació la persona quejosa",
                    max_chars=100
                )
                st.markdown("**Domicilio:**")
                domicilio = st.text_input(
                    "Calle",
                    placeholder="Calle del domicilio",
                    max_chars=255
                )
                numero_exterior = st.text_input(
                    "Número Exterior",
                    placeholder="Número exterior del domicilio",
                    max_chars=200
                )
                numero_interior = st.text_input(
                    "Número Interior",
                    placeholder="Número interior del domicilio",
                    max_chars=200
                )
                colonia = st.text_input(
                    "Colonia",
                    placeholder="Colonia del domicilio",
                    max_chars=255
                )
                codigo_postal = st.text_input(
                    "Código Postal",
                    placeholder="Código Postal del domicilio",
                    max_chars=10
                )
                municipio_domicilio = st.text_input(
                    "Municipio",
                    placeholder="Municipio del domicilio",
                    max_chars=255
                )
                estado_domicilio = st.text_input(
                    "Estado",
                    placeholder="Estado del domicilio",
                    max_chars=255
                )
                telefono = st.text_input(
                    "Teléfono",
                    placeholder="Teléfono de contacto",
                    max_chars=50
                )
    
        col_add1, col_add2, col_add3 = st.columns([1, 2, 1])
        with col_add2:
            if st.button("➕ Agregar Persona", use_container_width=True):
                # Validar campos obligatorios
                if all([nombre, quejoso]):
                    
                    nueva_persona = {
                        'nombre': nombre,
                        'quejoso': quejoso,
                        'sexo': sexo,
                        'edad_nivel': edad_nivel,
                        'edad': edad,
                        'fecha_nacimiento': fecha_nacimiento,
                        'ocupacion': ocupacion,
                        'ocupacion_nivel': ocupacion_nivel,
                        'sabe_leer': sabe_leer,
                        'escolaridad': escolaridad,
                        'estado_civil': estado_civil,
                        'calidad': calidad,
                        'curp': curp,
                        'nacionalidad': nacionalidad,
                        'n_pais': n_pais,
                        'n_estado': n_estado,
                        'n_municipio': n_municipio,
                        'domicilio': domicilio,
                        'numero_exterior': numero_exterior,
                        'numero_interior': numero_interior,
                        'colonia': colonia,
                        'codigo_postal': codigo_postal,
                        'municipio_domicilio': municipio_domicilio,
                        'estado_domicilio': estado_domicilio,
                        'telefono': telefono
                    }
                    
                    st.session_state.personas_lista.append(nueva_persona)
                    st.rerun()
                else:
                    st.error("Complete todos los campos obligatorios para agregar la persona")
    # Validación y botones (fuera de las pestañas)
    st.divider()
    st.markdown("### 📝 Validación y Envío")
    
    # Mostrar resumen de campos obligatorios
    campos_obligatorios = {
        "Expediente": expediente,
        "Fecha de Inicio": fecha_inicio,
        "Lugar de Procedencia": lugar_procedencia,
        "Ciudad de los Hechos": ciudad_hechos,
        "Personas": personas,
        "Subprocuraduría": subprocu,
        "Recepción": recepcion,
        "Resumen de Hechos": resumen,
        "Nombre": nombre,
        "Quejoso o Agraviado": quejoso
    }
    
    faltantes = [campo for campo, valor in campos_obligatorios.items() if not valor]
    
    # Botones de acción
    col_btn1, col_btn2 = st.columns(2)
    
    with col_btn1:
        if st.button("📝 Guardar Queja", type="primary", use_container_width=True, key="btn_guardar_completo"):
            if not faltantes:
                with st.spinner("Guardando en todas las tablas..."):
                    try:
                        # 1. Insertar en tabla Quejas
                        datos_basicos = (
                            expediente,
                            fecha_inicio,
                            lugar_procedencia,
                            recepcion,
                            personas,
                            subprocu,
                            observaciones if observaciones else None,
                            grupo_vulnerable if grupo_vulnerable else None,
                            1 if mujer_agraviada else 0,
                            organismo_emisor if organismo_emisor else None,
                            ciudad_hechos
                        )
                        datos = (
                            expediente,
                            fecha_inicio,
                            dependencia if dependencia else None,
                            municipio if municipio else None,
                            lugar_procedencia,
                            hecho if hecho else None,
                            recepcion,
                            personas,
                            subprocu,
                            observaciones if observaciones else None,
                            autoridad if autoridad else None,
                            grupo_vulnerable if grupo_vulnerable else None,
                            1 if mujer_agraviada else 0,
                            organismo_emisor if organismo_emisor else None,
                            direccion_municipal if direccion_municipal else None,
                            alias_dependencia if alias_dependencia else None,
                            alias_actualizado if alias_actualizado else None,
                            tipo_dependencia if tipo_dependencia else None,
                            alias_auxiliar if alias_auxiliar else None,
                            ciudad_hechos
                        )
                        cursor = conn.cursor()
                        if st.session_state.autoridades_lista:
                            for auth in st.session_state.autoridades_lista:
                                cursor.execute("""
                                    INSERT INTO ImportarQuejas 
                                    (Expediente, FechaInicio, 
                                    LugarProcedencia, Recepcion, Personas, Subprocu,
                                    Observaciones, GrupoVulnerable, MujerAgraviada,
                                    [Organismo emisor], CiudadDeLosHechos, Autoridad, Hecho, 
                                    Dependencia, Municipio, DireccionMunicipal, AliasDependencia, 
                                    AliasDependenciaActuallizado, AliasDependenciaAuxiliar, TipoDependencia
                                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                                """, (
                                    expediente,
                                    fecha_inicio,
                                    lugar_procedencia,
                                    recepcion,
                                    personas,
                                    subprocu,
                                    observaciones if observaciones else None,
                                    grupo_vulnerable if grupo_vulnerable else None,
                                    1 if mujer_agraviada else 0,
                                    organismo_emisor if organismo_emisor else None,
                                    ciudad_hechos,
                                    auth['autoridad'],
                                    auth['hecho'],
                                    auth['dependencia'],
                                    auth['municipio'],
                                    auth['direccion_municipal'],
                                    auth['alias_dependencia'],
                                    auth['alias_actualizado'],
                                    auth['alias_auxiliar'],
                                    auth['tipo_dependencia']
                                ))
                        else:
                            cursor.execute("""
                                    INSERT INTO ImportarQuejas 
                                    (Expediente, FechaInicio, Dependencia, Municipio, 
                                    LugarProcedencia, Hecho, Recepcion, Personas, Subprocu,
                                    Observaciones, Autoridad, GrupoVulnerable, MujerAgraviada,
                                    [Organismo emisor], DireccionMunicipal, AliasDependencia,
                                    AliasDependenciaActuallizado, TipoDependencia, AliasDependenciaAuxiliar,
                                    CiudadDeLosHechos)
                                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                                """, (datos))
                        
                        # 2. Insertar en Quejas_Motivos si hay motivo
                        if resumen and resumen.strip():
                            cursor.execute("""
                                INSERT INTO ImportarQuejas_Motivos (Expediente, Motivo)
                                VALUES (?, ?)
                            """, (expediente, resumen.strip()))
                        
                        # 3. Insertar en Quejosos_Ampliado
                        datos_persona = (
                            expediente,
                            nombre,
                            quejoso,
                            ocupacion if ocupacion else None,
                            sexo if sexo else None,
                            edad_nivel if edad_nivel else None,  # Edad
                            str(edad) if edad is not None and edad > 0 else None,  # EdadNumero
                            calidad if calidad else None,
                            subprocu if subprocu else None,
                            ocupacion_nivel if ocupacion_nivel else None,  # Ocupación-nivel
                            None,  # Victima_Tipo
                            fecha_nacimiento if fecha_nacimiento else None,
                            nacionalidad if nacionalidad else None,
                            curp if curp else None,
                            n_pais if n_pais else None,
                            n_estado if n_estado else None,
                            n_municipio if n_municipio else None,
                            None,  # LugarNacimiento_Poblacion
                            sabe_leer,
                            escolaridad if escolaridad else None,
                            estado_civil if estado_civil else None,
                            domicilio if domicilio else None,
                            numero_exterior if numero_exterior else None,  # Numero_ext
                            numero_interior if numero_interior else None,  # Numero_int
                            codigo_postal if codigo_postal else None,
                            colonia if colonia else None,
                            None,  # Domicilio_Localidad
                            municipio_domicilio if municipio_domicilio else None,
                            estado_domicilio if estado_domicilio else None,  # Domicilio_Entidad
                            telefono if telefono else None,
                        )

                        if st.session_state.personas_lista:
                            for per in st.session_state.personas_lista:
                                cursor.execute("""
                                    INSERT INTO ImportarQuejosos_Ampliado 
                                    (Expediente, Nombre, [Quejoso/Agraviado], Actividad, Sexo, 
                                    Edad, EdadNumero, CalidadPenal, Subprocu, 
                                    [Ocupación-Nivel], Victima_Tipo, Fecha_Nacimiento, 
                                    Nacionalidad, Curp, LugarNacimiento_Pais, LugarNacimiento_Entidad, 
                                    LugarNacimiento_Mucipio, LugarNacimiento_Poblacion, [Sabe Leer], 
                                    Escolaridad, Estado_Civil, Calle, Numero_ext, 
                                    Numero_int, CodigoPostal, Colonia, Domicilio_Localidad, 
                                    Domicilio_Municipio, Domicilio_Entidad, Telefono)
                                    VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
                                """, (expediente,
                                    per['nombre'],
                                        per['quejoso'],
                                        per['ocupacion'] if per['ocupacion'] else None,
                                        per['sexo'] if per['sexo'] else None,
                                        per['edad_nivel'] if per['edad_nivel'] else None,
                                        str(per['edad']) if per['edad'] is not None and per['edad'] > 0 else None,
                                        per['calidad'] if per['calidad'] else None,
                                        subprocu if subprocu else None,
                                        per['ocupacion_nivel'] if per['ocupacion_nivel'] else None,
                                        None,
                                        per['fecha_nacimiento'] if per['fecha_nacimiento'] else None,
                                        per['nacionalidad'] if per['nacionalidad'] else None,
                                        per['curp'] if per['curp'] else None,
                                        per['n_pais'] if per['n_pais'] else None,
                                        per['n_estado'] if per['n_estado'] else None,
                                        per['n_municipio'] if per['n_municipio'] else None,
                                        None,
                                        per['sabe_leer'],
                                        per['escolaridad'] if per['escolaridad'] else None,
                                        per['estado_civil'] if per['estado_civil'] else None,
                                        per['domicilio'] if per['domicilio'] else None,
                                        per['numero_exterior'] if per['numero_exterior'] else None,
                                        per['numero_interior'] if per['numero_interior'] else None,
                                        per['codigo_postal'] if per['codigo_postal'] else None,
                                        per['colonia'] if per['colonia'] else None,
                                        None,
                                        per['municipio_domicilio'] if per['municipio_domicilio'] else None,
                                        per['estado_domicilio'] if per['estado_domicilio'] else None,
                                        per['telefono'] if per['telefono'] else None,
                                    ))
                        else:
                            cursor.execute("""
                                INSERT INTO ImportarQuejosos_Ampliado 
                                    (Expediente, Nombre, [Quejoso/Agraviado], Actividad, Sexo, 
                                    Edad, EdadNumero, CalidadPenal, Subprocu, 
                                    [Ocupación-Nivel], Victima_Tipo, Fecha_Nacimiento, 
                                    Nacionalidad, Curp, LugarNacimiento_Pais, LugarNacimiento_Entidad, 
                                    LugarNacimiento_Mucipio, LugarNacimiento_Poblacion, [Sabe Leer], 
                                    Escolaridad, Estado_Civil, Calle, Numero_ext, 
                                    Numero_int, CodigoPostal, Colonia, Domicilio_Localidad, 
                                    Domicilio_Municipio, Domicilio_Entidad, Telefono)
                                VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
                            """, (datos_persona))


                        # 4. Insertar en Expediente
                        cursor.execute("""
                            INSERT INTO ImportarExpediente 
                            (Expediente, Conclusión, Alias_Conclusión, F_Conclusion, [Fecha de Inicio], LugarProcedencia, CiudadDeLosHechos, 
                            Personas, Subprocu, Recepcion, [Organismo emisor], GrupoVulnerable, 
                            MujerAgraviada)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """, (
                            expediente, 'En trámite', 'En trámite', None, fecha_inicio, lugar_procedencia, ciudad_hechos,
                            personas, subprocu, recepcion, organismo_emisor, grupo_vulnerable,
                            1 if mujer_agraviada else 0
                        ))
                        
                        conn.commit()
                        
                        st.success("✅ Expediente guardado exitosamente en todas las tablas!")
                        st.balloons()
                        # Limpiar cache de catálogos
                        cargar_catalogos.clear()
                        # Limpiar estado
                        st.session_state.expediente_editar = ""
                        st.balloons()
                        # Opción: limpiar formulario o redirigir
                        st.rerun()
                    except Exception as e:
                        conn.rollback()
                        st.error(f"❌ Error al guardar: {str(e)[:200]}")
            else:
                st.error("Complete todos los campos obligatorios (*)")
    
    with col_btn2:
        if st.button("🔄 Limpiar Formulario", use_container_width=True, key="btn_limpiar_completo"):
            # 1. Limpiar la lista de autoridades
            st.session_state.autoridades_lista = []
            
            # 2. Limpiar el expediente de edición
            if 'expediente_editar' in st.session_state:
                del st.session_state.expediente_editar
            
            # 3. Usar st.query_params para forzar una recarga completa
            # Esto es más efectivo que st.rerun() para limpiar widgets
            st.query_params.clear()
            
            # 4. Recargar
            st.rerun()