# UNIED - Sistema de Gestión de Quejas

![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=Streamlit&logoColor=white)
![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![SQL Server](https://img.shields.io/badge/Microsoft_SQL_Server-CC2927?style=for-the-badge&logo=microsoft-sql-server&logoColor=white)

**Unidad de Información Estadística y Documental - PRODHEG**

Sistema web para la gestión de expedientes de quejas con interfaz moderna y funcionalidades completas.

---

## Características Principales

### **Búsqueda Avanzada**
- Búsqueda por número de expediente
- Vista detallada de expedientes agrupados
- Capacidad de agregar nuevos hechos a expedientes existentes

### **Registro Completo**
- Formulario multipestaña organizado:
  - Información básica de la queja
  - Datos de la autoridad señalada
  - Información de personas involucradas
- Validación de campos obligatorios
- Catálogos dinámicos desde base de datos

### **Visualización y Análisis**
- Vista completa de todos los registros
- Filtros por expediente, municipio y dependencia
- Estadísticas en tiempo real
- Exportación a Excel

### **Interfaz Moderna**
- Diseño responsive con Streamlit
- CSS personalizado
- Navegación intuitiva con sidebar
- Logo institucional

---

## Estructura del Proyecto
app_quejas/\
├── main.py\
├── database.py\
├── models.py\
├── queries.py\
├── components/\
│   └── sidebar.py\
├── pages/\
│   ├── home.py\
│   ├── buscar.py\
│   ├── nueva_queja.py\
│   └── ver_todos.py\
├── img/\
│   ├── logo_horizontal.png\
│   └── loguito.png\
└── style.css\
## Requisitos Previos

### **Python 3.8+**
```bash
# Verificar instalación
python --version
```
Pasos para empezar a usar
```bash
pip install -r requirements.txt
git clone https://github.com/Taquitoo3000/captura_form.git
```
Editar `.streamlit/secrets.toml` con tus credenciales\
La apliacion se ejecuta con:
```bash
streamlit run main.py
```