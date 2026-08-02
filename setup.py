"""
Setup script for creating macOS app bundle using py2app
Run: python setup.py py2app
"""

from setuptools import setup
from py2app.build_app import py2app
import sys

APP = ['cortex_gui.py']

DATA_FILES = [
    ('resources', ['resources/cortex_icon.icns']),
]

OPTIONS = {
    'py2app': {
        'argv_emulation': True,
        'packages': [
            'PyQt6',
            'requests',
            'sklearn',
            'numpy',
            'pandas',
        ],
        'includes': [
            'PyQt6.QtCore',
            'PyQt6.QtGui',
            'PyQt6.QtWidgets',
            'PyQt6.QtWebEngineWidgets',
            'requests',
        ],
        'excludes': [
            'matplotlib',
            'scipy',
        ],
        'resources': ['resources/'],
        'plist': {
            'CFBundleName': 'Cortex',
            'CFBundleDisplayName': 'Cortex',
            'CFBundleIdentifier': 'com.cortex-research.cortex',
            'CFBundleVersion': '1.0.0',
            'CFBundleShortVersionString': '1.0.0',
            'NSPrincipalClass': 'NSApplication',
            'NSHighResolutionCapable': True,
            'NSRequiresIPhoneOS': False,
            'LSMinimumSystemVersion': '10.13.0',
        }
    }
}

setup(
    name='Cortex',
    app=APP,
    data_files=DATA_FILES,
    options=OPTIONS,
    setup_requires=['py2app'],
)
