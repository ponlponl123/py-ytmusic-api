# Logging Guide

## Overview

The YT Music API now has comprehensive error logging that captures all errors, exceptions, requests, and responses to the `ytmusic_api.log` file.

## What Gets Logged

### 1. **Application Lifecycle**

- Server startup with timestamp
- Server shutdown with timestamp

### 2. **All HTTP Requests**

- Request method (GET, POST, etc.)
- Request path
- Client IP address
- Request duration
- Response status code

### 3. **All Errors**

- HTTP exceptions (404, 500, etc.)
- Validation errors (422)
- KeyError with full traceback
- Connection errors
- Timeout errors
- All uncaught exceptions with full traceback

### 4. **Error Context**

- Error type and message
- Operation being performed
- Identifiers (video ID, channel ID, etc.)
- Full stack trace for debugging

## Log Format

Logs are written in the following format:

```
YYYY-MM-DD HH:MM:SS,mmm - module_name - LEVEL - message
```

Example:

```
2025-11-02 16:51:27,123 - src.main - INFO - Incoming Request: GET /search/health | Client: 127.0.0.1
2025-11-02 16:51:27,456 - src.utils.error_handlers - ERROR - KeyError in search for videoId: 'header'
```

## Log File Location

The log file is created in the root directory of the project:

```
ytmusic_api.log
```

## Viewing Logs

### Using the Log Viewer Utility

We've included a handy utility script `view_logs.py` for viewing and managing logs:

#### View last 50 lines (default):

```bash
python view_logs.py view
```

#### View last 100 lines:

```bash
python view_logs.py view 100
```

#### View only ERROR level logs:

```bash
python view_logs.py view 50 ERROR
```

#### View only errors:

```bash
python view_logs.py errors
```

#### View log statistics:

```bash
python view_logs.py stats
```

#### Archive logs:

```bash
python view_logs.py archive
```

This creates a timestamped backup (e.g., `ytmusic_api_20251102_165127.log`) and clears the current log.

#### Clear logs:

```bash
python view_logs.py clear
```

### Using Standard Tools

#### Windows PowerShell:

```powershell
# View last 50 lines
Get-Content ytmusic_api.log -Tail 50

# View and follow (live updates)
Get-Content ytmusic_api.log -Wait -Tail 50

# Search for errors
Select-String -Path ytmusic_api.log -Pattern "ERROR"

# Count errors
(Select-String -Path ytmusic_api.log -Pattern "ERROR").Count
```

#### Linux/Mac:

```bash
# View last 50 lines
tail -n 50 ytmusic_api.log

# Follow live
tail -f ytmusic_api.log

# Search for errors
grep "ERROR" ytmusic_api.log

# Count errors
grep -c "ERROR" ytmusic_api.log
```

## Log Levels

The application uses the following log levels:

- **INFO**: Normal operations, requests, and responses
- **WARNING**: Warnings that don't stop execution
- **ERROR**: Errors that occurred but were handled
- **CRITICAL**: Critical errors that may affect service

## Log Rotation

By default, logs append to the same file. For production environments, consider:

### Option 1: Manual Rotation

Use the archive utility:

```bash
python view_logs.py archive
```

### Option 2: Automatic Rotation (Advanced)

Modify `src/main.py` to use `RotatingFileHandler`:

```python
from logging.handlers import RotatingFileHandler

# Replace the FileHandler in logging.basicConfig with:
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        RotatingFileHandler(
            "ytmusic_api.log",
            maxBytes=10*1024*1024,  # 10 MB
            backupCount=5,           # Keep 5 backup files
            encoding='utf-8'
        ),
        logging.StreamHandler()
    ],
)
```

This will automatically rotate logs when they reach 10MB and keep the last 5 files.

## Troubleshooting

### Log file is too large

```bash
# Archive and start fresh
python view_logs.py archive

# Or clear completely
python view_logs.py clear
```

### Can't find specific errors

```bash
# Use the error-only view
python view_logs.py errors

# Or search with PowerShell
Select-String -Path ytmusic_api.log -Pattern "your_search_term" -Context 2,2
```

### Need logs from specific time period

```powershell
# PowerShell - logs from today
Get-Content ytmusic_api.log | Select-String "2025-11-02"

# PowerShell - logs between specific times
Get-Content ytmusic_api.log | Select-String "2025-11-02 (14|15|16):"
```

## Best Practices

1. **Regular Monitoring**: Check logs periodically for errors
2. **Archive Old Logs**: Use the archive feature to keep log files manageable
3. **Error Analysis**: Use `python view_logs.py stats` to track error trends
4. **Debug Mode**: For more detailed logging, change `level=logging.DEBUG` in `src/main.py`
5. **Production**: Consider implementing log rotation for long-running production servers

## Integration with Monitoring Tools

The log format is compatible with most log analysis tools:

- **Splunk**: Can parse the timestamp and log level
- **ELK Stack**: Use Filebeat to ship logs to Elasticsearch
- **CloudWatch**: Can ingest the log file directly
- **Papertrail**: Use remote_syslog2 to forward logs

## Example Log Entries

### Successful Request:

```
2025-11-02 16:51:27,123 - __main__ - INFO - Incoming Request: GET /search/health | Client: 127.0.0.1
2025-11-02 16:51:27,456 - __main__ - INFO - Response: 200 | Path: /search/health | Duration: 0.333s
```

### Error with Traceback:

```
2025-11-02 16:51:30,789 - src.utils.error_handlers - ERROR - KeyError in search for videoId: 'header'
Traceback (most recent call last):
  File "d:\github\py-ytmusic-api\src\utils\error_handlers.py", line 35, in wrapper
    return await func(*args, **kwargs)
  ...
KeyError: 'header'
```

### Application Lifecycle:

```
2025-11-02 16:51:00,000 - __main__ - INFO - ================================================================================
2025-11-02 16:51:00,001 - __main__ - INFO - YT Music API Starting Up
2025-11-02 16:51:00,002 - __main__ - INFO - Startup Time: 2025-11-02T16:51:00.000000
2025-11-02 16:51:00,003 - __main__ - INFO - ================================================================================
```
