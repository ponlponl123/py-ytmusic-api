"""
Simple utility to view and manage log files
"""
import os
import sys
from datetime import datetime


def view_logs(lines=50, level=None):
    """
    View the last N lines of the log file
    
    Args:
        lines: Number of lines to display from the end
        level: Filter by log level (INFO, ERROR, WARNING, etc.)
    """
    log_file = "ytmusic_api.log"
    
    if not os.path.exists(log_file):
        print(f"Log file '{log_file}' not found!")
        return
    
    with open(log_file, 'r', encoding='utf-8') as f:
        all_lines = f.readlines()
    
    # Filter by level if specified
    if level:
        all_lines = [line for line in all_lines if level.upper() in line]
    
    # Get the last N lines
    display_lines = all_lines[-lines:] if len(all_lines) > lines else all_lines
    
    print(f"\n{'='*80}")
    print(f"Log File: {log_file}")
    print(f"Total Lines: {len(all_lines)}")
    print(f"Displaying: {len(display_lines)} lines")
    if level:
        print(f"Filter: {level.upper()}")
    print(f"{'='*80}\n")
    
    for line in display_lines:
        print(line.rstrip())


def view_errors_only():
    """View only ERROR and CRITICAL level logs"""
    log_file = "ytmusic_api.log"
    
    if not os.path.exists(log_file):
        print(f"Log file '{log_file}' not found!")
        return
    
    with open(log_file, 'r', encoding='utf-8') as f:
        all_lines = f.readlines()
    
    error_lines = [line for line in all_lines if 'ERROR' in line or 'CRITICAL' in line]
    
    print(f"\n{'='*80}")
    print(f"Error Log Summary")
    print(f"Total Errors: {len(error_lines)}")
    print(f"{'='*80}\n")
    
    for line in error_lines:
        print(line.rstrip())


def log_stats():
    """Display statistics about the log file"""
    log_file = "ytmusic_api.log"
    
    if not os.path.exists(log_file):
        print(f"Log file '{log_file}' not found!")
        return
    
    with open(log_file, 'r', encoding='utf-8') as f:
        all_lines = f.readlines()
    
    info_count = sum(1 for line in all_lines if 'INFO' in line)
    warning_count = sum(1 for line in all_lines if 'WARNING' in line)
    error_count = sum(1 for line in all_lines if 'ERROR' in line)
    critical_count = sum(1 for line in all_lines if 'CRITICAL' in line)
    
    file_size = os.path.getsize(log_file) / 1024  # KB
    
    print(f"\n{'='*80}")
    print(f"Log Statistics for {log_file}")
    print(f"{'='*80}")
    print(f"File Size: {file_size:.2f} KB")
    print(f"Total Lines: {len(all_lines)}")
    print(f"\nLog Level Breakdown:")
    print(f"  INFO:     {info_count}")
    print(f"  WARNING:  {warning_count}")
    print(f"  ERROR:    {error_count}")
    print(f"  CRITICAL: {critical_count}")
    print(f"{'='*80}\n")


def clear_logs():
    """Clear the log file (with confirmation)"""
    log_file = "ytmusic_api.log"
    
    if not os.path.exists(log_file):
        print(f"Log file '{log_file}' not found!")
        return
    
    response = input(f"Are you sure you want to clear {log_file}? (yes/no): ")
    if response.lower() in ['yes', 'y']:
        with open(log_file, 'w', encoding='utf-8') as f:
            f.write(f"# Log cleared at {datetime.now().isoformat()}\n")
        print(f"Log file cleared!")
    else:
        print("Operation cancelled.")


def archive_logs():
    """Archive the current log file with timestamp"""
    log_file = "ytmusic_api.log"
    
    if not os.path.exists(log_file):
        print(f"Log file '{log_file}' not found!")
        return
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    archive_name = f"ytmusic_api_{timestamp}.log"
    
    # Copy the log file
    with open(log_file, 'r', encoding='utf-8') as src:
        content = src.read()
    
    with open(archive_name, 'w', encoding='utf-8') as dst:
        dst.write(content)
    
    # Clear the original log
    with open(log_file, 'w', encoding='utf-8') as f:
        f.write(f"# Log archived to {archive_name} at {datetime.now().isoformat()}\n")
    
    print(f"Log archived to: {archive_name}")
    print(f"Original log file cleared.")


def main():
    """Main function to handle command line arguments"""
    if len(sys.argv) < 2:
        print("YT Music API Log Viewer")
        print("\nUsage:")
        print("  python view_logs.py view [lines] [level]  - View last N lines (default: 50)")
        print("  python view_logs.py errors                - View only errors")
        print("  python view_logs.py stats                 - View log statistics")
        print("  python view_logs.py clear                 - Clear log file")
        print("  python view_logs.py archive               - Archive and clear log file")
        print("\nExamples:")
        print("  python view_logs.py view 100              - View last 100 lines")
        print("  python view_logs.py view 50 ERROR         - View last 50 ERROR lines")
        return
    
    command = sys.argv[1].lower()
    
    if command == 'view':
        lines = int(sys.argv[2]) if len(sys.argv) > 2 else 50
        level = sys.argv[3] if len(sys.argv) > 3 else None
        view_logs(lines, level)
    elif command == 'errors':
        view_errors_only()
    elif command == 'stats':
        log_stats()
    elif command == 'clear':
        clear_logs()
    elif command == 'archive':
        archive_logs()
    else:
        print(f"Unknown command: {command}")


if __name__ == "__main__":
    main()
