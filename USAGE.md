# Habit Tracker - Usage Guide

A simple CLI application for tracking daily habits, maintaining streaks, and analyzing completion patterns.

## Installation

### From Source

```bash
# Clone or download the repository
cd habit-tracker

# Install in development mode
pip install -e .
```

Or run directly:

```bash
python3 -m habit_tracker.main [COMMAND] [OPTIONS]
```

## Quick Start

### Add a Habit

```bash
habit-tracker add "Morning Jog" --description "30 min jog"
habit-tracker add "Meditation"
habit-tracker add "Reading" -d "Read 20 pages"
```

### Log Completion

```bash
# Log today's completion
habit-tracker log "Morning Jog"

# Log with notes
habit-tracker log "Morning Jog" --notes "Felt energetic"

# Log past date
habit-tracker log "Morning Jog" --date 2026-05-07

# Mark as not completed
habit-tracker log "Reading" --skip
habit-tracker log "Reading" --skip --notes "Too tired"
```

### View Habits

```bash
# List all active habits with current streaks
habit-tracker list
```

Output:
```
Active Habits:
--------------------------------------------------
  Morning Jog - 30 min jog [streak: 5] (active)
  Meditation [streak: 2] (active)
  Reading - Read 20 pages [streak: 0] (active)
```

### View Logs

```bash
# View recent logs for a specific habit (last 7 days)
habit-tracker view "Morning Jog"

# View extended history
habit-tracker view "Morning Jog" --days 30

# View today's summary (all habits)
habit-tracker view
```

Output for specific habit:
```
Log entries for 'Morning Jog' (last 7 days):
--------------------------------------------------
  2026-05-08: ✓ (Felt energetic)
  2026-05-07: ✓
  2026-05-06: ✓
  2026-05-05: ✗ (Sick)
```

Output for today's summary:
```
Today's log entries (2026-05-08):
--------------------------------------------------
  Meditation: ✓
  Morning Jog: ✓
  Reading: ✗
```

### View Streaks

```bash
# Show streak statistics for a habit
habit-tracker streak "Morning Jog"
```

Output:
```
Streak for 'Morning Jog':
--------------------------------------------------
  Current Streak: 5 days
  Longest Streak: 12 days
  Total Completions: 47
```

### Delete/Archive Habits

```bash
# Archive a habit (soft delete, preserves history)
habit-tracker delete "Reading"
```

### Export Data

```bash
# Export streak summary (default)
habit-tracker export

# Export to specific directory
habit-tracker export --output ~/backups/habits

# Export all habit definitions
habit-tracker export --type habits

# Export log entries for date range
habit-tracker export --type logs --start 2026-01-01 --end 2026-12-31

# Export logs to specific location
habit-tracker export --type logs --start 2026-05-01 --end 2026-05-31 --output ./reports
```

Generates CSV files:
- `streaks_20260508_041822.csv` - Streak statistics
- `habits_20260508_041822.csv` - Habit definitions
- `logs_2026-05-01_to_2026-05-31_20260508_041822.csv` - Log entries

## Common Workflows

### Morning Routine - Log Multiple Habits

```bash
# Log that you completed your morning routine
habit-tracker log "Morning Jog"
habit-tracker log "Meditation"
habit-tracker log "Breakfast"

# Or check your status
habit-tracker view
```

### Weekly Review

```bash
# Export streaks to see your progress
habit-tracker export --type streaks --output ./weekly_reports

# View last week's activity
habit-tracker view "Morning Jog" --days 7

# Check all habits
habit-tracker list
```

### Monthly Analysis

```bash
# Export entire month's logs
habit-tracker export --type logs \
  --start 2026-05-01 \
  --end 2026-05-31 \
  --output ./analysis

# Check longest streaks for the month
habit-tracker list
```

### Catch-up Logging

```bash
# Log past days (e.g., recovering from travel)
habit-tracker log "Morning Jog" --date 2026-05-06 --notes "Made up from travel day"
habit-tracker log "Morning Jog" --date 2026-05-05 --notes "Made up from travel day"

# Verify the logs
habit-tracker view "Morning Jog"
```

