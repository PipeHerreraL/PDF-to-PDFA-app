import os
import subprocess
import urllib.request
import tempfile
import shutil
import time

def ensure_ghostscript_installed():
    """Verifica e instala Ghostscript si es necesario."""
    gs_path = find_ghostscript()
    if gs_path:
        return True  # Ya instalado

    print("Ghostscript no está instalado. Iniciando descarga...")

    try:
        # URL del instalador oficial (versión estable)
        gs_url = "https://github.com/ArtifexSoftware/ghostpdl-downloads/releases/download/gs10060/gs10060w64.exe"

        temp_dir = tempfile.gettempdir()
        installer_path = os.path.join(temp_dir, "ghostscript_installer.exe")

        urllib.request.urlretrieve(gs_url, installer_path)
        print(f"Instalador descargado en: {installer_path}")

        # Ejecutar el instalador y esperar a que finalice
        print("Ejecutando instalador de Ghostscript, espera unos segundos...")
        result = subprocess.run([installer_path, "/S"], shell=True)  # /S instala en modo silencioso

        if result.returncode != 0:
            print("⚠️ El instalador devolvió un código de error.")
            return False

        print("Instalación completada. Verificando...")

        # Esperar a que Windows registre los nuevos binarios
        for _ in range(10):
            time.sleep(2)
            gs_path = find_ghostscript()
            if gs_path:
                print(f"✅ Ghostscript detectado en: {gs_path}")
                add_ghostscript_to_path(gs_path)
                return True

        print("❌ No se encontró Ghostscript después de la instalación.")
        return False

    except Exception as e:
        print(f"Error al intentar instalar Ghostscript: {e}")
        return False


def find_ghostscript():
    """Busca Ghostscript en PATH o rutas comunes."""
    paths_to_try = [
        shutil.which("gs"),
        shutil.which("gswin64c"),
        shutil.which("gswin32c"),
    ]

    for p in paths_to_try:
        if p:
            return p

    common_bases = [
        r"C:\Program Files\gs",
        r"C:\Program Files (x86)\gs",
    ]

    for base in common_bases:
        if os.path.exists(base):
            for folder in os.listdir(base):
                candidate = os.path.join(base, folder, "bin", "gswin64c.exe")
                if os.path.exists(candidate):
                    return candidate
    return None


def add_ghostscript_to_path(gs_path):
    """Agrega el directorio de Ghostscript al PATH del usuario."""
    gs_dir = os.path.dirname(gs_path)
    current_path = os.environ.get("PATH", "")

    if gs_dir.lower() in current_path.lower():
        print("✅ Ghostscript ya está en PATH.")
        return True

    print(f"🧩 Agregando {gs_dir} al PATH del usuario...")
    subprocess.run(f'setx PATH "{current_path};{gs_dir}"', shell=True)
    print("✅ Ruta agregada correctamente (efectiva en nuevas terminales).")
    return True

def get_ghostscript_command():
    """Detecta el comando correcto de Ghostscript en el sistema."""
    if shutil.which("gs"):
        return "gs"
    elif shutil.which("gswin64c"):
        return "gswin64c"
    elif shutil.which("gswin32c"):
        return "gswin32c"
    else:
        return None


def convert_to_pdfa(input_path, output_path):
    gs_command = get_ghostscript_command()
    if not gs_command:
        return False, "No se encontró Ghostscript en el sistema."

    try:
        subprocess.run([
            gs_command,
            "-dPDFA=2",
            "-dBATCH",
            "-dNOPAUSE",
            "-dNOOUTERSAVE",
            "-sProcessColorModel=DeviceCMYK",
            "-sDEVICE=pdfwrite",
            f"-sOutputFile={output_path}",
            input_path
        ], check=True)
        return True, None
    except subprocess.CalledProcessError as e:
        return False, str(e)