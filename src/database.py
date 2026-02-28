import json
import sqlite3
from datetime import datetime
from src.config import DB_PATH


class Database:
    """Couche de persistance SQLite pour l'agent."""

    def __init__(self, db_path: str = None):
        self.db_path = db_path or DB_PATH
        self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self.conn.execute("PRAGMA journal_mode=WAL")
        self.conn.execute("PRAGMA foreign_keys=ON")
        self._init_schema()

    def _init_schema(self):
        self.conn.executescript("""
            CREATE TABLE IF NOT EXISTS conversations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                conversation_id INTEGER NOT NULL,
                role TEXT NOT NULL,
                content TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (conversation_id) REFERENCES conversations(id) ON DELETE CASCADE
            );

            CREATE TABLE IF NOT EXISTS notes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                content TEXT DEFAULT '',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS reminders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                text TEXT NOT NULL,
                due_at TIMESTAMP,
                completed INTEGER DEFAULT 0,
                notified INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS preferences (
                key TEXT PRIMARY KEY,
                value TEXT
            );
        """)
        self.conn.commit()

    # --- Conversations ---

    def create_conversation(self, title: str = None) -> int:
        cursor = self.conn.execute(
            "INSERT INTO conversations (title) VALUES (?)",
            (title,),
        )
        self.conn.commit()
        return cursor.lastrowid

    def save_message(self, conversation_id: int, role: str, content) -> int:
        serialized = json.dumps(content, ensure_ascii=False) if not isinstance(content, str) else content
        cursor = self.conn.execute(
            "INSERT INTO messages (conversation_id, role, content) VALUES (?, ?, ?)",
            (conversation_id, role, serialized),
        )
        self.conn.execute(
            "UPDATE conversations SET updated_at = ? WHERE id = ?",
            (datetime.now().isoformat(), conversation_id),
        )
        self.conn.commit()
        return cursor.lastrowid

    def get_conversation_messages(self, conversation_id: int) -> list[dict]:
        rows = self.conn.execute(
            "SELECT role, content, created_at FROM messages WHERE conversation_id = ? ORDER BY id",
            (conversation_id,),
        ).fetchall()
        results = []
        for row in rows:
            content = row["content"]
            try:
                content = json.loads(content)
            except (json.JSONDecodeError, TypeError):
                pass
            results.append({
                "role": row["role"],
                "content": content,
                "created_at": row["created_at"],
            })
        return results

    def list_conversations(self, limit: int = 20) -> list[dict]:
        rows = self.conn.execute(
            "SELECT id, title, created_at, updated_at FROM conversations ORDER BY updated_at DESC LIMIT ?",
            (limit,),
        ).fetchall()
        return [dict(row) for row in rows]

    def delete_conversation(self, conversation_id: int):
        self.conn.execute("DELETE FROM conversations WHERE id = ?", (conversation_id,))
        self.conn.commit()

    # --- Notes ---

    def create_note(self, title: str, content: str = "") -> int:
        cursor = self.conn.execute(
            "INSERT INTO notes (title, content) VALUES (?, ?)",
            (title, content),
        )
        self.conn.commit()
        return cursor.lastrowid

    def get_note(self, note_id: int) -> dict | None:
        row = self.conn.execute("SELECT * FROM notes WHERE id = ?", (note_id,)).fetchone()
        return dict(row) if row else None

    def list_notes(self) -> list[dict]:
        rows = self.conn.execute("SELECT * FROM notes ORDER BY updated_at DESC").fetchall()
        return [dict(row) for row in rows]

    def update_note(self, note_id: int, title: str = None, content: str = None):
        note = self.get_note(note_id)
        if not note:
            return False
        self.conn.execute(
            "UPDATE notes SET title = ?, content = ?, updated_at = ? WHERE id = ?",
            (
                title if title is not None else note["title"],
                content if content is not None else note["content"],
                datetime.now().isoformat(),
                note_id,
            ),
        )
        self.conn.commit()
        return True

    def delete_note(self, note_id: int) -> bool:
        cursor = self.conn.execute("DELETE FROM notes WHERE id = ?", (note_id,))
        self.conn.commit()
        return cursor.rowcount > 0

    # --- Rappels ---

    def create_reminder(self, text: str, due_at: str = None) -> int:
        cursor = self.conn.execute(
            "INSERT INTO reminders (text, due_at) VALUES (?, ?)",
            (text, due_at),
        )
        self.conn.commit()
        return cursor.lastrowid

    def list_reminders(self, include_completed: bool = False) -> list[dict]:
        if include_completed:
            rows = self.conn.execute("SELECT * FROM reminders ORDER BY due_at").fetchall()
        else:
            rows = self.conn.execute(
                "SELECT * FROM reminders WHERE completed = 0 ORDER BY due_at"
            ).fetchall()
        return [dict(row) for row in rows]

    def complete_reminder(self, reminder_id: int) -> bool:
        cursor = self.conn.execute(
            "UPDATE reminders SET completed = 1 WHERE id = ?", (reminder_id,)
        )
        self.conn.commit()
        return cursor.rowcount > 0

    def delete_reminder(self, reminder_id: int) -> bool:
        cursor = self.conn.execute("DELETE FROM reminders WHERE id = ?", (reminder_id,))
        self.conn.commit()
        return cursor.rowcount > 0

    def get_due_reminders(self) -> list[dict]:
        now = datetime.now().isoformat()
        rows = self.conn.execute(
            "SELECT * FROM reminders WHERE completed = 0 AND notified = 0 AND due_at <= ?",
            (now,),
        ).fetchall()
        return [dict(row) for row in rows]

    def mark_notified(self, reminder_id: int):
        self.conn.execute(
            "UPDATE reminders SET notified = 1 WHERE id = ?", (reminder_id,)
        )
        self.conn.commit()

    # --- Préférences ---

    def set_preference(self, key: str, value) -> None:
        serialized = json.dumps(value, ensure_ascii=False)
        self.conn.execute(
            "INSERT OR REPLACE INTO preferences (key, value) VALUES (?, ?)",
            (key, serialized),
        )
        self.conn.commit()

    def get_preference(self, key: str, default=None):
        row = self.conn.execute("SELECT value FROM preferences WHERE key = ?", (key,)).fetchone()
        if row is None:
            return default
        try:
            return json.loads(row["value"])
        except (json.JSONDecodeError, TypeError):
            return default

    def close(self):
        self.conn.close()