## Database Management

### Custom Database Location

By default, the database is created in the current directory as `habit_tracker.db`. You can use a different location:

```bash
# Use custom database
habit-tracker --db ~/my_habits/tracker.db add "Habit"

# Use database in home directory
habit-tracker --db ~/.habit_tracker.db list

# Use temporary database for testing
habit-tracker --db /tmp/test.db log "Test Habit"
```

### Data Persistence

All data is automatically saved in the SQLite database:
- Habit definitions (name, description, creation date)
- Log entries (date, completion status, notes)
- Archive status (for soft-deleted habits)

Delete habits are NOT permanently removed - they're archived so historical data is preserved.

## Troubleshooting

### Habit not found error

```
✗ Habit 'Morning Jo' not found
```

**Solution:** Check the exact habit name. Names are case-sensitive.
```bash
habit-tracker list  # See correct names
```

### Missing required dates for logs export

```
✗ Error: --start and --end dates required for logs export
```

**Solution:** Provide both start and end dates:
```bash
habit-tracker export --type logs --start 2026-05-01 --end 2026-05-31
```

### Database locked error

This might occur if multiple instances are running. Wait a moment and try again. The application uses SQLite which handles most concurrent access gracefully.

## Advanced Usage

### Backup Your Data

```bash
# Export all habits
habit-tracker export --type habits --output ./backup

# Export all logs for a year
habit-tracker export --type logs \
  --start 2026-01-01 \
  --end 2026-12-31 \
  --output ./backup

# Or simply copy the database file
cp habit_tracker.db habit_tracker.backup.db
```

### Restore from Backup

Simply use the backup database file:

```bash
habit-tracker --db habit_tracker.backup.db list
```

### Analyze with Spreadsheets

Export logs to CSV and open in Excel, Google Sheets, or other tools:

```bash
# Export logs
habit-tracker export --type logs --start 2026-01-01 --end 2026-12-31

# Open the CSV file
open logs_2026-01-01_to_2026-12-31_*.csv
```

### Integration with Other Tools

The CSV exports are fully compatible with:
- Excel / Google Sheets
- Python pandas: `df = pd.read_csv('logs_*.csv')`
- R: `logs <- read.csv('logs_*.csv')`
- Data visualization tools
- Statistical analysis tools

## Tips for Success

1. **Daily Logging**: Log completions every day, ideally at the same time
2. **Use Notes**: Add notes for context - it helps when reviewing patterns
3. **Regular Reviews**: Check your streaks weekly to stay motivated
4. **Realistic Goals**: Start with habits you can realistically maintain
5. **Build Momentum**: Focus on building current streaks before adding new habits
6. **Track What Matters**: Only track habits that are important to you

## Command Reference

```
Global Options:
  --db PATH              Database file path (default: habit_tracker.db)
  -h, --help            Show help message

Commands:
  add NAME [--description TEXT]
                        Add a new habit
  
  list                  List all active habits
  
  delete NAME           Archive/delete a habit
  
  log NAME [--date DATE] [--notes TEXT] [--skip]
                        Log a completion
  
  view [NAME] [--days N]
                        View logs
  
  streak NAME           View streak statistics
  
  export [--type TYPE] [--start DATE] [--end DATE] [--output DIR]
                        Export to CSV

Date Format:
  YYYY-MM-DD (e.g., 2026-05-08)

Notes:
  - All commands are case-sensitive for habit names
  - Deleted habits are archived, not permanently removed
  - Logs include timestamps in ISO format
  - CSV exports use UTF-8 encoding
```

## Getting Help

```bash
# Show general help
habit-tracker --help

# Show command-specific help
habit-tracker add --help
habit-tracker log --help
habit-tracker export --help
```

## Testing

Run the test suite to verify the application works correctly:

```bash
python3 tests/test_suite.py
```

Expected output: All 40 tests should pass.

---

For more information, see:
- `ARCHITECTURE.md` - Technical architecture
- `docs/design-docs/` - Detailed module documentation
