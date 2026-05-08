# Database Module Design

## Overview

The `database.py` module provides a complete SQLite abstraction layer for the habit tracker, implementing a simple but robust interface for all persistence operations.

## Schema Design

### Habits Table
```sql
CREATE TABLE habits (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE NOT NULL,
    description TEXT,
    created_at TIMESTAMP NOT NULL,
    archived INTEGER DEFAULT 0
)
```

**Design Decisions:**
- **id**: Auto-incrementing primary key for efficient references
- **name**: Unique constraint ensures one habit per name (user-friendly references)
- **description**: Optional field for additional context
- **created_at**: ISO format timestamp for ordering and statistics
- **archived**: Boolean (stored as INTEGER) for soft delete - preserves historical data while hiding from normal listings

### Logs Table
```sql
CREATE TABLE logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    habit_id INTEGER NOT NULL,
    date DATE NOT NULL,
    completed INTEGER NOT NULL,
    notes TEXT,
    FOREIGN KEY (habit_id) REFERENCES habits (id),
    UNIQUE (habit_id, date)
)
```

**Design Decisions:**
- **id**: Primary key for individual log records
- **habit_id**: Foreign key references habits (enables cascading lookups)
- **date**: Stored as DATE (YYYY-MM-DD format) for easy range queries
- **completed**: Boolean (0 or 1) for simple completion flag
- **notes**: Optional user-provided context
- **UNIQUE (habit_id, date)**: Ensures one entry per habit per day; INSERT OR REPLACE allows updates

## Class Structure

### Database Class

#### Initialization
```python
def __init__(self, db_path: str = "habit_tracker.db"):
```
- Creates database file if needed
- Automatically initializes schema on first run
- Uses sqlite3.Row factory for dict-like row access

#### Connection Management
```python
@contextmanager
def connection(self):
```
- Implements context manager pattern for safe resource management
- Automatically closes connections in all cases (success or exception)
- Enables: `with db.connection() as conn:`

#### Core Operations

**Habit Operations:**
- `create_habit(name, description)` - INSERT with auto-increment
- `get_habit(habit_id)` - Single habit lookup by ID
- `get_habit_by_name(name)` - User-friendly lookup by name
- `list_habits(include_archived)` - All habits, filtered by archive status
- `delete_habit(habit_id)` - Soft delete via archive flag

**Log Operations:**
- `add_log_entry(habit_id, date, completed, notes)` - INSERT OR REPLACE
- `get_log_entries(habit_id, start_date, end_date)` - Range queries
- `get_logs_by_date(date)` - All completions for a specific date
- `get_completion_streak(habit_id)` - All completed dates (ordered newest first)

## Design Patterns

### 1. Context Manager Pattern
All database operations use context managers:
```python
with db.connection() as conn:
    cursor = conn.cursor()
    # operations
    conn.commit()
```

**Benefits:**
- Automatic connection closure on success or exception
- Clear resource lifecycle
- Prevents connection leaks

### 2. Soft Delete Pattern
Habits use `archived` flag instead of hard delete:
```sql
WHERE archived = 0
```

**Benefits:**
- Preserves historical data and logs
- Users can recover deleted habits
- Analytics on deleted habits remain valid
- Audit trail maintained

### 3. INSERT OR REPLACE for Idempotent Updates
Log entries use unique constraint with INSERT OR REPLACE:
```sql
UNIQUE (habit_id, date)
INSERT OR REPLACE INTO logs (habit_id, date, completed, notes) VALUES (...)
```

**Benefits:**
- Users can update logs without knowing if entry exists
- No error on duplicate date
- Simple API: always use add_log_entry

### 4. SQLite Row Factory
```python
conn.row_factory = sqlite3.Row
```

**Benefits:**
- Rows can be accessed as dictionaries: `row['name']`
- Can be converted to dict: `dict(row)`
- More Pythonic than tuple indexing

## Edge Cases Handled

1. **Duplicate Habit Names**: Raises `sqlite3.IntegrityError` (caught by commands layer)
2. **Updating Same Date**: INSERT OR REPLACE automatically overwrites
3. **Querying Empty Results**: Returns empty list (no exceptions)
4. **Archived Habits**: Hidden from normal operations via `archived = 0` filter
5. **Missing Habit**: Returns None from get methods

## Type Handling

- **Dates**: Stored as TEXT in YYYY-MM-DD format (easy querying, ISO standard)
- **Timestamps**: ISO format for created_at (timezone-aware operations possible)
- **Booleans**: Stored as INTEGER (0/1) - SQLite has no native boolean
- **Foreign Keys**: Enforced by schema, cascading deletes via UNIQUE constraint

## Performance Considerations

- **Indexing**: Primary keys auto-indexed, foreign keys enabled by default
- **Querying by Name**: O(1) due to unique constraint
- **Streak Calculations**: Returns all completion dates (memory trade-off for simplicity)
- **Large Datasets**: LIMIT or date range queries recommended for historical data

## Future Extensions

1. **Migrations**: Could add schema version tracking
2. **Backup/Restore**: CSV import/export already implemented in export module
3. **Indexes**: Could add explicit indexes on (habit_id, date) for large datasets
4. **Transactions**: Could implement transaction boundaries for multi-operation consistency
5. **Timestamps**: Could add last_updated field for audit trails

## Testing Strategy

All operations tested with:
- Happy path (normal usage)
- Edge cases (empty data, duplicates)
- Error conditions (invalid IDs, constraint violations)
- Data integrity (UNIQUE constraints working)
- Soft deletes (archived flag respected)
