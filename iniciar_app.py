# iniciar_app.py
import subprocess
import time
import requests
import sys
import os
from datetime import datetime
import webbrowser

def verificar_dependencias():
    """Verifica que todo esté instalado"""
    print("🔍 Verificando dependencias...")
    
    # Verificar Python
    try:
        import streamlit
        print(f"✅ Streamlit {streamlit.__version__}")
    except ImportError:
        print("❌ Streamlit no instalado. Instalando...")
        subprocess.run([sys.executable, "-m", "pip", "install", "streamlit"])
    
    try:
        import pandas
        print(f"✅ Pandas {pandas.__version__}")
    except ImportError:
        print("❌ Pandas no instalado. Instalando...")
        subprocess.run([sys.executable, "-m", "pip", "install", "pandas"])
    
    # Verificar pyodbc si usas SQL Server
    try:
        import pyodbc
        print("✅ pyodbc instalado")
    except ImportError:
        print("❌ pyodbc no instalado. Instalando...")
        subprocess.run([sys.executable, "-m", "pip", "install", "pyodbc"])

def iniciar_ngrok(port=8501):
    """Inicia ngrok y retorna el proceso y la URL"""
    print("🚀 Iniciando ngrok...")
    
    try:
        # Iniciar ngrok en segundo plano
        proceso = subprocess.Popen(
            ['ngrok', 'http', str(port)],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Esperar a que ngrok inicie
        print("⏳ Esperando a que ngrok se inicie...")
        time.sleep(4)
        
        # Obtener URL pública
        try:
            respuesta = requests.get('http://localhost:4040/api/tunnels', timeout=10)
            respuesta.raise_for_status()
            
            datos = respuesta.json()
            if datos.get('tunnels'):
                url_publica = datos['tunnels'][0]['public_url']
                print(f"\n{'='*60}")
                print(f"✅ ¡APP LISTA!")
                print(f"{'='*60}")
                print(f"🌐 URL PÚBLICA: {url_publica}")
                print(f"📅 Hora de inicio: {datetime.now().strftime('%H:%M:%S')}")
                print(f"⏱️  Disponible por: 2 horas (límite ngrok free)")
                print(f"{'='*60}")
                
                # Guardar URL en archivo
                with open('url_acceso.txt', 'w', encoding='utf-8') as f:
                    f.write(f"URL: {url_publica}\n")
                    f.write(f"Inicio: {datetime.now()}\n")
                    f.write(f"Comparte este enlace para acceder desde cualquier dispositivo\n")
                
                print("📄 URL guardada en: url_acceso.txt")
                print("📱 Puedes compartir este archivo o el enlace")
                print(f"{'='*60}\n")
                
                return proceso, url_publica
            else:
                print("❌ No se encontraron túneles en ngrok")
                return proceso, None
                
        except requests.exceptions.RequestException as e:
            print(f"❌ Error al conectar con ngrok API: {e}")
            print("   Asegúrate de que ngrok se haya iniciado correctamente")
            return proceso, None
            
    except FileNotFoundError:
        print("❌ ERROR: ngrok no encontrado")
        print("\n📥 SOLUCIÓN:")
        print("1. Descarga ngrok de: https://ngrok.com/download")
        print("2. Extrae ngrok.exe en esta misma carpeta")
        print("3. O ejecuta desde la terminal: ngrok authtoken TU_TOKEN")
        print("4. Vuelve a ejecutar este script")
        return None, None

def main():
    """Función principal"""
    print(f"{'='*60}")
    print("       🖥️ SIPRODHEG 2.0 - SERVIDOR PÚBLICO")
    print(f"{'='*60}")
    
    # Verificar dependencias
    verificar_dependencias()
    
    # Iniciar ngrok
    ngrok_proceso, url_publica = iniciar_ngrok(8501)
    
    if not ngrok_proceso:
        input("\n⚠️  Presiona Enter para salir...")
        return
    
    if url_publica:
        # Preguntar si abrir en navegador
        abrir = input("\n¿Abrir en navegador? (s/n): ").lower()
        if abrir == 's':
            webbrowser.open(url_publica)
    
    # Iniciar Streamlit
    print("\n🎬 Iniciando aplicación Streamlit...")
    print("   Presiona Ctrl+C en esta ventana para detener todo\n")
    
    try:
        # Ejecutar Streamlit
        streamlit_proceso = subprocess.run([
            sys.executable, "-m", "streamlit", "run", 
            "main.py",
            "--server.port=8501",
            "--server.headless=false",
            "--browser.serverAddress=localhost",
            "--theme.base=light"
        ])
    except KeyboardInterrupt:
        print("\n🛑 Deteniendo aplicación...")
    finally:
        # Terminar ngrok si está corriendo
        if ngrok_proceso:
            ngrok_proceso.terminate()
            print("✅ Ngrok detenido")
        
        print("\n👋 Aplicación finalizada")
        input("Presiona Enter para cerrar...")

if __name__ == "__main__":
    main()