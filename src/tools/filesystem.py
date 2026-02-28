import os
import subprocess
from datetime import datetime

TOOL_DEFINITIONS = [
    {
        "name": "run_command",
        "description": "Exécute une commande système (shell) et retourne le résultat. Utile pour lister des fichiers, installer des paquets, lancer des scripts, etc.",
        "input_schema": {
            "type": "object",
            "properties": {
                "command": {
                    "type": "string",
                    "description": "La commande shell à exécuter",
                }
            },
            "required": ["command"],
        },
    },
    {
        "name": "read_file",
        "description": "Lit le contenu d'un fichier et retourne son texte.",
        "input_schema": {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "Chemin du fichier à lire",
                }
            },
            "required": ["path"],
        },
    },
    {
        "name": "write_file",
        "description": "Écrit du contenu dans un fichier. Crée le fichier s'il n'existe pas, écrase le contenu s'il existe.",
        "input_schema": {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "Chemin du fichier à écrire",
                },
                "content": {
                    "type": "string",
                    "description": "Contenu à écrire dans le fichier",
                },
            },
            "required": ["path", "content"],
        },
    },
    {
        "name": "list_directory",
        "description": "Liste le contenu d'un répertoire avec les détails (taille, date de modification).",
        "input_schema": {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "Chemin du répertoire à lister (défaut: répertoire courant)",
                    "default": ".",
                }
            },
            "required": [],
        },
    },
]


def run_command(command: str) -> str:
    """Exécute une commande shell et retourne le résultat."""
    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=30,
        )
        output = result.stdout
        if result.stderr:
            output += f"\n[stderr]: {result.stderr}"
        if result.returncode != 0:
            output += f"\n[code de retour]: {result.returncode}"
        return output.strip() or "(aucune sortie)"
    except subprocess.TimeoutExpired:
        return "Erreur: la commande a dépassé le délai de 30 secondes."
    except Exception as e:
        return f"Erreur: {e}"


def read_file(path: str) -> str:
    """Lit un fichier et retourne son contenu."""
    try:
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return f"Erreur: fichier '{path}' introuvable."
    except Exception as e:
        return f"Erreur: {e}"


def write_file(path: str, content: str) -> str:
    """Écrit du contenu dans un fichier."""
    try:
        os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        return f"Fichier '{path}' écrit avec succès."
    except Exception as e:
        return f"Erreur: {e}"


def list_directory(path: str = ".") -> str:
    """Liste le contenu d'un répertoire."""
    try:
        entries = []
        for entry in sorted(os.listdir(path)):
            full_path = os.path.join(path, entry)
            stat = os.stat(full_path)
            is_dir = os.path.isdir(full_path)
            size = stat.st_size if not is_dir else "-"
            mtime = datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d %H:%M")
            prefix = "📁" if is_dir else "📄"
            entries.append(f"{prefix} {entry:<40} {str(size):>10}  {mtime}")
        return "\n".join(entries) or "(répertoire vide)"
    except FileNotFoundError:
        return f"Erreur: répertoire '{path}' introuvable."
    except Exception as e:
        return f"Erreur: {e}"


TOOL_HANDLERS = {
    "run_command": lambda args: run_command(args["command"]),
    "read_file": lambda args: read_file(args["path"]),
    "write_file": lambda args: write_file(args["path"], args["content"]),
    "list_directory": lambda args: list_directory(args.get("path", ".")),
}
