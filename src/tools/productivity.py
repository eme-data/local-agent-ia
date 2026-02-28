from src.database import Database

# Instance globale de la DB, initialisée par init_db()
_db: Database | None = None


def init_db(db: Database):
    """Initialise la référence à la base de données."""
    global _db
    _db = db


TOOL_DEFINITIONS = [
    {
        "name": "manage_notes",
        "description": "Gère les notes de l'utilisateur. Actions: create (créer), list (lister), read (lire), update (modifier), delete (supprimer).",
        "input_schema": {
            "type": "object",
            "properties": {
                "action": {
                    "type": "string",
                    "enum": ["create", "list", "read", "update", "delete"],
                    "description": "L'action à effectuer",
                },
                "title": {
                    "type": "string",
                    "description": "Titre de la note (pour create/update)",
                },
                "content": {
                    "type": "string",
                    "description": "Contenu de la note (pour create/update)",
                },
                "note_id": {
                    "type": "integer",
                    "description": "ID de la note (pour read/update/delete)",
                },
            },
            "required": ["action"],
        },
    },
    {
        "name": "manage_reminders",
        "description": "Gère les rappels. Actions: create (créer), list (lister), complete (marquer comme fait), delete (supprimer).",
        "input_schema": {
            "type": "object",
            "properties": {
                "action": {
                    "type": "string",
                    "enum": ["create", "list", "complete", "delete"],
                    "description": "L'action à effectuer",
                },
                "text": {
                    "type": "string",
                    "description": "Texte du rappel (pour create)",
                },
                "due_date": {
                    "type": "string",
                    "description": "Date d'échéance au format YYYY-MM-DD HH:MM (pour create)",
                },
                "reminder_id": {
                    "type": "integer",
                    "description": "ID du rappel (pour complete/delete)",
                },
            },
            "required": ["action"],
        },
    },
]


def manage_notes(action: str, title: str = None, content: str = None, note_id: int = None) -> str:
    """Gère les notes."""
    if _db is None:
        return "Erreur: base de données non initialisée."

    if action == "create":
        if not title:
            return "Erreur: titre requis pour créer une note."
        nid = _db.create_note(title, content or "")
        return f"Note #{nid} créée : '{title}'"

    elif action == "list":
        notes = _db.list_notes()
        if not notes:
            return "Aucune note."
        lines = []
        for n in notes:
            preview = n["content"][:80] + "..." if len(n["content"]) > 80 else n["content"]
            lines.append(f"#{n['id']} - {n['title']} ({n['updated_at']})\n   {preview}")
        return "\n\n".join(lines)

    elif action == "read":
        if note_id is None:
            return "Erreur: note_id requis pour lire une note."
        note = _db.get_note(note_id)
        if not note:
            return f"Erreur: note #{note_id} introuvable."
        return f"# {note['title']}\n\n{note['content']}\n\n(Créée: {note['created_at']}, Modifiée: {note['updated_at']})"

    elif action == "update":
        if note_id is None:
            return "Erreur: note_id requis pour modifier une note."
        if not _db.update_note(note_id, title=title, content=content):
            return f"Erreur: note #{note_id} introuvable."
        return f"Note #{note_id} mise à jour."

    elif action == "delete":
        if note_id is None:
            return "Erreur: note_id requis pour supprimer une note."
        if not _db.delete_note(note_id):
            return f"Erreur: note #{note_id} introuvable."
        return f"Note #{note_id} supprimée."

    return f"Erreur: action '{action}' inconnue."


def manage_reminders(action: str, text: str = None, due_date: str = None, reminder_id: int = None) -> str:
    """Gère les rappels."""
    if _db is None:
        return "Erreur: base de données non initialisée."

    if action == "create":
        if not text:
            return "Erreur: texte requis pour créer un rappel."
        rid = _db.create_reminder(text, due_date)
        due_info = f" (échéance: {due_date})" if due_date else ""
        return f"Rappel #{rid} créé : '{text}'{due_info}"

    elif action == "list":
        reminders = _db.list_reminders()
        if not reminders:
            return "Aucun rappel en cours."
        lines = []
        for r in reminders:
            status = "✅" if r["completed"] else "⏳"
            due = f" — échéance: {r['due_at']}" if r["due_at"] else ""
            lines.append(f"{status} #{r['id']} - {r['text']}{due}")
        return "\n".join(lines)

    elif action == "complete":
        if reminder_id is None:
            return "Erreur: reminder_id requis."
        if not _db.complete_reminder(reminder_id):
            return f"Erreur: rappel #{reminder_id} introuvable."
        return f"Rappel #{reminder_id} marqué comme terminé."

    elif action == "delete":
        if reminder_id is None:
            return "Erreur: reminder_id requis."
        if not _db.delete_reminder(reminder_id):
            return f"Erreur: rappel #{reminder_id} introuvable."
        return f"Rappel #{reminder_id} supprimé."

    return f"Erreur: action '{action}' inconnue."


TOOL_HANDLERS = {
    "manage_notes": lambda args: manage_notes(
        args["action"],
        title=args.get("title"),
        content=args.get("content"),
        note_id=args.get("note_id"),
    ),
    "manage_reminders": lambda args: manage_reminders(
        args["action"],
        text=args.get("text"),
        due_date=args.get("due_date"),
        reminder_id=args.get("reminder_id"),
    ),
}
