#!/usr/bin/env python3
"""Script de build pour créer l'exécutable avec PyInstaller."""

import platform
import subprocess
import sys


def build():
    system = platform.system()
    separator = ";" if system == "Windows" else ":"

    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--name", "Autobot",
        "--windowed",
        "--onefile",
        f"--add-data", f"ui{separator}ui",
        "--hidden-import", "webview",
        "--hidden-import", "pystray",
        "--hidden-import", "clr_loader",
        "--hidden-import", "pythonnet",
        "--collect-all", "pywebview",
        "--noconfirm",
        "--clean",
        "app.py",
    ]

    # Icônes spécifiques à la plateforme
    if system == "Windows":
        cmd.extend(["--icon", "ui/assets/icon.ico"])
    elif system == "Darwin":
        cmd.extend([
            "--icon", "ui/assets/icon.icns",
            "--osx-bundle-identifier", "com.autobot.app",
        ])

    print(f"Build pour {system}...")
    print(f"Commande : {' '.join(cmd)}")
    subprocess.run(cmd, check=True)
    print("\nBuild terminé ! L'exécutable est dans le dossier dist/")


if __name__ == "__main__":
    build()
