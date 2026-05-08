# Commands Module Design

## Overview

The `commands.py` module implements the business logic for all user-facing operations. It bridges the database layer with the CLI layer, providing high-level operations with formatted output suitable for terminal display.

## Architecture

### HabitTrackerCommands Class

Single class that encapsulates all command operations. Initialized with a Database instance:

```python
class HabitTrackerCommands:
    def __init__(self, db: Database):
        self.db = db
```

**Design Rationale:**
- Centralized command logic
- Easy to test with mocked database
- Single responsibility per method
- Consistent error handling

## Commands

### add_habit(name, description="")

**Purpose:** Create a new habit

**Parameters:**
- `name` (str): Unique habit name
- `description` (str): Optional details

**Returns:** Success or error message (user-friendly)

**Process:**
1. Call `db.create_habit()`
2. Catch `sqlite3.IntegrityError` if name already exists
3. Return formatted message

**Output Format:**
```
✓ Habit 'Morning Jog' created successfully (ID: 1)
✗ Error: Habit already exists
```

**Error Cases:**
- Duplicate name: caught and reported
- Database errors: propagated with error message

### list_habits(include_archived=False)

**Purpose:** Display all habits

**Parameters:**
- `include_archived` (bool): Whether to show archived habits

**Returns:** Formatted list with current streaks

**Process:**
1. Query `db.list_habits()`
2. For each habit, calculate current streak
3. Format as table with visual layout

**Output Format:**
```
Active Habits:
--------------------------------------------------
  Morning Jog - 30 min jog [streak: 5] (active)
  Meditation [streak: 0] (active)
```

**Visual Elements:**
- Header indicates archive status
- Separator line for clarity
- Habit name and optional description
- Current streak in brackets
- Status (active/archived)

**Edge Case:** Empty list returns "No habits found."

### delete_habit(name)

**Purpose:** Archive/delete a habit

**Parameters:**
- `name` (str): Name of habit to delete

**Returns:** Success or error message

**Process:**
1. Look up habit by name
2. Call `db.delete_habit()` (soft delete)
3. Return confirmation

**Output Format:**
```
✓ Habit 'Morning Jog' archived
✗ Habit 'Unknown' not found
```

**Design Notes:**
- Uses soft delete to preserve history
- Lookup by name (user-friendly)
- Confirms successful operation

### log_completion(name, date=None, completed=True, notes="")

**Purpose:** Record habit completion/non-completion

**Parameters:**
- `name` (str): Habit name
- `date` (str): Optional date YYYY-MM-DD (default: today)
- `completed` (bool): Completion status (default: True)
- `notes` (str): Optional notes

**Returns:** Success or error message

**Process:**
1. Get today's date if not provided
2. Look up habit by name
3. Call `db.add_log_entry()`
4. Return confirmation with date and status

**Output Format:**
```
✓ Logged 'Morning Jog' as completed on 2026-05-08
✓ Logged 'Reading' as not completed on 2026-05-07
```

**Design Notes:**
- Defaults to today (common case)
- Supports past date entry (catch-up logging)
- Clear status message
- Can log non-completion with notes

### view_log(name=None, days=7)

**Purpose:** View log entries

