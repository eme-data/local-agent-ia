#!/usr/bin/env python3
"""Script de build pour créer l'exécutable avec PyInstaller."""

import os
import platform
import subprocess
import sys


def generate_icons():
    """Génère les icônes si elles n'existent pas."""
    ico_path = os.path.join("ui", "assets", "icon.ico")
    if not os.path.exists(ico_path):
        print("Génération des icônes...")
        subprocess.run(
            [sys.executable, os.path.join("scripts", "generate_icon.py")],
            check=True,
        )


def build():
    generate_icons()

    system = platform.system()
    separator = ";" if system == "Windows" else ":"

    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--name", "Autobot",
        "--windowed",
        "--onefile",
        "--add-data", f"ui{separator}ui",
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
    ico_path = os.path.join("ui", "assets", "icon.ico")
    icns_path = os.path.join("ui", "assets", "icon.icns")

    if system == "Windows" and os.path.exists(ico_path):
        cmd.extend(["--icon", ico_path])
    elif system == "Darwin" and os.path.exists(icns_path):
        cmd.extend([
            "--icon", icns_path,
            "--osx-bundle-identifier", "com.autobot.app",
        ])

    print(f"Build pour {system}...")
    print(f"Commande : {' '.join(cmd)}")
    subprocess.run(cmd, check=True)
    print("\nBuild terminé ! L'exécutable est dans le dossier dist/")


if __name__ == "__main__":
    build()
