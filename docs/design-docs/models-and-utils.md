# Models and Utilities Design

## Overview

The `models.py` module provides type-safe data structures using Python dataclasses, and `utils.py` contains helper functions for calculations and formatting that are used across the application.

## Models Module (models.py)

### Design Pattern: Dataclasses

Uses Python's `dataclasses` for concise, type-safe data representation:

```python
@dataclass
class Habit:
    id: int
    name: str
    description: str = ""
    created_at: str = None
    archived: int = 0
```

**Benefits:**
- Type hints for IDE support and type checking
- Automatic `__init__`, `__repr__`, `__eq__`
- Default values built-in
- Memory efficient
- Familiar to Python developers

### Habit Class

Represents a single habit with metadata.

**Fields:**
- `id`: Unique identifier (from database)
- `name`: Human-readable habit name
- `description`: Optional details about the habit
- `created_at`: ISO format timestamp (auto-set if None)
- `archived`: Flag for soft-delete (0 = active, 1 = archived)

**Methods:**
- `to_dict()`: Converts to dictionary for serialization (uses `asdict()`)
- `from_dict(data)`: Class method to create Habit from dictionary

**Design Notes:**
- `created_at` defaults to current time if not provided in `__post_init__`
- Allows seamless conversion to/from database records and JSON
- Simple, focused responsibility

### LogEntry Class

Represents a single completion log for a habit on a specific date.

**Fields:**
- `id`: Unique log entry identifier
- `habit_id`: Reference to the habit (foreign key)
- `date`: Date of completion (YYYY-MM-DD format)
- `completed`: Boolean flag (stored as 0/1 in database)
- `notes`: Optional user-provided context/notes

**Methods:**
- `to_dict()`: Dictionary conversion for serialization
- `from_dict(data)`: Create LogEntry from dictionary

**Design Notes:**
- Separates habit metadata from completion records
- Supports both completion and non-completion logs (notes can explain why)
- Date format consistent with database storage

## Utilities Module (utils.py)

Contains helper functions for common operations across the application.

### Streak Calculation Functions

#### calculate_current_streak(db, habit_id)

Calculates the current consecutive completion streak.

**Algorithm:**
1. Fetch all completed dates (ordered newest first from database)
2. Start from today's date
3. Walk backwards through dates, checking if each is consecutive
4. Stop at first gap
5. Return count

**Edge Cases:**
- Empty completion history: returns 0
- Today not completed: streak is from yesterday backwards
- Non-consecutive days: breaks at first gap (returns partial streak)

**Time Complexity:** O(n) where n = number of completions
**Space Complexity:** O(n) for date list

**Example:**
```
Completions: [May 8, May 7, May 6]
Today: May 8
Result: 3 days (May 8 → 7 → 6 consecutive)

Completions: [May 8, May 6, May 5]  # Gap on May 7
Today: May 8
Result: 1 day (only May 8 is current streak)
```

#### calculate_longest_streak(db, habit_id)

Finds the longest consecutive streak ever achieved.

**Algorithm:**
1. Fetch all completed dates and reverse (oldest first)
2. Iterate forward through time
3. Track current streak length and longest streak
4. Reset streak counter at gaps
5. Return longest

**Edge Cases:**
- Empty history: returns 0
- Single completion: returns 1
- All non-consecutive: returns 1

**Time Complexity:** O(n)
**Space Complexity:** O(n)

**Example:**
```
Completions (chronological): [May 1-5, gap, May 10-15]
Streaks: 5 days, then 6 days
Result: 6 days
```

### Date Range Functions

#### get_date_range(start_date, end_date)

Generates a list of all dates in a range (inclusive).

**Parameters:**
- `start_date`: YYYY-MM-DD format
- `end_date`: YYYY-MM-DD format

**Returns:** List of ISO format date strings

**Implementation:** Iterative day-by-day increment with `timedelta`

**Use Cases:**
- Exporting date ranges
- Generating statistics for periods
- Filling gaps in data for analysis

### Formatting Functions

#### format_date(date_obj)

Converts date objects to YYYY-MM-DD string format.

**Flexibility:**
- Accepts both datetime.date and string inputs
- Returns input if already string
- Returns ISO format otherwise

#### get_today()

Returns today's date as YYYY-MM-DD string.

**Simplifies:** Common pattern of getting today without datetime import

### Statistics Functions

#### get_habit_stats(db, habit_id)

Aggregates all statistics for a habit in one call.

**Returns Dictionary:**
```python
{
    "current_streak": int,      # Days in current streak
    "longest_streak": int,       # Best streak ever
    "total_completions": int    # Total completed days
}
```

**Efficiency:**
- Single database query for completion count
- Reuses calculation functions
- One-stop stat lookup for CLI display

**Use Cases:**
- Quick stats display
- Summary exports
- Dashboard views

## Design Decisions

### 1. Dataclass Usage
- **Why**: Type-safe, concise, built-in serialization support
- **Alternative**: Named tuples (less serialization flexibility)
- **Alternative**: Regular classes (more boilerplate)

### 2. Calculation Functions Over Methods
- **Why**: Keeps domain logic in utils, models stay simple
- **Benefit**: Easy to test independently
- **Benefit**: Can be reused in different contexts

### 3. Database Dependency in Utils
- **Why**: Functions need data from database
- **Trade-off**: Utils depends on database module
- **Isolation**: Functions still testable with test database

### 4. String Dates Over DateTime Objects
- **Why**: Matches database storage format
- **Why**: Simple for range queries
- **Simplification**: Reduces datetime complexity
- **Trade-off**: No timezone information

### 5. Dict Conversion Methods
- **Why**: Easy JSON serialization for APIs or exports
- **Why**: Compatible with database Row objects
- **Flexibility**: Different from initialization

## Testing Considerations

### Models Testing
- Dataclass creation and initialization
- Default value handling
- `to_dict()` and `from_dict()` round-trip
- Field types and constraints

### Utils Testing
- Streak calculations with various patterns
- Empty data handling
- Date range edge cases (single day, long ranges)
- Statistics aggregation

### Test Scenarios for Streaks
```
Scenario 1: Today completed
Completions: [Today, Today-1, Today-2]
Current: 3, Longest: 3

Scenario 2: Gap before today
Completions: [Today-1, Today-2, Today-3, gap, Today-10]
Current: 0, Longest: 3

Scenario 3: Empty
Completions: []
Current: 0, Longest: 0

Scenario 4: Historical streak longer than current
Completions: [Today, ..., long gap, historical 20-day streak]
Current: 1, Longest: 20
```

## Future Extensions

1. **Statistics**: Add average completion rate, best day of week
2. **Projections**: Estimate when user might reach next milestone
3. **Models**: Add Habit categories, habit dependencies
4. **Validation**: Add model validation methods (min/max streak validations)
5. **Serialization**: Add JSON encoder/decoder for full object persistence
