"""Package d'outils pour l'agent IA."""

from src.tools import filesystem, system, web, productivity

# Agrégation de toutes les définitions d'outils
TOOL_DEFINITIONS = (
    filesystem.TOOL_DEFINITIONS
    + system.TOOL_DEFINITIONS
    + web.TOOL_DEFINITIONS
    + productivity.TOOL_DEFINITIONS
)

# Agrégation de tous les handlers
TOOL_HANDLERS = {
    **filesystem.TOOL_HANDLERS,
    **system.TOOL_HANDLERS,
    **web.TOOL_HANDLERS,
    **productivity.TOOL_HANDLERS,
}


def execute_tool(name: str, args: dict) -> str:
    """Exécute un outil par son nom avec les arguments donnés."""
    handler = TOOL_HANDLERS.get(name)
    if handler is None:
        return f"Outil inconnu: {name}"
    return handler(args)


def init_tools(db=None):
    """Initialise les outils qui nécessitent des dépendances (DB, etc.)."""
    if db:
        productivity.init_db(db)
