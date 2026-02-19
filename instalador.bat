@echo off
echo ============================================
echo       Instalacion SUNIED
echo ============================================
echo.

echo [1/2] Instalando Python...
instaladores\python-3.11.9-amd64.exe /quiet InstallAllUsers=0 PrependPath=1 Include_launcher=0
timeout /t 8 /nobreak >nul

set PYTHON=%USERPROFILE%\AppData\Local\Programs\Python\Python311\python.exe

echo [2/2] Instalando dependencias...
"%PYTHON%" -m pip install --upgrade pip >nul
"%PYTHON%" -m pip install -r requirements.txt

echo.
echo  Instalacion completa! 
echo  Ahora usa iniciar.bat para abrir la app.
echo.
pause