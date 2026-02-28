#!/usr/bin/env python3
"""Point d'entrée de l'application desktop Autobot."""

import json
import os
import sys
import threading
import webview

from src.agent import Agent
from src.database import Database
from src.tray import TrayManager
from src.tools import init_tools


def resource_path(relative_path: str) -> str:
    """Résout le chemin vers les ressources (dev et PyInstaller)."""
    if hasattr(sys, "_MEIPASS"):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath(os.path.dirname(__file__)), relative_path)


class ChatAPI:
    """API exposée au JavaScript via pywebview js_api."""

    def __init__(self, db: Database):
        self.db = db
        self.agent = Agent(db=db)
        self._window = None

    def set_window(self, window):
        self._window = window

    def send_message(self, text: str):
        """Appelé par JS. Lance le streaming dans un thread worker."""
        thread = threading.Thread(target=self._process, args=(text,), daemon=True)
        thread.start()

    def _process(self, text: str):
        """Thread worker : streame la réponse vers l'UI."""
        try:
            for event in self.agent.chat_stream(text):
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
        self.agent.reset()
        return True


def main():
    # Initialiser la base de données
    db = Database()
    init_tools(db=db)

    # Créer l'API
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

    # Créer le tray manager
    def on_quit():
        window.destroy()

    tray = TrayManager(window=window, on_quit=on_quit)

    # Lancer webview sur le thread principal, tray dans un thread secondaire
    def start_tray():
        tray.run()

    webview.start(func=start_tray, debug=False)

    # Nettoyage
    tray.stop()
    db.close()


if __name__ == "__main__":
    main()
