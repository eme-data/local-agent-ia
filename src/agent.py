import anthropic
from src.config import ANTHROPIC_API_KEY, MODEL, MAX_TOKENS, SYSTEM_PROMPT
from src.tools import TOOL_DEFINITIONS, execute_tool


class Agent:
    """Agent conversationnel local connecté à l'API Anthropic."""

    def __init__(self):
        if not ANTHROPIC_API_KEY:
            raise ValueError(
                "ANTHROPIC_API_KEY manquante. "
                "Copie .env.example en .env et ajoute ta clé API."
            )
        self.client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
        self.conversation: list[dict] = []

    def chat(self, user_message: str) -> str:
        """Envoie un message et retourne la réponse de l'agent."""
        self.conversation.append({"role": "user", "content": user_message})

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
        return assistant_text

    def _call_api(self) -> anthropic.types.Message:
        """Appelle l'API Anthropic."""
        return self.client.messages.create(
            model=MODEL,
            max_tokens=MAX_TOKENS,
            system=SYSTEM_PROMPT,
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

    def reset(self):
        """Remet la conversation à zéro."""
        self.conversation = []
