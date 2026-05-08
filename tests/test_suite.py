"""Comprehensive test suite for habit tracker."""

import unittest
import tempfile
import os
import sys
import csv
from datetime import datetime, timedelta

# Ensure package is importable
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from habit_tracker.database import Database
from habit_tracker.commands import HabitTrackerCommands
from habit_tracker.models import Habit, LogEntry
from habit_tracker.utils import (
    calculate_current_streak,
    calculate_longest_streak,
    get_date_range,
    format_date,
    get_today,
    get_habit_stats
)
from habit_tracker.export import HabitExporter


class TestDatabase(unittest.TestCase):
    """Test database module."""
    
    def setUp(self):
        """Create a temp database for each test."""
        self.temp_dir = tempfile.TemporaryDirectory()
        self.db_path = os.path.join(self.temp_dir.name, "test.db")
        self.db = Database(self.db_path)
    
    def tearDown(self):
        """Clean up temp database."""
        self.temp_dir.cleanup()
    
    def test_schema_creation(self):
        """Test that database schema is created."""
        with self.db.connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = {row[0] for row in cursor.fetchall()}
            self.assertIn('habits', tables)
            self.assertIn('logs', tables)
    
    def test_create_habit(self):
        """Test creating a habit."""
        habit_id = self.db.create_habit("Morning Jog", "30 min")
        self.assertIsInstance(habit_id, int)
        self.assertGreater(habit_id, 0)
    
    def test_create_duplicate_habit_fails(self):
        """Test that duplicate habit name raises error."""
        self.db.create_habit("Morning Jog")
        with self.assertRaises(Exception):
            self.db.create_habit("Morning Jog")
    
    def test_get_habit(self):
        """Test retrieving habit by ID."""
        habit_id = self.db.create_habit("Morning Jog", "30 min")
        habit = self.db.get_habit(habit_id)
        self.assertIsNotNone(habit)
        self.assertEqual(habit['name'], "Morning Jog")
        self.assertEqual(habit['description'], "30 min")
    
    def test_get_habit_by_name(self):
        """Test retrieving habit by name."""
        self.db.create_habit("Morning Jog")
        habit = self.db.get_habit_by_name("Morning Jog")
        self.assertIsNotNone(habit)
        self.assertEqual(habit['name'], "Morning Jog")
    
    def test_get_nonexistent_habit(self):
        """Test getting nonexistent habit returns None."""
        habit = self.db.get_habit(999)
        self.assertIsNone(habit)
    
    def test_list_habits(self):
        """Test listing habits."""
        self.db.create_habit("Habit 1")
        self.db.create_habit("Habit 2")
        habits = self.db.list_habits()
        self.assertEqual(len(habits), 2)
    
    def test_list_habits_excludes_archived(self):
        """Test that list excludes archived habits by default."""
        id1 = self.db.create_habit("Habit 1")
        id2 = self.db.create_habit("Habit 2")
        self.db.delete_habit(id1)
        
        habits = self.db.list_habits()
        self.assertEqual(len(habits), 1)
        self.assertEqual(habits[0]['name'], "Habit 2")
    
    def test_delete_habit(self):
        """Test soft delete of habit."""
        habit_id = self.db.create_habit("Test")
        self.db.delete_habit(habit_id)
        
        habit = self.db.get_habit(habit_id)
        self.assertEqual(habit['archived'], 1)
    
    def test_add_log_entry(self):
        """Test adding a log entry."""
        habit_id = self.db.create_habit("Test")
        log_id = self.db.add_log_entry(habit_id, "2026-05-08", True)
        self.assertIsInstance(log_id, int)
    
    def test_log_entry_replace(self):
        """Test that log entry updates existing entry."""
        habit_id = self.db.create_habit("Test")
        self.db.add_log_entry(habit_id, "2026-05-08", True, "First")
        self.db.add_log_entry(habit_id, "2026-05-08", False, "Updated")
        
        logs = self.db.get_log_entries(habit_id)
        self.assertEqual(len(logs), 1)
        self.assertEqual(logs[0]['completed'], 0)
        self.assertEqual(logs[0]['notes'], "Updated")
    
    def test_get_log_entries(self):
        """Test retrieving log entries."""
        habit_id = self.db.create_habit("Test")
        self.db.add_log_entry(habit_id, "2026-05-08", True)
        self.db.add_log_entry(habit_id, "2026-05-07", True)
        self.db.add_log_entry(habit_id, "2026-05-06", True)
        
        logs = self.db.get_log_entries(habit_id)
        self.assertEqual(len(logs), 3)
    
    def test_get_logs_by_date(self):
        """Test getting all logs for a date."""
        habit1 = self.db.create_habit("Habit 1")
        habit2 = self.db.create_habit("Habit 2")
        
        self.db.add_log_entry(habit1, "2026-05-08", True)
        self.db.add_log_entry(habit2, "2026-05-08", True)
        
        logs = self.db.get_logs_by_date("2026-05-08")
        self.assertEqual(len(logs), 2)
    
    def test_get_completion_streak(self):
        """Test getting completion dates."""
        habit_id = self.db.create_habit("Test")
        self.db.add_log_entry(habit_id, "2026-05-08", True)
        self.db.add_log_entry(habit_id, "2026-05-07", True)
        self.db.add_log_entry(habit_id, "2026-05-06", False)
        
        dates = self.db.get_completion_streak(habit_id)
        self.assertEqual(len(dates), 2)
        self.assertEqual(dates[0], "2026-05-08")


