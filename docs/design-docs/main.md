# Main CLI Interface Design

## Overview

The `main.py` module implements the command-line interface (CLI) using Python's `argparse`. It serves as the entry point for all user interactions, parsing arguments and routing to appropriate command handlers.

## Architecture

### Entry Point

```python
def main():
    parser = ArgumentParser(...)
    ...
    return 0 or 1  # Exit code
```

**Design Pattern:**
- Single `main()` function returns exit code
- Can be called programmatically or via `python -m`
- Handles all error cases gracefully

### Argument Parsing Strategy

Uses nested subparsers for command-based CLI:

```
habit-tracker [global-options] COMMAND [command-options]
```

**Components:**
1. **Global Options**: `--db` (database file path)
2. **Subcommands**: add, list, delete, log, view, streak, export
3. **Command Options**: Specific to each command

**Benefits:**
- Clear command structure
- Command-specific help messages
- Standard argparse behavior

## Commands

### add - Create New Habit

```
habit-tracker add NAME [--description TEXT]
```

**Arguments:**
- `name` (positional): Habit name
- `--description` / `-d` (optional): Description text

**Example:**
```bash
habit-tracker add "Morning Jog" --description "30 min morning run"
```

**Routing:**
```python
if args.command == "add":
    print(commands.add_habit(args.name, args.description))
```

### list - Display Habits

```
habit-tracker list
```

**No arguments** - Lists all active habits with current streaks

**Example:**
```bash
habit-tracker list
```

### delete - Archive Habit

```
habit-tracker delete NAME
```

**Arguments:**
- `name` (positional): Habit name to delete

**Example:**
```bash
habit-tracker delete "Morning Jog"
```

### log - Record Completion

```
habit-tracker log NAME [--date YYYY-MM-DD] [--notes TEXT] [--skip]
```

**Arguments:**
- `name` (positional): Habit name
- `--date` (optional): Date in YYYY-MM-DD (default: today)
- `--notes` / `-n` (optional): Notes about completion
- `--skip` (flag): Mark as not completed instead

**Examples:**
```bash
# Log today's completion
habit-tracker log "Morning Jog"

# Log past date with notes
habit-tracker log "Morning Jog" --date 2026-05-05 --notes "Felt great!"

# Mark as not completed
habit-tracker log "Morning Jog" --skip
```

**Design Note:**
- Default `completed=True`, use `--skip` to invert
- Default date is today (common case)

### view - Display Logs

```
habit-tracker view [NAME] [--days N]
```

