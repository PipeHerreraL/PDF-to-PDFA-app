# PDF/A Converter (PDF_A_Converter)

This repository contains a small PyQt6 app that converts PDFs to PDF/A.

This README explains how to build a standalone Windows application using PyInstaller.

## Requirements

- Python 3.8+ (use a virtual environment)
- Ghostscript (required at runtime) — install from https://ghostscript.com/releases/gsdnld.html and make sure it is on your PATH.
- The project `requirements.txt` (install with pip)

## Setup (Windows, PowerShell)

Open PowerShell and run:

```powershell
# from project root
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
# Install PyInstaller if not present
python -m pip install pyinstaller
```

## Build (create a single-file .exe)

From the project root (where `main.py` lives), run the PyInstaller command below. This will create a single-file, windowed executable named `PDF_A_Converter.exe` in the `dist` folder.

```powershell
# Build a single-file, GUI (windowed) executable
python -m PyInstaller --name "PDF_A_Converter" --onefile --windowed main.py
```

Notes and tips:
- PyInstaller will analyze imports and bundle your Python modules (`converter.py`, etc.).
- If your app needs to include non-Python data files (icons, additional assets), add `--add-data` options. The syntax on Windows PowerShell is:

```powershell
# Example: include an assets folder
python -m PyInstaller --name "PDF_A_Converter" --onefile --windowed `
  --add-data "assets;assets" main.py
```

- If your app needs to ship Ghostscript with it, Ghostscript is a separate binary and is typically installed by the user; make sure the target machine has Ghostscript installed and on PATH. Your app's `main.py` already checks for Ghostscript and will show instructions if it is missing.

## After build

- The built executable will be in `dist\PDF_A_Converter\` if you used non-default options, or `dist\PDF_A_Converter.exe` for the single-file build.
- Test the executable on a machine with Ghostscript installed.

## Running locally (development)

With your virtualenv active, run:

```powershell
python main.py
```

## Troubleshooting

- If the executable fails with missing modules, try building a `.spec` file and add hidden imports or data files. You can generate a spec file by running PyInstaller once and editing the generated `PDF_A_Converter.spec`.
- If PyInstaller misses an import used dynamically, add it with the `--hidden-import` option:

```powershell
python -m PyInstaller --onefile --windowed --hidden-import some.module main.py
```

- If the GUI doesn't show or you see console output, remove `--windowed` to see console logs while debugging.

## Summary

1. Create and activate venv, install dependencies.
2. Install PyInstaller.
3. Run:

```powershell
python -m PyInstaller --name "PDF_A_Converter" --onefile --windowed main.py
```

4. Test the `dist\PDF_A_Converter.exe` on Windows with Ghostscript installed.

If you want, I can also:
- Add a small `build.ps1` script to automate the build steps for PowerShell.
- Suggest `--add-data` lines if you tell me which asset files/folders must be bundled.

---

File created: `README.md`