class TestModels(unittest.TestCase):
    """Test data models."""
    
    def test_habit_creation(self):
        """Test Habit model."""
        habit = Habit(id=1, name="Test", description="Desc")
        self.assertEqual(habit.id, 1)
        self.assertEqual(habit.name, "Test")
        self.assertIsNotNone(habit.created_at)
    
    def test_habit_to_dict(self):
        """Test Habit serialization."""
        habit = Habit(id=1, name="Test", created_at="2026-05-08T10:00:00")
        data = habit.to_dict()
        self.assertIsInstance(data, dict)
        self.assertEqual(data['name'], "Test")
    
    def test_habit_from_dict(self):
        """Test Habit deserialization."""
        data = {'id': 1, 'name': "Test", 'description': "", 'created_at': "2026-05-08T10:00:00", 'archived': 0}
        habit = Habit.from_dict(data)
        self.assertEqual(habit.name, "Test")
    
    def test_log_entry_creation(self):
        """Test LogEntry model."""
        entry = LogEntry(id=1, habit_id=1, date="2026-05-08", completed=True)
        self.assertEqual(entry.habit_id, 1)
        self.assertTrue(entry.completed)
    
    def test_log_entry_to_dict(self):
        """Test LogEntry serialization."""
        entry = LogEntry(id=1, habit_id=1, date="2026-05-08", completed=True)
        data = entry.to_dict()
        self.assertEqual(data['date'], "2026-05-08")