**Arguments:**
- `name` (optional): Habit name (None = today's summary)
- `--days` (optional): Number of days to show (default: 7)

**Examples:**
```bash
# View specific habit logs (last 7 days)
habit-tracker view "Morning Jog"

# View extended history
habit-tracker view "Morning Jog" --days 30

# View today's summary for all habits
habit-tracker view
```

**Behavior:**
- With name: Show that habit's logs
- Without name: Show today's completions for all habits

### streak - Display Statistics

```
habit-tracker streak NAME
```

**Arguments:**
- `name` (positional): Habit name

**Example:**
```bash
habit-tracker streak "Morning Jog"
```

**Output:**
- Current streak (consecutive days)
- Longest streak (best achievement)
- Total completions

### export - Export Data to CSV

```
habit-tracker export [--type TYPE] [--start DATE] [--end DATE] [--output DIR]
```

**Arguments:**
- `--type` (optional): Export type - habits, logs, streaks (default: streaks)
- `--start` (optional): Start date for logs export (YYYY-MM-DD)
- `--end` (optional): End date for logs export (YYYY-MM-DD)
- `--output` (optional): Output directory (default: current directory)

**Examples:**
```bash
# Export streak summary
habit-tracker export

# Export habits
habit-tracker export --type habits

# Export logs for date range
habit-tracker export --type logs --start 2026-05-01 --end 2026-05-31 --output ./exports

# Export to custom location
habit-tracker export --type streaks --output /backup/habits
```

**Validation:**
- Logs export requires both `--start` and `--end`
- Returns error if missing dates for logs export

## Implementation Details

### Subparser Configuration

Each command gets a subparser:

```python
add_parser = subparsers.add_parser("add", help="Add a new habit")
add_parser.add_argument("name", help="Name of the habit")
add_parser.add_argument("--description", "-d", default="", help="...")
```

**Pattern:**
1. Create subparser with name and help
2. Add arguments (positional and optional)
3. Set defaults for optional arguments

### Command Routing

```python
if args.command == "add":
    print(commands.add_habit(...))
elif args.command == "list":
    print(commands.list_habits())
...
```

**Design:**
- Sequential if-elif chain (clear, maintainable)
- All commands print results (consistent behavior)
- Exception handling wraps entire block

### Error Handling

```python
try:
    db = Database(args.db)
    commands = HabitTrackerCommands(db)
    ...
except Exception as e:
    print(f"✗ Error: {str(e)}", file=sys.stderr)
    return 1
```

**Pattern:**
- Catch all exceptions
- Print to stderr (error channel)
- Return exit code 1 (indicates failure)
- No stack traces shown to user

### Exit Codes

- **0**: Success
- **1**: Error (any exception or validation failure)

**Design:** Simple binary success/failure

## Help Messages

### Global Help

```bash
habit-tracker --help
```

Shows:
- Description of application
- List of available commands
- Global options
- Example usage (from epilog)

### Command Help

```bash
habit-tracker add --help
```

Shows:
- Command description
- Available arguments and options
- Default values
- Argument help text

### Example Usage

Included in main help epilog:

```
Examples:
  habit-tracker add "Morning Jog" --description "30 min jog"
  habit-tracker log "Morning Jog"
  ...
```

**Benefit:** Users see practical examples immediately

## Database Path Management

### Default
```
habit_tracker.db  # In current working directory
```

### Custom Path
```bash
habit-tracker --db ~/habits/my_tracker.db add "Habit"
```

**Design:**
- Global `--db` option applies to all commands
- Each invocation can use different database
- Enables multiple tracking contexts
- Default is current directory (simple, no permission issues)

## Design Decisions

### 1. Subparser Structure Over Positional Arguments
- **Why**: Clear command semantics
- **Why**: Easy to add new commands
- **Alternative**: Single parser with complex logic (less scalable)

### 2. Sequential If-Elif Routing
- **Why**: Simple, maintainable
- **Alternative**: Command dispatch dictionary (more elegant but less readable)
- **Trade-off**: Slightly repetitive code

### 3. String Return Values from Commands
- **Why**: Decouples commands from output format
- **Why**: Easy to test (compare strings)
- **Benefit**: Can redirect output easily

### 4. Required Dates for Logs Export
- **Why**: Prevents accidental full exports
- **Why**: Clear validation feedback
- **Alternative**: Optional with sensible defaults (less explicit)

### 5. Exit Code 0/1 Pattern
- **Why**: Standard Unix convention
- **Why**: Works with shell scripts and CI/CD
- **Alternative**: Detailed exit codes (less compatible)

### 6. Default Database in Current Directory
- **Why**: No permission issues
- **Why**: Simple for initial use
- **Why**: Can be overridden per invocation
- **Trade-off**: Database not centralized

## Future Enhancements

1. **Interactive Mode**: `habit-tracker interactive` for menu-driven interface
2. **Config File**: Support `~/.habit-tracker/config` for defaults
3. **Shell Completion**: `_habit-tracker` bash/zsh completion script
4. **Aliases**: Short command versions (e.g., `ht l` for list)
5. **Batch Operations**: `--batch FILE` to read commands from file
6. **Output Formats**: `--format json` for machine-readable output
7. **Piping**: Support piping to other commands (`| grep`, `| jq`)
8. **Quiet Mode**: `--quiet` to suppress success messages

## Testing Strategy

### CLI Tests
- Command parsing (valid and invalid arguments)
- Error handling (missing arguments, invalid values)
- Exit codes (success and failure cases)
- Help messages (completeness and accuracy)

### Integration Tests
- Full workflow: add → log → view → streak → export
- Multiple commands in sequence
- Database persistence across invocations

### Edge Cases
- Non-existent habits
- Invalid date formats
- Missing required arguments
- File system errors (DB not writable)
