import os
import subprocess
import urllib.request
import tempfile
import shutil
import time
from pathlib import Path

def ensure_ghostscript_installed():
    """Verifica e instala Ghostscript si es necesario."""
    gs_path = get_ghostscript_command()
    if gs_path:
        return True  # Ya instalado

    print("Ghostscript no está instalado. Iniciando descarga...")

    try:
        # URL del instalador oficial (versión estable, actualizar según necesidad)
        gs_url = "https://github.com/ArtifexSoftware/ghostpdl-downloads/releases/download/gs10060/gs10060w64.exe"

        temp_dir = tempfile.gettempdir()
        installer_path = os.path.join(temp_dir, "ghostscript_installer.exe")

        urllib.request.urlretrieve(gs_url, installer_path)
        print(f"Instalador descargado en: {installer_path}")

        # Ejecutar el instalador silencioso
        print("Ejecutando instalador de Ghostscript...")
        result = subprocess.run([installer_path, "/S"], shell=True)  # /S modo silencioso
        if result.returncode != 0:
            print("⚠️ El instalador devolvió un código de error.")
            return False

        print("Instalación completada. Verificando...")

        # Esperar unos segundos a que Windows registre el nuevo binario
        for _ in range(10):
            time.sleep(2)
            gs_path = get_ghostscript_command()
            if gs_path:
                print(f"✅ Ghostscript detectado en: {gs_path}")
                add_ghostscript_to_path(gs_path)
                return True

        print("❌ No se encontró Ghostscript después de la instalación.")
        return False

    except Exception as e:
        print(f"Error al intentar instalar Ghostscript: {e}")
        return False


def get_ghostscript_command():
    """Detecta el comando correcto de Ghostscript y agrega su carpeta al PATH temporal del proceso."""
    candidates = ["gs", "gswin64c", "gswin32c"]

    for cmd in candidates:
        path = shutil.which(cmd)
        if path:
            # Agregar carpeta al PATH del proceso actual
            os.environ["PATH"] += os.pathsep + str(Path(path).parent)
            return cmd

    # Intentar rutas comunes de instalación
    common_bases = [
        r"C:\Program Files\gs",
        r"C:\Program Files (x86)\gs",
    ]

    for base in common_bases:
        if os.path.exists(base):
            for folder in os.listdir(base):
                candidate = Path(base) / folder / "bin" / "gswin64c.exe"
                if candidate.exists():
                    os.environ["PATH"] += os.pathsep + str(candidate.parent)
                    return str(candidate)

    return None


def add_ghostscript_to_path(gs_path):
    """Agrega el directorio de Ghostscript al PATH del usuario (para nuevas terminales)."""
    gs_dir = str(Path(gs_path).parent)
    current_path = os.environ.get("PATH", "")

    if gs_dir.lower() in current_path.lower():
        print("✅ Ghostscript ya está en PATH.")
        return True

    print(f"🧩 Agregando {gs_dir} al PATH del usuario...")
    subprocess.run(f'setx PATH "{current_path};{gs_dir}"', shell=True)
    print("✅ Ruta agregada correctamente (efectiva en nuevas terminales).")
    return True


def convert_to_pdfa(input_path, output_path):
    """Convierte un PDF a PDF/A usando Ghostscript de manera completamente silenciosa."""
    gs_command = get_ghostscript_command()
    if not gs_command:
        return False, "No se encontró Ghostscript en el sistema."

    try:
        creationflags = 0
        startupinfo = None

        if os.name == 'nt':
            # Evita que se abra la ventana de consola en Windows
            creationflags = subprocess.CREATE_NO_WINDOW
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW

        subprocess.run(
            [
                gs_command,
                "-dPDFA=2",
                "-dBATCH",
                "-dNOPAUSE",
                "-dNOOUTERSAVE",
                "-sProcessColorModel=DeviceCMYK",
                "-sDEVICE=pdfwrite",
                f"-sOutputFile={output_path}",
                input_path
            ],
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            startupinfo=startupinfo,
            creationflags=creationflags
        )
        return True, None
    except subprocess.CalledProcessError as e:
        return False, str(e)