class TestUtils(unittest.TestCase):
    """Test utility functions."""
    
    def setUp(self):
        """Create a temp database for each test."""
        self.temp_dir = tempfile.TemporaryDirectory()
        self.db_path = os.path.join(self.temp_dir.name, "test.db")
        self.db = Database(self.db_path)
    
    def tearDown(self):
        """Clean up temp database."""
        self.temp_dir.cleanup()
    
    def test_calculate_current_streak_empty(self):
        """Test streak with no data."""
        habit_id = self.db.create_habit("Test")
        streak = calculate_current_streak(self.db, habit_id)
        self.assertEqual(streak, 0)
    
    def test_calculate_current_streak_today(self):
        """Test streak with today's completion."""
        habit_id = self.db.create_habit("Test")
        today = datetime.now().date().isoformat()
        self.db.add_log_entry(habit_id, today, True)
        
        streak = calculate_current_streak(self.db, habit_id)
        self.assertEqual(streak, 1)
    
    def test_calculate_current_streak_consecutive(self):
        """Test consecutive days streak."""
        habit_id = self.db.create_habit("Test")
        today = datetime.now().date()
        
        for i in range(5):
            date = (today - timedelta(days=i)).isoformat()
            self.db.add_log_entry(habit_id, date, True)
        
        streak = calculate_current_streak(self.db, habit_id)
        self.assertEqual(streak, 5)
    
    def test_calculate_current_streak_with_gap(self):
        """Test streak stops at gap."""
        habit_id = self.db.create_habit("Test")
        today = datetime.now().date()
        
        # 2 consecutive days
        self.db.add_log_entry(habit_id, today.isoformat(), True)
        self.db.add_log_entry(habit_id, (today - timedelta(days=1)).isoformat(), True)
        # Gap on day 2
        # 3 more days before gap
        self.db.add_log_entry(habit_id, (today - timedelta(days=3)).isoformat(), True)
        self.db.add_log_entry(habit_id, (today - timedelta(days=4)).isoformat(), True)
        self.db.add_log_entry(habit_id, (today - timedelta(days=5)).isoformat(), True)
        
        streak = calculate_current_streak(self.db, habit_id)
        self.assertEqual(streak, 2)
    
    def test_calculate_longest_streak(self):
        """Test longest streak."""
        habit_id = self.db.create_habit("Test")
        
        # 3-day streak
        self.db.add_log_entry(habit_id, "2026-05-01", True)
        self.db.add_log_entry(habit_id, "2026-05-02", True)
        self.db.add_log_entry(habit_id, "2026-05-03", True)
        
        # Gap
        
        # 5-day streak
        self.db.add_log_entry(habit_id, "2026-05-09", True)
        self.db.add_log_entry(habit_id, "2026-05-10", True)
        self.db.add_log_entry(habit_id, "2026-05-11", True)
        self.db.add_log_entry(habit_id, "2026-05-12", True)
        self.db.add_log_entry(habit_id, "2026-05-13", True)
        
        streak = calculate_longest_streak(self.db, habit_id)
        self.assertEqual(streak, 5)
    
    def test_get_date_range(self):
        """Test date range generation."""
        dates = get_date_range("2026-05-08", "2026-05-10")
        self.assertEqual(len(dates), 3)
        self.assertEqual(dates[0], "2026-05-08")
        self.assertEqual(dates[2], "2026-05-10")
    
    def test_format_date_string(self):
        """Test format_date with string."""
        result = format_date("2026-05-08")
        self.assertEqual(result, "2026-05-08")
    
    def test_get_today(self):
        """Test get_today function."""
        today = get_today()
        self.assertEqual(len(today), 10)
        self.assertEqual(today[4], "-")
        self.assertEqual(today[7], "-")
    
    def test_get_habit_stats(self):
        """Test stats aggregation."""
        habit_id = self.db.create_habit("Test")
        
        today = datetime.now().date()
        for i in range(3):
            date = (today - timedelta(days=i)).isoformat()
            self.db.add_log_entry(habit_id, date, True)
        
        stats = get_habit_stats(self.db, habit_id)
        
        self.assertEqual(stats['current_streak'], 3)
        self.assertEqual(stats['longest_streak'], 3)
        self.assertEqual(stats['total_completions'], 3)


class TestCommands(unittest.TestCase):
    """Test command handlers."""
    
    def setUp(self):
        """Create a temp database for each test."""
        self.temp_dir = tempfile.TemporaryDirectory()
        self.db_path = os.path.join(self.temp_dir.name, "test.db")
        self.db = Database(self.db_path)
        self.commands = HabitTrackerCommands(self.db)
    
    def tearDown(self):
        """Clean up temp database."""
        self.temp_dir.cleanup()
    
    def test_add_habit(self):
        """Test add_habit command."""
        result = self.commands.add_habit("Morning Jog", "30 min")
        self.assertIn("✓", result)
        self.assertIn("Morning Jog", result)
    
    def test_list_habits_empty(self):
        """Test list_habits with no habits."""
        result = self.commands.list_habits()
        self.assertIn("No habits", result)
    
    def test_list_habits(self):
        """Test list_habits with data."""
        self.commands.add_habit("Morning Jog", "30 min")
        self.commands.add_habit("Meditation")
        result = self.commands.list_habits()
        self.assertIn("Morning Jog", result)
        self.assertIn("Meditation", result)
        self.assertIn("streak:", result)
    
    def test_delete_habit(self):
        """Test delete_habit command."""
        self.commands.add_habit("Test")
        result = self.commands.delete_habit("Test")
        self.assertIn("✓", result)
        self.assertIn("archived", result.lower())
    
    def test_delete_nonexistent(self):
        """Test delete nonexistent habit."""
        result = self.commands.delete_habit("Nonexistent")
        self.assertIn("✗", result)
        self.assertIn("not found", result.lower())
    
    def test_log_completion(self):
        """Test log_completion command."""
        self.commands.add_habit("Test")
        result = self.commands.log_completion("Test", "2026-05-08", True)
        self.assertIn("✓", result)
        self.assertIn("completed", result.lower())
    
    def test_log_not_completed(self):
        """Test logging incomplete."""
        self.commands.add_habit("Test")
        result = self.commands.log_completion("Test", "2026-05-08", False)
        self.assertIn("✓", result)
        self.assertIn("not completed", result.lower())
    
    def test_view_log(self):
        """Test view_log command."""
        self.commands.add_habit("Test")
        self.commands.log_completion("Test", "2026-05-08", True, "Note")
        result = self.commands.view_log("Test", 7)
        self.assertIn("Test", result)
        self.assertIn("2026-05-08", result)
        self.assertIn("✓", result)
    
    def test_view_streak(self):
        """Test view_streak command."""
        self.commands.add_habit("Test")
        self.commands.log_completion("Test", "2026-05-08", True)
        self.commands.log_completion("Test", "2026-05-07", True)
        
        result = self.commands.view_streak("Test")
        self.assertIn("Current Streak", result)
        self.assertIn("Longest Streak", result)
        self.assertIn("Total Completions", result)


