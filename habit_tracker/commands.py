"""
CLI command handlers for habit tracker.

Contains functions for all user-facing operations.
"""

from typing import Optional, List, Dict
from datetime import datetime
from .database import Database
from .utils import calculate_current_streak, calculate_longest_streak, get_today, get_habit_stats


class HabitTrackerCommands:
    """Handler for all CLI commands."""
    
    def __init__(self, db: Database):
        """Initialize commands with database."""
        self.db = db
    
    def add_habit(self, name: str, description: str = "") -> str:
        """
        Add a new habit.
        
        Args:
            name: Name of the habit
            description: Optional description
            
        Returns:
            Success message
        """
        try:
            habit_id = self.db.create_habit(name, description)
            return f"✓ Habit '{name}' created successfully (ID: {habit_id})"
        except Exception as e:
            return f"✗ Error: {str(e)}"
    
    def list_habits(self, include_archived: bool = False) -> str:
        """
        List all habits.
        
        Args:
            include_archived: Whether to include archived habits
            
        Returns:
            Formatted list of habits
        """
        habits = self.db.list_habits(include_archived=include_archived)
        
        if not habits:
            return "No habits found."
        
        output = []
        output.append("Active Habits:" if not include_archived else "All Habits:")
        output.append("-" * 50)
        
        for habit in habits:
            streak = calculate_current_streak(self.db, habit['id'])
            status = "archived" if habit['archived'] else "active"
            desc = f" - {habit['description']}" if habit['description'] else ""
            output.append(f"  {habit['name']}{desc} [streak: {streak}] ({status})")
        
        return "\n".join(output)
    
    def delete_habit(self, name: str) -> str:
        """
        Archive/delete a habit.
        
        Args:
            name: Name of the habit to delete
            
        Returns:
            Success or error message
        """
        habit = self.db.get_habit_by_name(name)
        if not habit:
            return f"✗ Habit '{name}' not found"
        
        self.db.delete_habit(habit['id'])
        return f"✓ Habit '{name}' archived"
    
    def log_completion(self, name: str, date: str = None, completed: bool = True, notes: str = "") -> str:
        """
        Log a habit completion.
        
        Args:
            name: Name of the habit
            date: Date in YYYY-MM-DD format (default: today)
            completed: Whether the habit was completed
            notes: Optional notes
            
        Returns:
            Success or error message
        """
        if date is None:
            date = get_today()
        
        habit = self.db.get_habit_by_name(name)
        if not habit:
            return f"✗ Habit '{name}' not found"
        
        try:
            self.db.add_log_entry(habit['id'], date, completed, notes)
            status = "completed" if completed else "not completed"
            return f"✓ Logged '{name}' as {status} on {date}"
        except Exception as e:
            return f"✗ Error: {str(e)}"
    
    def view_log(self, name: str = None, days: int = 7) -> str:
        """
        View log entries.
        
        Args:
            name: Specific habit name (None for all)
            days: Number of days to show
            
        Returns:
            Formatted log entries
        """
        if name:
            habit = self.db.get_habit_by_name(name)
            if not habit:
                return f"✗ Habit '{name}' not found"
            
            # Get entries for last N days
            entries = self.db.get_log_entries(habit['id'])
            entries = entries[:days]
            
            if not entries:
                return f"No log entries for '{name}'"
            
            output = [f"Log entries for '{name}' (last {days} days):"]
            output.append("-" * 50)
            
            for entry in entries:
                status = "✓" if entry['completed'] else "✗"
                notes = f" ({entry['notes']})" if entry['notes'] else ""
                output.append(f"  {entry['date']}: {status}{notes}")
            
            return "\n".join(output)
        else:
            # Show all habits' recent logs
            today = get_today()
            entries = self.db.get_logs_by_date(today)
            
            if not entries:
                return f"No log entries for {today}"
            
            output = [f"Today's log entries ({today}):"]
            output.append("-" * 50)
            
            for entry in entries:
                status = "✓" if entry['completed'] else "✗"
                output.append(f"  {entry['name']}: {status}")
            
            return "\n".join(output)
    
    def view_streak(self, name: str) -> str:
        """
        View streak information for a habit.
        
        Args:
            name: Name of the habit
            
        Returns:
            Formatted streak information
        """
        habit = self.db.get_habit_by_name(name)
        if not habit:
            return f"✗ Habit '{name}' not found"
        
        stats = get_habit_stats(self.db, habit['id'])
        
        output = [f"Streak for '{name}':"]
        output.append("-" * 50)
        output.append(f"  Current Streak: {stats['current_streak']} days")
        output.append(f"  Longest Streak: {stats['longest_streak']} days")
        output.append(f"  Total Completions: {stats['total_completions']}")
        
        return "\n".join(output)
