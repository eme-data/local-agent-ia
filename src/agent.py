import os
import anthropic
from src.config import MODEL, MAX_TOKENS, get_system_prompt
from src.tools import TOOL_DEFINITIONS, execute_tool


class Agent:
    """Agent conversationnel local connecté à l'API Anthropic."""

    def __init__(self, db=None):
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            raise ValueError(
                "ANTHROPIC_API_KEY manquante. "
                "Copie .env.example en .env et ajoute ta clé API."
            )
        self.client = anthropic.Anthropic(api_key=api_key)
        self.conversation: list[dict] = []
        self.db = db
        self.conversation_id = None

    def chat(self, user_message: str) -> str:
        """Envoie un message et retourne la réponse (mode synchrone pour le CLI)."""
        self.conversation.append({"role": "user", "content": user_message})
        self._save_message("user", user_message)

        response = self._call_api()

        # Boucle agentic : tant que le modèle veut utiliser des outils
        while response.stop_reason == "tool_use":
            tool_results = self._process_tool_calls(response)
            self.conversation.append({"role": "assistant", "content": response.content})
            self.conversation.append({"role": "user", "content": tool_results})
            response = self._call_api()

        # Extraire le texte final
        assistant_text = self._extract_text(response)
        self.conversation.append({"role": "assistant", "content": response.content})
        self._save_message("assistant", assistant_text)
        return assistant_text

    def chat_stream(self, user_message: str):
        """Générateur qui yield des événements de streaming pour l'UI desktop."""
        self.conversation.append({"role": "user", "content": user_message})
        self._save_message("user", user_message)

        while True:
            with self.client.messages.stream(
                model=MODEL,
                max_tokens=MAX_TOKENS,
                system=get_system_prompt(),
                tools=TOOL_DEFINITIONS,
                messages=self.conversation,
            ) as stream:
                for event in stream:
                    if event.type == "content_block_delta":
                        if hasattr(event.delta, "text"):
                            yield {"type": "token", "text": event.delta.text}

                response = stream.get_final_message()

            if response.stop_reason == "tool_use":
                tool_results = []
                for block in response.content:
                    if block.type == "tool_use":
                        yield {"type": "tool_start", "name": block.name, "input": block.input}
                        result = execute_tool(block.name, block.input)
                        yield {"type": "tool_result", "name": block.name, "result": result}
                        tool_results.append({
                            "type": "tool_result",
                            "tool_use_id": block.id,
                            "content": result,
                        })
                self.conversation.append({"role": "assistant", "content": response.content})
                self.conversation.append({"role": "user", "content": tool_results})
            else:
                assistant_text = self._extract_text(response)
                self.conversation.append({"role": "assistant", "content": response.content})
                self._save_message("assistant", assistant_text)
                yield {"type": "done"}
                break

    def _call_api(self) -> anthropic.types.Message:
        """Appelle l'API Anthropic."""
        return self.client.messages.create(
            model=MODEL,
            max_tokens=MAX_TOKENS,
            system=get_system_prompt(),
            tools=TOOL_DEFINITIONS,
            messages=self.conversation,
        )

    def _process_tool_calls(self, response) -> list[dict]:
        """Traite les appels d'outils et retourne les résultats."""
        results = []
        for block in response.content:
            if block.type == "tool_use":
                tool_result = execute_tool(block.name, block.input)
                results.append(
                    {
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": tool_result,
                    }
                )
        return results

    def _extract_text(self, response) -> str:
        """Extrait le texte d'une réponse."""
        parts = []
        for block in response.content:
            if hasattr(block, "text"):
                parts.append(block.text)
        return "\n".join(parts)

    def _save_message(self, role: str, content):
        """Sauvegarde un message en DB si disponible."""
        if not self.db:
            return
        if self.conversation_id is None:
            title = content[:50] if isinstance(content, str) else "Conversation"
            self.conversation_id = self.db.create_conversation(title)
        self.db.save_message(self.conversation_id, role, content)

    def reset(self):
        """Remet la conversation à zéro."""
        self.conversation = []
        self.conversation_id = None
