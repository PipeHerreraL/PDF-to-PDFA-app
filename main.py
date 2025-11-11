import sys
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLabel,
    QPushButton, QFileDialog, QMessageBox, QProgressBar
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from pathlib import Path

# Importar funciones del convertidor
from converter import convert_to_pdfa, ensure_ghostscript_installed, find_ghostscript, add_ghostscript_to_path


class ConverterThread(QThread):
    progress = pyqtSignal(int)
    finished = pyqtSignal(bool)

    def __init__(self, files, output_dirs):
        super().__init__()
        self.files = files
        self.output_dirs = output_dirs

    def run(self):
        total = len(self.files)
        for i, (file, out_dir) in enumerate(zip(self.files, self.output_dirs), start=1):
            file_path = Path(file)
            out_dir = Path(out_dir)
            out_dir.mkdir(parents=True, exist_ok=True)

            # Mantener el nombre original
            output_file = out_dir / file_path.name

            success, error = convert_to_pdfa(str(file_path), str(output_file))
            if not success:
                print(f"Error al convertir {file}: {error}")

            self.progress.emit(int(i / total * 100))
        self.finished.emit(True)



class PDFConverterApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PDF/A Converter")
        self.setFixedSize(400, 250)

        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.label = QLabel("Seleccione archivos PDF para convertir a PDF/A")
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.btn_select = QPushButton("Seleccionar Archivos")
        self.btn_select.clicked.connect(self.select_files)

        self.progress = QProgressBar()
        self.progress.setValue(0)
        self.progress.setTextVisible(True)

        self.btn_convert = QPushButton("Convertir")
        self.btn_convert.setEnabled(False)
        self.btn_convert.clicked.connect(self.start_conversion)

        layout.addWidget(self.label)
        layout.addWidget(self.btn_select)
        layout.addWidget(self.progress)
        layout.addWidget(self.btn_convert)

        self.setLayout(layout)
        self.files = []

    def select_files(self):
        files, _ = QFileDialog.getOpenFileNames(
            self, "Seleccionar archivos PDF", "", "Archivos PDF (*.pdf)"
        )
        if files:
            self.files = files
            self.btn_convert.setEnabled(True)
            self.label.setText(f"{len(files)} archivo(s) seleccionado(s)")

    def start_conversion(self):
        if not self.files:
            QMessageBox.warning(self, "Advertencia", "No hay archivos seleccionados.")
            return

        # Pedir carpeta de destino
        folder = QFileDialog.getExistingDirectory(
            self, "Seleccionar carpeta de destino para los PDFs convertidos"
        )

        self.output_dirs = []

        for file in self.files:
            file_path = Path(file)
            if folder:
                # Crear carpeta 'converted' dentro de la carpeta seleccionada
                output_dir = Path(folder) / "converted"
            else:
                # Crear carpeta 'converted' junto al archivo original
                output_dir = file_path.parent / "converted"

            output_dir.mkdir(parents=True, exist_ok=True)
            self.output_dirs.append(output_dir)

        # Inicializar el thread de conversión
        self.thread = ConverterThread(self.files, self.output_dirs)
        self.thread.progress.connect(self.progress.setValue)
        self.thread.finished.connect(self.on_finished)
        self.thread.start()

        self.btn_convert.setEnabled(False)

    def on_finished(self, success):
        QMessageBox.information(self, "Completado", "Conversión terminada correctamente.")
        self.progress.setValue(100)
        self.btn_convert.setEnabled(True)
        self.label.setText("Seleccione archivos PDF para convertir a PDF/A")


def main():
    app = QApplication(sys.argv)

    # 1️⃣ Verificar Ghostscript antes de abrir la app
    if not ensure_ghostscript_installed():
        QMessageBox.critical(None, "Error",
                             "No se pudo instalar Ghostscript automáticamente.\n"
                             "Por favor instálalo manualmente desde:\n"
                             "https://ghostscript.com/releases/gsdnld.html")
        sys.exit()

    # 2️⃣ Intentar encontrar el ejecutable y agregarlo al PATH
    gs_path = find_ghostscript()
    if gs_path:
        add_ghostscript_to_path(gs_path)
    else:
        QMessageBox.warning(None, "Advertencia",
                            "Ghostscript fue instalado, pero no se encontró automáticamente.\n"
                            "Por favor reinicia la aplicación o verifica la instalación manualmente.")
        sys.exit()

    # 3️⃣ Iniciar la ventana principal
    window = PDFConverterApp()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
