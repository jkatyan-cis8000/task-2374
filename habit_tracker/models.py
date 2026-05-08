"""
Data models for habit tracker.

Defines data structures for Habit and LogEntry.
"""

from dataclasses import dataclass, asdict
from datetime import datetime
from typing import Optional


@dataclass
class Habit:
    """Represents a habit to track."""
    
    id: int
    name: str
    description: str = ""
    created_at: str = None
    archived: int = 0
    
    def __post_init__(self):
        """Initialize created_at if not provided."""
        if self.created_at is None:
            self.created_at = datetime.now().isoformat()
    
    def to_dict(self) -> dict:
        """Convert habit to dictionary."""
        return asdict(self)
    
    @staticmethod
    def from_dict(data: dict) -> "Habit":
        """Create Habit from dictionary."""
        return Habit(**data)


@dataclass
class LogEntry:
    """Represents a log entry for habit completion."""
    
    id: int
    habit_id: int
    date: str
    completed: bool
    notes: str = ""
    
    def to_dict(self) -> dict:
        """Convert log entry to dictionary."""
        return asdict(self)
    
    @staticmethod
    def from_dict(data: dict) -> "LogEntry":
        """Create LogEntry from dictionary."""
        return LogEntry(**data)
