import os
import platform
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
MODEL = "claude-sonnet-4-20250514"
MAX_TOKENS = 8096

# Répertoire de données (platform-aware)
if platform.system() == "Windows":
    DATA_DIR = os.path.join(os.environ.get("APPDATA", "."), "Autobot")
elif platform.system() == "Darwin":
    DATA_DIR = os.path.expanduser("~/Library/Application Support/Autobot")
else:
    DATA_DIR = os.path.expanduser("~/.local/share/Autobot")

os.makedirs(DATA_DIR, exist_ok=True)
DB_PATH = os.path.join(DATA_DIR, "agent.db")


def get_system_prompt() -> str:
    """Retourne le prompt système avec la date/heure actuelle."""
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return f"""Tu es Autobot, un assistant IA local qui aide l'utilisateur dans son quotidien.
Tu te présentes sous le nom Autobot.
Tu peux exécuter des commandes système, lire et écrire des fichiers, effectuer des recherches web,
gérer des notes et des rappels, et accéder au presse-papier.
Tu réponds en français par défaut. Tu es concis et efficace.
Tu as accès à des outils que tu peux utiliser pour accomplir des tâches concrètes.

Date et heure actuelles : {now}

Les notes et rappels sont persistants entre les sessions.
Quand l'utilisateur te demande de noter quelque chose ou de créer un rappel,
utilise les outils manage_notes et manage_reminders."""
