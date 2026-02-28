import os
import platform
from datetime import datetime
import pyperclip

TOOL_DEFINITIONS = [
    {
        "name": "get_system_info",
        "description": "Retourne des informations sur le système (OS, architecture, date/heure, répertoire courant).",
        "input_schema": {
            "type": "object",
            "properties": {},
            "required": [],
        },
    },
    {
        "name": "clipboard",
        "description": "Lit ou écrit dans le presse-papier du système.",
        "input_schema": {
            "type": "object",
            "properties": {
                "action": {
                    "type": "string",
                    "enum": ["read", "write"],
                    "description": "Action à effectuer : 'read' pour lire, 'write' pour écrire",
                },
                "content": {
                    "type": "string",
                    "description": "Contenu à copier dans le presse-papier (requis pour 'write')",
                },
            },
            "required": ["action"],
        },
    },
]


def get_system_info() -> str:
    """Retourne les informations système."""
    info = {
        "OS": f"{platform.system()} {platform.release()}",
        "Architecture": platform.machine(),
        "Python": platform.python_version(),
        "Date/Heure": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "Répertoire courant": os.getcwd(),
        "Utilisateur": os.getenv("USER") or os.getenv("USERNAME", "inconnu"),
    }
    return "\n".join(f"{k}: {v}" for k, v in info.items())


def clipboard_action(action: str, content: str = None) -> str:
    """Lit ou écrit dans le presse-papier."""
    try:
        if action == "read":
            text = pyperclip.paste()
            return text if text else "(presse-papier vide)"
        elif action == "write":
            if not content:
                return "Erreur: contenu requis pour écrire dans le presse-papier."
            pyperclip.copy(content)
            return "Contenu copié dans le presse-papier."
        else:
            return f"Erreur: action '{action}' inconnue. Utilisez 'read' ou 'write'."
    except Exception as e:
        return f"Erreur presse-papier: {e}"


TOOL_HANDLERS = {
    "get_system_info": lambda args: get_system_info(),
    "clipboard": lambda args: clipboard_action(args["action"], args.get("content")),
}
