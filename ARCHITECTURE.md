# Habit Tracker Architecture

## Overview

The Habit Tracker is a Python CLI application designed to help users track daily habits, maintain streaks, and analyze their completion patterns. The architecture follows a modular design with clear separation of concerns.

## Module Structure

### 1. `habit_tracker/__init__.py`
Package initialization file that defines the version and basic metadata.

### 2. `habit_tracker/database.py`
**Database Layer**

Handles all SQLite database operations with a context manager pattern for safe connection handling.

**Key Classes:**
- `Database`: Main database handler

**Key Responsibilities:**
- Schema initialization (habits and logs tables)
- CRUD operations for habits and log entries
- Safe connection management using context managers
- Query operations for logs, streaks, and historical data

**Database Schema:**
- `habits`: id, name (unique), description, created_at, archived
- `logs`: id, habit_id (FK), date, completed, notes; unique constraint on (habit_id, date)

### 3. `habit_tracker/models.py`
**Data Models Layer**

Defines data structures using Python dataclasses for type safety and clarity.

**Key Classes:**
- `Habit`: Represents a single habit with metadata
- `LogEntry`: Represents a completion log for a specific date

**Responsibilities:**
- Type-safe data representation
- Serialization/deserialization (to_dict, from_dict methods)
- Default value handling

### 4. `habit_tracker/utils.py`
**Utilities Layer**

Contains helper functions for common operations across the application.

**Key Functions:**
- `calculate_current_streak()`: Calculates current consecutive completion streak
- `calculate_longest_streak()`: Finds the longest streak in history
- `get_date_range()`: Generates date sequences for queries
- `get_habit_stats()`: Aggregates statistics for a habit
- Date formatting and manipulation helpers

**Design Notes:**
- Streak calculation handles edge cases (missing days, gaps)
- All calculations are based on actual database records
- Stat functions provide unified interface for metrics

### 5. `habit_tracker/commands.py`
**Command Handler Layer**

Implements user-facing operations with formatted output for CLI display.

**Key Classes:**
- `HabitTrackerCommands`: Orchestrates all user operations

**Available Commands:**
- `add_habit()`: Create new habit
- `list_habits()`: Display all active habits with current streaks
- `delete_habit()`: Archive a habit (soft delete)
- `log_completion()`: Record habit completion for a date
- `view_log()`: Display recent logs for a habit or all habits
- `view_streak()`: Show streak statistics for a habit

**Design Notes:**
- Returns formatted strings for CLI output
- Input validation and error handling
- Integrates database, models, and utility functions
- User-friendly messages with visual indicators (✓, ✗)

### 6. `habit_tracker/export.py`
**Export Layer**

Handles CSV export functionality for data analysis and backup.

**Key Classes:**
- `HabitExporter`: CSV export operations

**Export Types:**
- `export_habits()`: All habit definitions
- `export_logs()`: Log entries for date range
- `export_streaks()`: Streak summary statistics

**Design Notes:**
- Automatic filename generation with timestamps
- Customizable output directory
- Validation for empty data
- Column headers for clarity

### 7. `habit_tracker/main.py`
**CLI Entry Point**

Command-line interface using argparse for argument parsing and command routing.

**Responsibilities:**
- Argument parsing for all commands and options
- Command routing and execution
- Error handling and user feedback
- Database initialization
- Help documentation

**Command Structure:**
```
habit-tracker [--db PATH] COMMAND [OPTIONS]

Commands:
  add NAME [--description TEXT]
  list
  delete NAME
  log NAME [--date YYYY-MM-DD] [--notes TEXT] [--skip]
  view [NAME] [--days N]
  streak NAME
  export [--type {habits|logs|streaks}] [--start DATE] [--end DATE] [--output DIR]
```

## Data Flow

1. **User Input** → argparse in main.py
2. **Parsing** → Command dispatcher
3. **Execution** → HabitTrackerCommands methods
4. **Database Operations** → Database class
5. **Calculations** → Utils functions
6. **Formatting** → Output strings to CLI

## Design Principles

### Separation of Concerns
- Database layer handles persistence
- Commands layer handles business logic
- Utils layer handles calculations
- Main module handles CLI interface

### Error Handling
- Database errors are caught and reported to user
- Habit not found cases return user-friendly messages
- Export functions validate data before processing

### Extensibility
- New commands can be added to HabitTrackerCommands
- Export types can be extended in HabitExporter
- Database operations can be extended in Database class

### Code Quality
- Type hints throughout
- Docstrings for all classes and functions
- Context managers for resource management
- Dataclasses for type-safe models

## Dependencies

**Standard Library Only:**
- sqlite3: Database operations
- csv: CSV export
- datetime: Date handling
- argparse: CLI parsing
- pathlib: File path handling
- dataclasses: Data models

No external dependencies required - fully self-contained with Python standard library.

## Future Enhancements

1. Database migration system
2. Data backup/restore functionality
3. Statistics visualizations
4. Habit categories/tags
5. Reminders/notifications
6. Web UI alternative
7. Cloud sync capability
