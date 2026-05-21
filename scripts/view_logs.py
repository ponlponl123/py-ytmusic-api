#!/usr/bin/env python3
"""
Utility to view and manage the YT Music API log file.
The log file is expected at the project root: ytmusic_api.log

Run from the project root: python scripts/view_logs.py <command> [args]

Commands:
  view [N] [LEVEL]   View last N lines, optionally filtered by log level
  errors             View only ERROR and CRITICAL lines
  stats              Print log statistics
  clear              Clear the log file (with confirmation)
  archive            Archive the log with a timestamp and clear the original
"""

import os
import sys
from datetime import datetime
from pathlib import Path

# Resolve log file relative to project root (one level above scripts/)
PROJECT_ROOT = Path(__file__).parent.parent
LOG_FILE = PROJECT_ROOT / "ytmusic_api.log"


def _read_lines() -> list[str]:
    """Read all lines from the log file."""
    if not LOG_FILE.exists():
        print(f"Log file '{LOG_FILE}' not found!")
        sys.exit(1)
    with open(LOG_FILE, "r", encoding="utf-8") as fh:
        return fh.readlines()


def view_logs(lines: int = 50, level: str | None = None) -> None:
    """View the last N lines of the log file, optionally filtered by level."""
    all_lines = _read_lines()

    if level:
        all_lines = [line for line in all_lines if level.upper() in line]

    display_lines = all_lines[-lines:] if len(all_lines) > lines else all_lines

    print(f"\n{'=' * 80}")
    print(f"Log File: {LOG_FILE}")
    print(f"Total Lines: {len(all_lines)}")
    print(f"Displaying: {len(display_lines)} lines")
    if level:
        print(f"Filter: {level.upper()}")
    print(f"{'=' * 80}\n")

    for line in display_lines:
        print(line.rstrip())


def view_errors_only() -> None:
    """View only ERROR and CRITICAL level log entries."""
    all_lines = _read_lines()
    error_lines = [ln for ln in all_lines if "ERROR" in ln or "CRITICAL" in ln]

    print(f"\n{'=' * 80}")
    print("Error Log Summary")
    print(f"Total Errors/Criticals: {len(error_lines)}")
    print(f"{'=' * 80}\n")

    for line in error_lines:
        print(line.rstrip())


def log_stats() -> None:
    """Print statistics about the log file."""
    all_lines = _read_lines()

    counts = {
        "INFO": sum(1 for ln in all_lines if "INFO" in ln),
        "WARNING": sum(1 for ln in all_lines if "WARNING" in ln),
        "ERROR": sum(1 for ln in all_lines if "ERROR" in ln),
        "CRITICAL": sum(1 for ln in all_lines if "CRITICAL" in ln),
    }
    file_size_kb = os.path.getsize(LOG_FILE) / 1024

    print(f"\n{'=' * 80}")
    print(f"Log Statistics — {LOG_FILE}")
    print(f"{'=' * 80}")
    print(f"File Size:    {file_size_kb:.2f} KB")
    print(f"Total Lines:  {len(all_lines)}")
    print("\nLog Level Breakdown:")
    for lvl, count in counts.items():
        print(f"  {lvl:<10} {count}")
    print(f"{'=' * 80}\n")


def clear_logs() -> None:
    """Clear the log file after confirmation."""
    if not LOG_FILE.exists():
        print(f"Log file '{LOG_FILE}' not found!")
        return

    answer = input(f"Are you sure you want to clear {LOG_FILE}? (yes/no): ")
    if answer.lower() in ("yes", "y"):
        with open(LOG_FILE, "w", encoding="utf-8") as fh:
            fh.write(f"# Log cleared at {datetime.now().isoformat()}\n")
        print("Log file cleared!")
    else:
        print("Operation cancelled.")


def archive_logs() -> None:
    """Archive the current log with a timestamp and clear the original."""
    if not LOG_FILE.exists():
        print(f"Log file '{LOG_FILE}' not found!")
        return

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    archive_path = PROJECT_ROOT / f"ytmusic_api_{timestamp}.log"

    content = LOG_FILE.read_text(encoding="utf-8")
    archive_path.write_text(content, encoding="utf-8")

    with open(LOG_FILE, "w", encoding="utf-8") as fh:
        fh.write(f"# Log archived to {archive_path.name} at {datetime.now().isoformat()}\n")

    print(f"Log archived to: {archive_path}")
    print("Original log file cleared.")


def main() -> None:
    """Parse CLI arguments and dispatch to the appropriate function."""
    if len(sys.argv) < 2:
        print(__doc__)
        return

    command = sys.argv[1].lower()

    if command == "view":
        num_lines = int(sys.argv[2]) if len(sys.argv) > 2 else 50
        level_filter = sys.argv[3] if len(sys.argv) > 3 else None
        view_logs(num_lines, level_filter)
    elif command == "errors":
        view_errors_only()
    elif command == "stats":
        log_stats()
    elif command == "clear":
        clear_logs()
    elif command == "archive":
        archive_logs()
    else:
        print(f"Unknown command: {command}")
        print(__doc__)


if __name__ == "__main__":
    main()
