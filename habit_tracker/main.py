"""
Main CLI entry point for habit tracker.

Command-line interface using argparse.
"""

import argparse
import sys
from pathlib import Path
from .database import Database
from .commands import HabitTrackerCommands
from .export import HabitExporter


def main():
    """Main entry point for CLI."""
    parser = argparse.ArgumentParser(
        description="Habit Tracker - Track and manage your daily habits",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  habit-tracker add "Morning Jog" --description "30 min jog"
  habit-tracker log "Morning Jog"
  habit-tracker list
  habit-tracker streak "Morning Jog"
  habit-tracker view "Morning Jog" --days 14
  habit-tracker delete "Morning Jog"
  habit-tracker export --type streaks
  habit-tracker export --type logs --start 2024-01-01 --end 2024-12-31
        """
    )
    
    parser.add_argument(
        "--db",
        default="habit_tracker.db",
        help="Path to database file (default: habit_tracker.db)"
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Add command
    add_parser = subparsers.add_parser("add", help="Add a new habit")
    add_parser.add_argument("name", help="Name of the habit")
    add_parser.add_argument(
        "--description", "-d",
        default="",
        help="Description of the habit"
    )
    
    # List command
    subparsers.add_parser("list", help="List all habits")
    
    # Delete command
    delete_parser = subparsers.add_parser("delete", help="Delete/archive a habit")
    delete_parser.add_argument("name", help="Name of the habit to delete")
    
    # Log command
    log_parser = subparsers.add_parser("log", help="Log a habit completion")
    log_parser.add_argument("name", help="Name of the habit")
    log_parser.add_argument(
        "--date",
        help="Date in YYYY-MM-DD format (default: today)"
    )
    log_parser.add_argument(
        "--notes", "-n",
        default="",
        help="Optional notes"
    )
    log_parser.add_argument(
        "--skip",
        action="store_true",
        help="Mark as not completed instead of completed"
    )
    
    # View command
    view_parser = subparsers.add_parser("view", help="View log entries")
    view_parser.add_argument(
        "name",
        nargs="?",
        help="Name of the habit (leave empty to see today's logs)"
    )
    view_parser.add_argument(
        "--days",
        type=int,
        default=7,
        help="Number of days to show (default: 7)"
    )
    
    # Streak command
    streak_parser = subparsers.add_parser("streak", help="View habit streaks")
    streak_parser.add_argument("name", help="Name of the habit")
    
    # Export command
    export_parser = subparsers.add_parser("export", help="Export data to CSV")
    export_parser.add_argument(
        "--type",
        choices=["habits", "logs", "streaks"],
        default="streaks",
        help="Type of export (default: streaks)"
    )
    export_parser.add_argument(
        "--start",
        help="Start date for logs export (YYYY-MM-DD)"
    )
    export_parser.add_argument(
        "--end",
        help="End date for logs export (YYYY-MM-DD)"
    )
    export_parser.add_argument(
        "--output",
        default=".",
        help="Output directory for CSV file (default: current directory)"
    )
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 0
    
    try:
        # Initialize database and commands
        db = Database(args.db)
        commands = HabitTrackerCommands(db)
        exporter = HabitExporter(db, args.output if hasattr(args, 'output') else ".")
        
        # Handle commands
        if args.command == "add":
            print(commands.add_habit(args.name, args.description))
        
        elif args.command == "list":
            print(commands.list_habits())
        
        elif args.command == "delete":
            print(commands.delete_habit(args.name))
        
        elif args.command == "log":
            completed = not args.skip if hasattr(args, 'skip') else True
            print(commands.log_completion(args.name, args.date, completed, args.notes))
        
        elif args.command == "view":
            print(commands.view_log(args.name, args.days))
        
        elif args.command == "streak":
            print(commands.view_streak(args.name))
        
        elif args.command == "export":
            if args.type == "logs":
                if not args.start or not args.end:
                    print("✗ Error: --start and --end dates required for logs export")
                    return 1
                filepath = exporter.export_logs(args.start, args.end)
            elif args.type == "habits":
                filepath = exporter.export_habits()
            else:  # streaks
                filepath = exporter.export_streaks()
            
            print(f"✓ Data exported to {filepath}")
        
        return 0
    
    except Exception as e:
        print(f"✗ Error: {str(e)}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
