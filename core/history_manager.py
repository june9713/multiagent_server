"""
History Manager - SQLite-based conversation history management
"""

import sqlite3
import json
from pathlib import Path
from typing import List, Dict, Optional
from datetime import datetime


class HistoryManager:
    """Manages conversation history in SQLite database"""
    
    def __init__(self, db_path: Path):
        self.db_path = db_path
        self._init_db()
    
    def _init_db(self) -> None:
        """Initialize database schema"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Conversations table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS conversations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT NOT NULL,
                agent_id TEXT NOT NULL,
                role TEXT NOT NULL,
                message TEXT NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Sessions table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS sessions (
                session_id TEXT PRIMARY KEY,
                agent_id TEXT NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                last_active DATETIME DEFAULT CURRENT_TIMESTAMP,
                metadata TEXT
            )
        """)
        
        # Indexes
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_session 
            ON conversations(session_id)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_agent 
            ON conversations(agent_id)
        """)
        
        conn.commit()
        conn.close()
    
    def save_message(
        self,
        session_id: str,
        agent_id: str,
        role: str,
        message: str
    ) -> None:
        """Save a message to history"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO conversations (session_id, agent_id, role, message)
            VALUES (?, ?, ?, ?)
        """, (session_id, agent_id, role, message))
        
        # Update session last_active
        cursor.execute("""
            INSERT OR REPLACE INTO sessions (session_id, agent_id, last_active)
            VALUES (?, ?, ?)
        """, (session_id, agent_id, datetime.now()))
        
        conn.commit()
        conn.close()
    
    def load_history(
        self,
        session_id: str,
        limit: int = 50
    ) -> List[Dict]:
        """Load conversation history for a session"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT role, message, timestamp
            FROM conversations
            WHERE session_id = ?
            ORDER BY timestamp DESC
            LIMIT ?
        """, (session_id, limit))
        
        rows = cursor.fetchall()
        conn.close()
        
        # Convert to Gemini format (reversed for chronological order)
        history = []
        for role, message, timestamp in reversed(rows):
            history.append({
                "role": role,
                "parts": [message]
            })
        
        return history
    
    def get_session_info(self, session_id: str) -> Optional[Dict]:
        """Get session information"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT agent_id, created_at, last_active, metadata
            FROM sessions
            WHERE session_id = ?
        """, (session_id,))
        
        row = cursor.fetchone()
        conn.close()
        
        if not row:
            return None
        
        return {
            "agent_id": row[0],
            "created_at": row[1],
            "last_active": row[2],
            "metadata": json.loads(row[3]) if row[3] else {}
        }
    
    def list_sessions(self, agent_id: Optional[str] = None) -> List[Dict]:
        """List all sessions, optionally filtered by agent"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        if agent_id:
            cursor.execute("""
                SELECT session_id, agent_id, created_at, last_active
                FROM sessions
                WHERE agent_id = ?
                ORDER BY last_active DESC
            """, (agent_id,))
        else:
            cursor.execute("""
                SELECT session_id, agent_id, created_at, last_active
                FROM sessions
                ORDER BY last_active DESC
            """)
        
        rows = cursor.fetchall()
        conn.close()
        
        return [
            {
                "session_id": row[0],
                "agent_id": row[1],
                "created_at": row[2],
                "last_active": row[3]
            }
            for row in rows
        ]
