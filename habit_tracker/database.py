"""
Database module for SQLite operations.

Handles all database interactions for habits and log entries.
"""

import sqlite3
from contextlib import contextmanager
from datetime import datetime
from pathlib import Path


class Database:
    """SQLite database handler for the habit tracker."""

    def __init__(self, db_path: str = "habit_tracker.db"):
        """Initialize database connection."""
        self.db_path = Path(db_path)
        self._init_schema()

    def _init_schema(self) -> None:
        """Initialize database schema if it doesn't exist."""
        with self.connection() as conn:
            cursor = conn.cursor()
            
            # Create habits table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS habits (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT UNIQUE NOT NULL,
                    description TEXT,
                    created_at TIMESTAMP NOT NULL,
                    archived INTEGER DEFAULT 0
                )
            """)
            
            # Create logs table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    habit_id INTEGER NOT NULL,
                    date DATE NOT NULL,
                    completed INTEGER NOT NULL,
                    notes TEXT,
                    FOREIGN KEY (habit_id) REFERENCES habits (id),
                    UNIQUE (habit_id, date)
                )
            """)
            
            conn.commit()

    @contextmanager
    def connection(self):
        """Context manager for database connection."""
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        try:
            yield conn
        finally:
            conn.close()

    def create_habit(self, name: str, description: str = "") -> int:
        """
        Create a new habit.
        
        Args:
            name: Habit name (must be unique)
            description: Optional habit description
            
        Returns:
            The ID of the newly created habit
            
        Raises:
            sqlite3.IntegrityError: If habit name already exists
        """
        with self.connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO habits (name, description, created_at) VALUES (?, ?, ?)",
                (name, description, datetime.now().isoformat())
            )
            conn.commit()
            return cursor.lastrowid

    def get_habit(self, habit_id: int) -> dict:
        """Get a habit by ID."""
        with self.connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM habits WHERE id = ?", (habit_id,))
            row = cursor.fetchone()
            return dict(row) if row else None

    def get_habit_by_name(self, name: str) -> dict:
        """Get a habit by name."""
        with self.connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM habits WHERE name = ? AND archived = 0", (name,))
            row = cursor.fetchone()
            return dict(row) if row else None

    def list_habits(self, include_archived: bool = False) -> list:
        """
        List all habits.
        
        Args:
            include_archived: Whether to include archived habits
            
        Returns:
            List of habit dictionaries
        """
        with self.connection() as conn:
            cursor = conn.cursor()
            if include_archived:
                cursor.execute("SELECT * FROM habits ORDER BY created_at DESC")
            else:
                cursor.execute(
                    "SELECT * FROM habits WHERE archived = 0 ORDER BY created_at DESC"
                )
            return [dict(row) for row in cursor.fetchall()]

    def delete_habit(self, habit_id: int) -> None:
        """Archive a habit (soft delete)."""
        with self.connection() as conn:
            cursor = conn.cursor()
            cursor.execute("UPDATE habits SET archived = 1 WHERE id = ?", (habit_id,))
            conn.commit()

    def add_log_entry(self, habit_id: int, date: str, completed: bool, notes: str = "") -> int:
        """
        Add a log entry for a habit.
        
        Args:
            habit_id: ID of the habit
            date: Date in YYYY-MM-DD format
            completed: Whether the habit was completed
            notes: Optional notes
            
        Returns:
            The ID of the newly created log entry
        """
        with self.connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """INSERT OR REPLACE INTO logs (habit_id, date, completed, notes) 
                   VALUES (?, ?, ?, ?)""",
                (habit_id, date, int(completed), notes)
            )
            conn.commit()
            return cursor.lastrowid

    def get_log_entries(self, habit_id: int, start_date: str = None, end_date: str = None) -> list:
        """
        Get log entries for a habit.
        
        Args:
            habit_id: ID of the habit
            start_date: Start date (YYYY-MM-DD), optional
            end_date: End date (YYYY-MM-DD), optional
            
        Returns:
            List of log entry dictionaries
        """
        with self.connection() as conn:
            cursor = conn.cursor()
            
            if start_date and end_date:
                cursor.execute(
                    """SELECT * FROM logs 
                       WHERE habit_id = ? AND date BETWEEN ? AND ?
                       ORDER BY date DESC""",
                    (habit_id, start_date, end_date)
                )
            else:
                cursor.execute(
                    "SELECT * FROM logs WHERE habit_id = ? ORDER BY date DESC",
                    (habit_id,)
                )
            
            return [dict(row) for row in cursor.fetchall()]

    def get_logs_by_date(self, date: str) -> list:
        """Get all log entries for a specific date."""
        with self.connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """SELECT l.*, h.name FROM logs l
                   JOIN habits h ON l.habit_id = h.id
                   WHERE l.date = ? ORDER BY h.name""",
                (date,)
            )
            return [dict(row) for row in cursor.fetchall()]

    def get_completion_streak(self, habit_id: int) -> list:
        """
        Get the current completion streak as a list of dates.
        
        Returns consecutive completion dates from most recent backwards.
        """
        with self.connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """SELECT date FROM logs 
                   WHERE habit_id = ? AND completed = 1
                   ORDER BY date DESC""",
                (habit_id,)
            )
            return [row[0] for row in cursor.fetchall()]
