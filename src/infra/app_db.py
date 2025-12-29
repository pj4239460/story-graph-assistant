"""
Application Database Infrastructure
Uses SQLite to store application-level settings and metadata (recent projects, etc.)
"""
import sqlite3
import json
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, Optional

class AppDatabase:
    def __init__(self, db_path: str = "app.db"):
        self.db_path = db_path
        self._init_db()

    def _get_connection(self):
        return sqlite3.connect(self.db_path)

    def _init_db(self):
        """Initialize database tables"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            # Settings table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS settings (
                    key TEXT PRIMARY KEY,
                    value TEXT,
                    updated_at TIMESTAMP
                )
            """)
            
            # Recent projects table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS recent_projects (
                    path TEXT PRIMARY KEY,
                    name TEXT,
                    last_opened TIMESTAMP
                )
            """)
            
            # Chat history table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS chat_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    project_id TEXT NOT NULL,
                    role TEXT NOT NULL,
                    content TEXT NOT NULL,
                    created_at TIMESTAMP NOT NULL,
                    FOREIGN KEY (project_id) REFERENCES recent_projects(path)
                )
            """)
            
            # Create index for faster queries
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_chat_project 
                ON chat_history(project_id, created_at)
            """)
            
            conn.commit()

    # --- Settings Operations ---

    def get_setting(self, key: str, default: Any = None) -> Any:
        """Get a setting value"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT value FROM settings WHERE key = ?", (key,))
            row = cursor.fetchone()
            
            if row:
                try:
                    return json.loads(row[0])
                except json.JSONDecodeError:
                    return row[0]
            return default

    def set_setting(self, key: str, value: Any):
        """Set a setting value"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            json_val = json.dumps(value)
            now = datetime.now().isoformat()
            
            cursor.execute("""
                INSERT OR REPLACE INTO settings (key, value, updated_at)
                VALUES (?, ?, ?)
            """, (key, json_val, now))
            conn.commit()

    # --- Recent Projects Operations ---

    def add_recent_project(self, path: str, name: str):
        """Add or update a recent project"""
        # Normalize path
        path = str(Path(path).resolve())
        
        with self._get_connection() as conn:
            cursor = conn.cursor()
            now = datetime.now().isoformat()
            
            cursor.execute("""
                INSERT OR REPLACE INTO recent_projects (path, name, last_opened)
                VALUES (?, ?, ?)
            """, (path, name, now))
            conn.commit()

    def get_recent_projects(self, limit: int = 5) -> List[Dict[str, str]]:
        """Get list of recent projects"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT path, name, last_opened 
                FROM recent_projects 
                ORDER BY last_opened DESC 
                LIMIT ?
            """, (limit,))
            
            projects = []
            for row in cursor.fetchall():
                projects.append({
                    "path": row[0],
                    "name": row[1],
                    "last_opened": row[2]
                })
            return projects

    def remove_recent_project(self, path: str):
        """Remove a project from history (e.g. if file not found)"""
        path = str(Path(path).resolve())
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM recent_projects WHERE path = ?", (path,))
            conn.commit()

    # --- Chat History Operations ---

    def save_chat_message(self, project_id: str, role: str, content: str):
        """Save a single chat message"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            now = datetime.now().isoformat()
            
            cursor.execute("""
                INSERT INTO chat_history (project_id, role, content, created_at)
                VALUES (?, ?, ?, ?)
            """, (project_id, role, content, now))
            conn.commit()

    def get_chat_history(self, project_id: str, limit: Optional[int] = None) -> List[Dict[str, str]]:
        """Get chat history for a project"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            if limit:
                cursor.execute("""
                    SELECT role, content, created_at 
                    FROM chat_history 
                    WHERE project_id = ? 
                    ORDER BY created_at DESC 
                    LIMIT ?
                """, (project_id, limit))
            else:
                cursor.execute("""
                    SELECT role, content, created_at 
                    FROM chat_history 
                    WHERE project_id = ? 
                    ORDER BY created_at ASC
                """, (project_id,))
            
            messages = []
            for row in cursor.fetchall():
                messages.append({
                    "role": row[0],
                    "content": row[1],
                    "created_at": row[2]
                })
            
            # Reverse if we used LIMIT (to get most recent first, then reverse to chronological)
            if limit:
                messages.reverse()
            
            return messages

    def clear_chat_history(self, project_id: str):
        """Clear all chat history for a project"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM chat_history WHERE project_id = ?", (project_id,))
            conn.commit()

    def get_chat_count(self, project_id: str) -> int:
        """Get total number of messages for a project"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT COUNT(*) FROM chat_history WHERE project_id = ?
            """, (project_id,))
            return cursor.fetchone()[0]