class TestExport(unittest.TestCase):
    """Test export functionality."""
    
    def setUp(self):
        """Create a temp database and exporter."""
        self.temp_dir = tempfile.TemporaryDirectory()
        self.db_path = os.path.join(self.temp_dir.name, "test.db")
        self.db = Database(self.db_path)
        self.export_dir = os.path.join(self.temp_dir.name, "exports")
        os.makedirs(self.export_dir, exist_ok=True)
        self.exporter = HabitExporter(self.db, self.export_dir)
    
    def tearDown(self):
        """Clean up."""
        self.temp_dir.cleanup()
    
    def test_export_habits(self):
        """Test exporting habits."""
        self.db.create_habit("Habit 1", "Desc 1")
        self.db.create_habit("Habit 2")
        
        filepath = self.exporter.export_habits()
        
        self.assertTrue(os.path.exists(filepath))
        with open(filepath) as f:
            reader = csv.DictReader(f)
            rows = list(reader)
        
        self.assertEqual(len(rows), 2)
        self.assertIn('name', rows[0])
        self.assertIn('description', rows[0])
    
    def test_export_logs(self):
        """Test exporting logs."""
        habit_id = self.db.create_habit("Test")
        self.db.add_log_entry(habit_id, "2026-05-08", True, "Good")
        self.db.add_log_entry(habit_id, "2026-05-07", False)
        
        filepath = self.exporter.export_logs("2026-05-01", "2026-05-31")
        
        self.assertTrue(os.path.exists(filepath))
        with open(filepath) as f:
            reader = csv.DictReader(f)
            rows = list(reader)
        
        self.assertEqual(len(rows), 2)
        self.assertIn('completed', rows[0])
        self.assertIn('Yes', [r['completed'] for r in rows])
        self.assertIn('No', [r['completed'] for r in rows])
    
    def test_export_streaks(self):
        """Test exporting streaks."""
        habit_id = self.db.create_habit("Test")
        self.db.add_log_entry(habit_id, "2026-05-08", True)
        self.db.add_log_entry(habit_id, "2026-05-07", True)
        
        filepath = self.exporter.export_streaks()
        
        self.assertTrue(os.path.exists(filepath))
        with open(filepath) as f:
            reader = csv.DictReader(f)
            rows = list(reader)
        
        self.assertEqual(len(rows), 1)
        self.assertIn('current_streak', rows[0])
        self.assertIn('longest_streak', rows[0])
        self.assertIn('total_completions', rows[0])


def run_tests():
    """Run all tests."""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add all test classes
    suite.addTests(loader.loadTestsFromTestCase(TestDatabase))
    suite.addTests(loader.loadTestsFromTestCase(TestModels))
    suite.addTests(loader.loadTestsFromTestCase(TestUtils))
    suite.addTests(loader.loadTestsFromTestCase(TestCommands))
    suite.addTests(loader.loadTestsFromTestCase(TestExport))
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.wasSuccessful()


if __name__ == '__main__':
    success = run_tests()
    sys.exit(0 if success else 1)
