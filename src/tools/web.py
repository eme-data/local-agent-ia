from duckduckgo_search import DDGS

TOOL_DEFINITIONS = [
    {
        "name": "web_search",
        "description": "Effectue une recherche web et retourne les résultats (titres, liens, descriptions).",
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "La requête de recherche",
                },
                "max_results": {
                    "type": "integer",
                    "description": "Nombre maximum de résultats (défaut: 5)",
                    "default": 5,
                },
            },
            "required": ["query"],
        },
    },
]


def web_search(query: str, max_results: int = 5) -> str:
    """Effectue une recherche web via DuckDuckGo."""
    try:
        results = DDGS().text(query, max_results=max_results)
        if not results:
            return "Aucun résultat trouvé."
        formatted = []
        for r in results:
            formatted.append(f"**{r['title']}**\n{r['href']}\n{r['body']}")
        return "\n\n---\n\n".join(formatted)
    except Exception as e:
        return f"Erreur de recherche: {e}"


TOOL_HANDLERS = {
    "web_search": lambda args: web_search(args["query"], args.get("max_results", 5)),
}
