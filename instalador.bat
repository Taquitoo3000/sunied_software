@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion
title Instalador SUNIED Software
color 0A

echo ========================================
echo    INSTALADOR SUNIED SOFTWARE
echo ========================================
echo.
echo Este instalador configurara todo lo necesario
echo para ejecutar la aplicacion SUNIED.
echo.
echo Por favor, NO cierre esta ventana hasta que
echo la instalacion se complete.
echo.
pause

:: ================================
:: 1. VERIFICAR/INSTALAR PYTHON
:: ================================
echo.
echo [1/5] Verificando Python...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Python no encontrado. Instalando Python 3.10...
    
    :: Descargar Python
    powershell -Command "Invoke-WebRequest -Uri 'https://www.python.org/ftp/python/3.10.11/python-3.10.11-amd64.exe' -OutFile 'python_installer.exe'"
    
    :: Instalar Python silenciosamente
    echo Instalando Python, por favor espere...
    start /wait python_installer.exe /quiet InstallAllUsers=1 PrependPath=1 Include_test=0
    
    :: Limpiar instalador
    del python_installer.exe
    
    :: Actualizar PATH inmediatamente
    setx PATH "%PATH%;C:\Python310;C:\Python310\Scripts"
    set PATH=%PATH%;C:\Python310;C:\Python310\Scripts
) else (
    echo Python ya esta instalado.
)

:: ================================
:: 2. VERIFICAR GIT
:: ================================
echo.
echo [2/5] Verificando Git...
git --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Git no encontrado. Instalando Git...
    
    :: Descargar Git
    powershell -Command "Invoke-WebRequest -Uri 'https://github.com/git-for-windows/git/releases/download/v2.42.0.windows.2/Git-2.42.0.2-64-bit.exe' -OutFile 'git_installer.exe'"
    
    :: Instalar Git silenciosamente
    echo Instalando Git, por favor espere...
    start /wait git_installer.exe /VERYSILENT /NORESTART /NOCANCEL /SP- /CLOSEAPPLICATIONS /RESTARTAPPLICATIONS
    
    :: Limpiar
    timeout /t 5 >nul
    del git_installer.exe
    
    :: Agregar Git al PATH
    set PATH=%PATH%;C:\Program Files\Git\cmd
) else (
    echo Git ya esta instalado.
)

:: ================================
:: 3. CLONAR REPOSITORIO
:: ================================
echo.
echo [3/5] Descargando SUNIED Software...
if exist "C:\SUNIED" (
    echo Carpeta existente encontrada. Actualizando...
    cd C:\SUNIED
    git pull origin main
) else (
    git clone https://github.com/Taquitoo3000/sunied_software.git C:\SUNIED
    cd C:\SUNIED
)

:: ================================
:: 4. INSTALAR DEPENDENCIAS
:: ================================
echo.
echo [4/5] Instalando dependencias de Python...
echo Esto puede tomar unos minutos...

:: Crear y activar entorno virtual (opcional pero recomendado)
python -m venv venv
call venv\Scripts\activate.bat

:: Instalar dependencias
pip install --upgrade pip
pip install streamlit pandas pyodbc python-dateutil
pip install -r requirements.txt 2>nul || (
    echo Creando archivo de requerimientos...
    echo streamlit>=1.28.0 > requirements.txt
    echo pandas>=2.0.0 >> requirements.txt
    echo pyodbc>=5.0.0 >> requirements.txt
    echo python-dateutil>=2.8.0 >> requirements.txt
    pip install -r requirements.txt
)

:: ================================
:: 5. CONFIGURAR ACCESO DIRECTO
:: ================================
echo.
echo [5/5] Configurando acceso rapido...

:: Crear script de inicio
echo @echo off > "C:\SUNIED\iniciar_sunied.bat"
echo chcp 65001 >> "C:\SUNIED\iniciar_sunied.bat"
echo title SUNIED Software >> "C:\SUNIED\iniciar_sunied.bat"
echo echo Iniciando SUNIED Software... >> "C:\SUNIED\iniciar_sunied.bat"
echo cd /d "C:\SUNIED" >> "C:\SUNIED\iniciar_sunied.bat"
echo call venv\Scripts\activate.bat >> "C:\SUNIED\iniciar_sunied.bat"
echo streamlit run app.py --server.port 8501 --server.headless true >> "C:\SUNIED\iniciar_sunied.bat"

:: Crear acceso directo en escritorio
echo Set oWS = WScript.CreateObject("WScript.Shell") > "%TEMP%\crear_acceso.vbs"
echo sLinkFile = "%USERPROFILE%\Desktop\SUNIED Software.lnk" >> "%TEMP%\crear_acceso.vbs"
echo Set oLink = oWS.CreateShortcut(sLinkFile) >> "%TEMP%\crear_acceso.vbs"
echo oLink.TargetPath = "C:\SUNIED\iniciar_sunied.bat" >> "%TEMP%\crear_acceso.vbs"
echo oLink.WorkingDirectory = "C:\SUNIED" >> "%TEMP%\crear_acceso.vbs"
echo oLink.Description = "SUNIED Software" >> "%TEMP%\crear_acceso.vbs"
echo oLink.Save >> "%TEMP%\crear_acceso.vbs"
cscript //nologo "%TEMP%\crear_acceso.vbs"
del "%TEMP%\crear_acceso.vbs"

:: ================================
:: FINALIZACION
:: ================================
echo.
echo ========================================
echo    INSTALACION COMPLETADA!
echo ========================================
echo.
echo Se ha creado un acceso directo en tu escritorio
echo llamado "SUNIED Software.lnk"
echo.
echo Para iniciar la aplicacion:
echo 1. Haz doble click en el acceso directo del escritorio
echo 2. O ejecuta: C:\SUNIED\iniciar_sunied.bat
echo.
echo La aplicacion se abrira en tu navegador en:
echo http://localhost:8501
echo.
echo Manten esta ventana abierta mientras usas la app.
echo.
pause