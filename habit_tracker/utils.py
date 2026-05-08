"""
Utility functions for habit tracker.

Contains helper functions for streak calculations, date queries, and formatting.
"""

from datetime import datetime, timedelta
from typing import List, Tuple
from .database import Database


def calculate_current_streak(db: Database, habit_id: int) -> int:
    """
    Calculate the current streak for a habit.
    
    Args:
        db: Database instance
        habit_id: ID of the habit
        
    Returns:
        Number of consecutive days completed (ending today or yesterday)
    """
    dates = db.get_completion_streak(habit_id)
    if not dates:
        return 0
    
    today = datetime.now().date()
    streak = 0
    
    for date_str in dates:
        date = datetime.strptime(date_str, "%Y-%m-%d").date()
        
        # Check if this is today or yesterday minus streak days
        expected_date = today - timedelta(days=streak)
        if date == expected_date:
            streak += 1
        else:
            break
    
    return streak


def calculate_longest_streak(db: Database, habit_id: int) -> int:
    """
    Calculate the longest streak ever for a habit.
    
    Args:
        db: Database instance
        habit_id: ID of the habit
        
    Returns:
        Length of the longest streak
    """
    dates = db.get_completion_streak(habit_id)
    if not dates:
        return 0
    
    # Reverse to go chronologically
    dates = list(reversed(dates))
    
    longest = 0
    current = 0
    last_date = None
    
    for date_str in dates:
        date = datetime.strptime(date_str, "%Y-%m-%d").date()
        
        if last_date is None:
            current = 1
        elif date == last_date + timedelta(days=1):
            current += 1
        else:
            longest = max(longest, current)
            current = 1
        
        last_date = date
    
    longest = max(longest, current)
    return longest


def get_date_range(start_date: str, end_date: str) -> List[str]:
    """
    Get a list of dates in a range (inclusive).
    
    Args:
        start_date: Start date (YYYY-MM-DD)
        end_date: End date (YYYY-MM-DD)
        
    Returns:
        List of date strings in format YYYY-MM-DD
    """
    start = datetime.strptime(start_date, "%Y-%m-%d").date()
    end = datetime.strptime(end_date, "%Y-%m-%d").date()
    
    dates = []
    current = start
    while current <= end:
        dates.append(current.isoformat())
        current += timedelta(days=1)
    
    return dates


def format_date(date_obj) -> str:
    """Format a date object to YYYY-MM-DD string."""
    if isinstance(date_obj, str):
        return date_obj
    return date_obj.isoformat()


def get_today() -> str:
    """Get today's date as YYYY-MM-DD string."""
    return datetime.now().date().isoformat()


def get_habit_stats(db: Database, habit_id: int) -> dict:
    """
    Get statistics for a habit.
    
    Args:
        db: Database instance
        habit_id: ID of the habit
        
    Returns:
        Dictionary with current_streak, longest_streak, total_completions
    """
    current_streak = calculate_current_streak(db, habit_id)
    longest_streak = calculate_longest_streak(db, habit_id)
    
    entries = db.get_log_entries(habit_id)
    total_completions = sum(1 for entry in entries if entry['completed'])
    
    return {
        "current_streak": current_streak,
        "longest_streak": longest_streak,
        "total_completions": total_completions
    }
