@echo off
echo Directorio actual: %cd%
echo.
echo.
echo Contenido de la carpeta sunied:
dir
echo.

if exist main.py (
    echo Iniciando Streamlit...
    streamlit run main.py
) else (
    echo No se encuentra main.py
    echo Archivos .py disponibles:
    dir *.py
)

pause