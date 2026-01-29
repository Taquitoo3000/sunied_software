@echo off
echo ============================================
echo    INSTALADOR SIPRODHEG 2.0
echo ============================================
echo.
echo Este instalador configurará todo automáticamente.
echo Por favor, no cierre esta ventana durante la instalación.
echo.

:: Obtener ruta del script
set "SCRIPT_DIR=%~dp0"
cd /d "%SCRIPT_DIR%"

:: Verificar si es administrador
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo ⚠️  Ejecutando como administrador...
    powershell -Command "Start-Process '%~f0' -Verb RunAs"
    exit /b
)

echo [1/6] Verificando Python...
where python >nul 2>&1
if %errorLevel% equ 0 (
    echo ✅ Python ya está instalado
    python --version
) else (
    echo 📥 Descargando Python 3.11...
    
    :: Crear carpeta temporal
    if not exist "temp" mkdir temp
    cd temp
    
    :: Descargar Python
    powershell -Command "Invoke-WebRequest -Uri 'https://www.python.org/ftp/python/3.11.9/python-3.11.9-amd64.exe' -OutFile 'python-installer.exe'"
    
    if exist python-installer.exe (
        echo 🔧 Instalando Python (esto puede tomar unos minutos)...
        echo.
        echo IMPORTANTE: Durante la instalación, MARQUE la opción:
        echo "Add Python to PATH" y haga clic en "Install Now"
        echo.
        python-installer.exe /quiet InstallAllUsers=1 PrependPath=1
        timeout /t 5 /nobreak >nul
        
        :: Verificar instalación
        where python >nul 2>&1
        if %errorLevel% equ 0 (
            echo ✅ Python instalado correctamente
        ) else (
            echo ❌ Error al instalar Python. Instálelo manualmente desde:
            echo https://www.python.org/downloads/
            pause
            exit /b 1
        )
    ) else (
        echo ❌ No se pudo descargar Python
        echo Descárguelo manualmente desde: https://www.python.org/downloads/
        pause
        exit /b 1
    )
    
    cd ..
)

echo.
echo [2/6] Actualizando pip...
python -m pip install --upgrade pip

echo.
echo [3/6] Instalando Streamlit y dependencias principales...
pip install streamlit pandas openpyxl cryptography

echo.
echo [4/6] Instalando conector MySQL...
pip install pymysql mysql-connector-python

echo.
echo [5/6] Creando archivos necesarios...

:: Crear archivo requirements.txt
(
echo streamlit^>=1.28.0
echo pandas^>=2.0.0
echo openpyxl^>=3.0.0
echo cryptography^>=41.0.0
echo pymysql^>=1.0.0
echo mysql-connector-python^>=8.0.0
) > requirements.txt

:: Crear archivo de configuración
if not exist "config" mkdir config
(
echo [database]
echo host = localhost
echo user = root
echo password = 
echo database = siprodeg
echo port = 3306
) > config\database.ini

echo.
echo [6/6] Configurando acceso directo en el escritorio...

:: Crear acceso directo
set "DESKTOP=%USERPROFILE%\Desktop"
set "SHORTCUT=%DESKTOP%\SIPRODHEG 2.0.lnk"

powershell -Command "$ws = New-Object -ComObject WScript.Shell; $sc = $ws.CreateShortcut('%SHORTCUT%'); $sc.TargetPath = '%~dp0EJECUTAR_APP.bat'; $sc.WorkingDirectory = '%~dp0'; $sc.Description = 'Sistema SIPRODHEG 2.0 - UIED'; $sc.Save()"

:: Crear acceso directo en el menú inicio
set "START_MENU=%APPDATA%\Microsoft\Windows\Start Menu\Programs\SIPRODHEG"
if not exist "%START_MENU%" mkdir "%START_MENU%"

powershell -Command "$ws = New-Object -ComObject WScript.Shell; $sc = $ws.CreateShortcut('%START_MENU%\SIPRODHEG 2.0.lnk'); $sc.TargetPath = '%~dp0EJECUTAR_APP.bat'; $sc.WorkingDirectory = '%~dp0'; $sc.Description = 'Sistema SIPRODHEG 2.0 - UIED'; $sc.Save()"

echo.
echo ============================================
echo    ✅ INSTALACIÓN COMPLETADA
echo ============================================
echo.
echo Se han creado accesos directos en:
echo 1. El escritorio: SIPRODHEG 2.0
echo 2. Menú Inicio: Programas > SIPRODHEG
echo.
echo Para ejecutar la aplicación, use el acceso directo
echo o ejecute "EJECUTAR_APP.bat"
echo.
echo Presione cualquier tecla para cerrar...
pause >nul