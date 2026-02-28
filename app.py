#!/usr/bin/env python3
"""Point d'entrée de l'application desktop Autobot."""

import json
import os
import sys
import threading
import webbrowser
import webview

from src.database import Database
from src.tray import TrayManager
from src.tools import init_tools


def resource_path(relative_path: str) -> str:
    """Résout le chemin vers les ressources (dev et PyInstaller)."""
    if hasattr(sys, "_MEIPASS"):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath(os.path.dirname(__file__)), relative_path)


def get_env_path() -> str:
    """Retourne le chemin du fichier .env."""
    if hasattr(sys, "_MEIPASS"):
        from src.config import DATA_DIR
        return os.path.join(DATA_DIR, ".env")
    return os.path.join(os.path.abspath(os.path.dirname(__file__)), ".env")


def has_api_key() -> bool:
    """Vérifie si la clé API est configurée."""
    if os.getenv("ANTHROPIC_API_KEY"):
        return True
    env_path = get_env_path()
    if os.path.exists(env_path):
        with open(env_path, "r") as f:
            for line in f:
                if line.strip().startswith("ANTHROPIC_API_KEY="):
                    value = line.strip().split("=", 1)[1].strip()
                    if value and value != "sk-ant-xxxxx":
                        return True
    return False


class SetupAPI:
    """API pour l'écran de configuration initiale."""

    def __init__(self):
        self._window = None
        self.key_saved = False

    def set_window(self, window):
        self._window = window

    def save_api_key(self, key: str):
        """Sauvegarde la clé API dans le fichier .env."""
        try:
            env_path = get_env_path()
            os.makedirs(os.path.dirname(env_path) or ".", exist_ok=True)
            with open(env_path, "w") as f:
                f.write(f"ANTHROPIC_API_KEY={key}\n")
            os.environ["ANTHROPIC_API_KEY"] = key
            self.key_saved = True
            if self._window:
                threading.Timer(0.5, self._window.destroy).start()
            return True
        except Exception as e:
            return str(e)

    def open_link(self, url: str):
        """Ouvre un lien dans le navigateur."""
        webbrowser.open(url)


class ChatAPI:
    """API exposée au JavaScript via pywebview js_api."""

    def __init__(self, db: Database):
        self.db = db
        self._window = None
        self._agent = None

    def _get_agent(self):
        if self._agent is None:
            from src.agent import Agent
            self._agent = Agent(db=self.db)
        return self._agent

    def set_window(self, window):
        self._window = window

    def send_message(self, text: str):
        """Appelé par JS. Lance le streaming dans un thread worker."""
        thread = threading.Thread(target=self._process, args=(text,), daemon=True)
        thread.start()

    def _process(self, text: str):
        """Thread worker : streame la réponse vers l'UI."""
        try:
            agent = self._get_agent()
            for event in agent.chat_stream(text):
                if self._window is None:
                    break

                if event["type"] == "token":
                    escaped = json.dumps(event["text"])
                    self._window.evaluate_js(f"receiveToken({escaped})")

                elif event["type"] == "tool_start":
                    payload = json.dumps({"name": event["name"]})
                    self._window.evaluate_js(f"toolStart({payload})")

                elif event["type"] == "tool_result":
                    payload = json.dumps({
                        "name": event["name"],
                        "result": event["result"][:200],
                    })
                    self._window.evaluate_js(f"toolResult({payload})")

                elif event["type"] == "done":
                    self._window.evaluate_js("responseComplete()")

        except Exception as e:
            error_msg = json.dumps(str(e))
            if self._window:
                self._window.evaluate_js(f"streamError({error_msg})")

    def get_history(self):
        """Retourne la liste des conversations récentes."""
        return self.db.list_conversations(limit=20)

    def load_conversation(self, conversation_id: int):
        """Charge les messages d'une conversation."""
        return self.db.get_conversation_messages(conversation_id)

    def new_conversation(self):
        """Démarre une nouvelle conversation."""
        if self._agent:
            self._agent.reset()
        return True


def run_setup() -> bool:
    """Affiche l'écran de configuration. Retourne True si la clé a été sauvegardée."""
    setup_api = SetupAPI()
    window = webview.create_window(
        title="Autobot — Configuration",
        url=resource_path("ui/setup.html"),
        js_api=setup_api,
        width=420,
        height=480,
        resizable=False,
    )
    setup_api.set_window(window)
    webview.start()
    return setup_api.key_saved


def main():
    # Vérifier la clé API — afficher le setup si nécessaire
    if not has_api_key():
        if not run_setup():
            return

    # Recharger le .env après setup
    from dotenv import load_dotenv
    load_dotenv(get_env_path(), override=True)

    # Initialiser la base de données et les outils
    db = Database()
    init_tools(db=db)

    # Créer l'API chat (l'agent est créé en lazy à la première requête)
    api = ChatAPI(db=db)

    # Créer la fenêtre
    window = webview.create_window(
        title="Autobot",
        url=resource_path("ui/index.html"),
        js_api=api,
        width=420,
        height=650,
        resizable=True,
        on_top=False,
        confirm_close=False,
    )
    api.set_window(window)

    # System tray
    def on_quit():
        window.destroy()

    tray = TrayManager(window=window, on_quit=on_quit)

    def start_tray():
        tray.run()

    webview.start(func=start_tray, debug=False)

    # Nettoyage
    tray.stop()
    db.close()


if __name__ == "__main__":
    main()
