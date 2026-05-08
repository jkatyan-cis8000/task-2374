"""
CSV export functionality for habit tracker.

Handles exporting habit data and logs to CSV files.
"""

import csv
from datetime import datetime
from pathlib import Path
from typing import Optional
from .database import Database
from .utils import get_date_range


class HabitExporter:
    """Handler for CSV export operations."""
    
    def __init__(self, db: Database, output_dir: str = "."):
        """
        Initialize exporter.
        
        Args:
            db: Database instance
            output_dir: Directory for output files
        """
        self.db = db
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
    
    def export_habits(self, filename: str = None) -> str:
        """
        Export all habits to CSV.
        
        Args:
            filename: Optional custom filename
            
        Returns:
            Path to exported file
        """
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"habits_{timestamp}.csv"
        
        filepath = self.output_dir / filename
        habits = self.db.list_habits(include_archived=True)
        
        if not habits:
            raise ValueError("No habits to export")
        
        with open(filepath, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=['id', 'name', 'description', 'created_at', 'archived'])
            writer.writeheader()
            writer.writerows(habits)
        
        return str(filepath)
    
    def export_logs(self, start_date: str, end_date: str, filename: str = None) -> str:
        """
        Export log entries for a date range to CSV.
        
        Args:
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            filename: Optional custom filename
            
        Returns:
            Path to exported file
        """
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"logs_{start_date}_to_{end_date}_{timestamp}.csv"
        
        filepath = self.output_dir / filename
        
        # Get all habits and their logs for the date range
        habits = self.db.list_habits(include_archived=False)
        rows = []
        
        for habit in habits:
            logs = self.db.get_log_entries(habit['id'], start_date, end_date)
            for log in logs:
                rows.append({
                    'date': log['date'],
                    'habit': habit['name'],
                    'completed': 'Yes' if log['completed'] else 'No',
                    'notes': log['notes']
                })
        
        if not rows:
            raise ValueError("No log entries found for the specified date range")
        
        with open(filepath, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=['date', 'habit', 'completed', 'notes'])
            writer.writeheader()
            writer.writerows(rows)
        
        return str(filepath)
    
    def export_streaks(self, filename: str = None) -> str:
        """
        Export streak summaries to CSV.
        
        Args:
            filename: Optional custom filename
            
        Returns:
            Path to exported file
        """
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"streaks_{timestamp}.csv"
        
        filepath = self.output_dir / filename
        habits = self.db.list_habits(include_archived=False)
        
        from .utils import calculate_current_streak, calculate_longest_streak
        
        rows = []
        for habit in habits:
            from .utils import get_habit_stats
            stats = get_habit_stats(self.db, habit['id'])
            rows.append({
                'habit': habit['name'],
                'current_streak': stats['current_streak'],
                'longest_streak': stats['longest_streak'],
                'total_completions': stats['total_completions']
            })
        
        if not rows:
            raise ValueError("No habits to export")
        
        with open(filepath, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=['habit', 'current_streak', 'longest_streak', 'total_completions'])
            writer.writeheader()
            writer.writerows(rows)
        
        return str(filepath)
