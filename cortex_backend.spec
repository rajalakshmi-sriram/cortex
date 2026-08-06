# PyInstaller spec for the Cortex Flask backend, bundled as a standalone
# binary that the Tauri desktop wrapper spawns as a child process. Build
# with:
#   pyinstaller cortex_backend.spec
# Produces dist/cortex-backend/cortex-backend (a folder build, not
# --onefile - onefile self-extracts to a temp dir on every launch, which
# is slower to start and unnecessary here since Tauri already ships the
# whole folder as a bundled resource).

import sys
from pathlib import Path

block_cipher = None
project_root = Path(SPECPATH)

a = Analysis(
    ['run_desktop.py'],
    pathex=[str(project_root)],
    binaries=[],
    datas=[],
    hiddenimports=[
        'flask_cors',
        'pandas',
        'openpyxl',
        'numpy',
        'scipy',
        'scipy.stats',
        'matplotlib',
        'matplotlib.backends.backend_agg',
        'sklearn',
        'sklearn.feature_extraction.text',
        'bs4',
        'lxml',
        'feedparser',
        'yaml',
        'dotenv',
    ],
    hookspath=[],
    runtime_hooks=[],
    excludes=['PyQt6', 'PyQt6.QtCore', 'PyQt6.QtWidgets', 'PyQt6.QtGui', 'tkinter'],
    noarchive=False,
    cipher=block_cipher,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='cortex-backend',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=True,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=False,
    name='cortex-backend',
)