**Parameters:**
- `name` (str): Optional habit name (None = today's logs)
- `days` (int): Number of recent days to show

**Returns:** Formatted log entries

**Process - Habit-Specific:**
1. Look up habit by name
2. Get log entries (most recent N days)
3. Format as list with dates and status

**Output Format:**
```
Log entries for 'Morning Jog' (last 7 days):
--------------------------------------------------
  2026-05-08: ✓ (Felt great!)
  2026-05-07: ✓
  2026-05-06: ✗ (Sick today)
```

**Process - Today's Logs:**
1. Get all logs for today
2. Join with habit names
3. Format as completion summary

**Output Format:**
```
Today's log entries (2026-05-08):
--------------------------------------------------
  Meditation: ✓
  Morning Jog: ✓
  Reading: ✗
```

**Design Notes:**
- Default 7 days shows recent week
- Shows completion status as ✓/✗
- Includes notes if present
- Different output for aggregate vs. habit-specific

### view_streak(name)

**Purpose:** Display streak statistics

**Parameters:**
- `name` (str): Habit name

**Returns:** Formatted streak information

**Process:**
1. Look up habit
2. Call `utils.get_habit_stats()`
3. Format statistics

**Output Format:**
```
Streak for 'Morning Jog':
--------------------------------------------------
  Current Streak: 5 days
  Longest Streak: 12 days
  Total Completions: 47
```

**Metrics:**
- **Current Streak**: Consecutive days ending today
- **Longest Streak**: Best achievement ever
- **Total Completions**: All-time count

**Design Notes:**
- Single call to stats function
- Clear labels for each metric
- Consistent formatting

## Output Formatting

### Success/Error Indicators
```
✓ Success message
✗ Error message
```

### Tables and Lists
```
Header Text:
--------------------------------------------------
  Item 1
  Item 2
  Item 3
```

**Design Pattern:**
- Consistent 50-character separator
- 2-space indentation for items
- Header with colon
- Clear visual hierarchy

### Return Type Consistency

All commands return **strings** for easy CLI output:
```python
print(commands.add_habit("Jog"))  # Just print the result
```

**Benefit:** Decouples commands from output mechanism

## Error Handling Strategy

### Input Validation
- Habit not found: "✗ Habit 'X' not found"
- Empty lists: Specific message per command
- Invalid dates: Caught by database layer

### Database Errors
- Caught and wrapped in user-friendly messages
- Stack trace not shown to user
- Clear explanation of what went wrong

### Design Principle
- Fail gracefully with informative messages
- Never let exceptions bubble up to CLI
- Return error messages as strings (same as success)

## Testing Approach

### Unit Test Scenarios
1. **Happy Path**: All operations with valid input
2. **Not Found**: Habit doesn't exist
3. **Duplicates**: Adding same habit twice
4. **Edge Cases**:
   - Empty habit list
   - Empty logs
   - Single-day streaks
   - Historical dates

### Integration Tests
- Add habit → log → view → streak
- Multiple habits with different patterns
- Date range queries

## Performance Characteristics

### Database Efficiency
- `add_habit`: Single INSERT
- `list_habits`: Single SELECT with JOIN (for streak)
- `log_completion`: INSERT OR REPLACE (single operation)
- `view_log`: SELECT range with optional date filter
- `view_streak`: All completed dates lookup

### Calculation Overhead
- Streak calculations done in memory (Python)
- Database returns only necessary data
- No unnecessary queries

## Design Decisions

### 1. String Return Values
- **Why**: Consistent with CLI output
- **Alternative**: Return tuples/dicts (less convenient for CLI)
- **Trade-off**: Not ideal for API usage (but that's OK for CLI-focused)

### 2. Optional Parameters with Defaults
- **Why**: Common cases have sensible defaults
- **Benefits**: Simpler CLI commands
- **Examples**: date=today, days=7, description=""

### 3. Lookup by Name (Not ID)
- **Why**: User-friendly CLI interface
- **Trade-off**: One extra query (database handles efficiently)
- **Benefit**: Users don't need to remember IDs

### 4. Soft Delete Pattern
- **Why**: Preserves historical data
- **Why**: User can recover habits
- **Benefit**: Analytics remain accurate

### 5. Unified Error Handling
- **Why**: Consistent user experience
- **Why**: All errors are strings (easy to test)
- **Benefit**: No exceptions leak to CLI

## Future Enhancements

1. **Batch Operations**: Log multiple habits at once
2. **Filters**: List habits by category, streak range
3. **Statistics**: Weekly reports, trends
4. **Habits View**: Show completions in calendar format
5. **Undo**: Support undoing recent logs
6. **Recurring**: Add daily/weekly habit patterns
