# Logging Guide

## Overview

The YT Music API has comprehensive logging that captures all errors, exceptions, requests, and responses to a log file (`ytmusic_api.log`, written to the project root when the server runs).

## What Gets Logged

| Category | Details |
|----------|---------|
| **Application lifecycle** | Server startup and shutdown timestamps |
| **HTTP requests** | Method, path, client IP, duration, response status |
| **Errors** | HTTP exceptions, validation errors, KeyError with traceback, connection/timeout errors |
| **Error context** | Error type, operation name, identifiers, full stack trace |

---

## Log Format

```
YYYY-MM-DD HH:MM:SS,mmm - module_name - LEVEL - message
```

**Example:**

```
2025-11-02 16:51:27,123 - src.main - INFO - Incoming Request: GET /search/health | Client: 127.0.0.1
2025-11-02 16:51:27,456 - src.utils.error_handlers - ERROR - KeyError in search for videoId: 'header'
```

---

## Log Levels

| Level | Meaning |
|-------|---------|
| `INFO` | Normal operations, requests, and responses |
| `WARNING` | Non-fatal warnings that don't stop execution |
| `ERROR` | Errors that occurred but were handled |
| `CRITICAL` | Critical errors that may affect service |

---

## Viewing Logs

### Using the Log Viewer Utility

The `scripts/view_logs.py` utility provides a simple interface:

```bash
# View last 50 lines (default)
python scripts/view_logs.py view

# View last 100 lines
python scripts/view_logs.py view 100

# View only ERROR-level logs
python scripts/view_logs.py view 50 ERROR

# View only errors and criticals
python scripts/view_logs.py errors

# Show log statistics
python scripts/view_logs.py stats

# Archive log and start fresh
python scripts/view_logs.py archive

# Clear log file (with confirmation)
python scripts/view_logs.py clear
```

### Using Platform Tools

**Windows PowerShell:**

```powershell
# View last 50 lines
Get-Content ytmusic_api.log -Tail 50

# Follow live (like tail -f)
Get-Content ytmusic_api.log -Wait -Tail 50

# Search for errors
Select-String -Path ytmusic_api.log -Pattern "ERROR"
```

**Linux / macOS:**

```bash
tail -n 50 ytmusic_api.log
tail -f ytmusic_api.log
grep "ERROR" ytmusic_api.log
grep -c "ERROR" ytmusic_api.log
```

---

## Log Rotation

By default, logs append to the same file. For production:

### Option 1 — Manual Rotation

```bash
python scripts/view_logs.py archive
```

This creates a timestamped backup (e.g., `ytmusic_api_20251102_165127.log`) and clears the current log.

### Option 2 — Automatic Rotation

Modify `src/main.py` to use `RotatingFileHandler`:

```python
from logging.handlers import RotatingFileHandler

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        RotatingFileHandler(
            "ytmusic_api.log",
            maxBytes=10 * 1024 * 1024,  # 10 MB
            backupCount=5,
            encoding="utf-8",
        ),
        logging.StreamHandler(),
    ],
)
```

---

## Troubleshooting

### Log file is too large

```bash
python scripts/view_logs.py archive
# or
python scripts/view_logs.py clear
```

### Can't find specific errors

```bash
python scripts/view_logs.py errors

# PowerShell with context
Select-String -Path ytmusic_api.log -Pattern "your_search_term" -Context 2,2
```

### Need logs from a specific time period

```powershell
Get-Content ytmusic_api.log | Select-String "2025-11-02"
Get-Content ytmusic_api.log | Select-String "2025-11-02 (14|15|16):"
```

---

## Best Practices

1. **Regular Monitoring**: Check logs periodically for errors
2. **Archive Old Logs**: Use the archive feature to keep log files manageable
3. **Error Analysis**: Use `python scripts/view_logs.py stats` to track error trends
4. **Debug Mode**: For more detailed logging, change `level=logging.DEBUG` in `src/main.py`
5. **Production**: Implement log rotation for long-running production servers

---

## Example Log Entries

### Successful request

```
2025-11-02 16:51:27,123 - __main__ - INFO - Incoming Request: GET /search/health | Client: 127.0.0.1
2025-11-02 16:51:27,456 - __main__ - INFO - Response: 200 | Path: /search/health | Duration: 0.333s
```

### Error with traceback

```
2025-11-02 16:51:30,789 - src.utils.error_handlers - ERROR - KeyError in search for videoId: 'header'
Traceback (most recent call last):
  ...
KeyError: 'header'
```

### Application lifecycle

```
2025-11-02 16:51:00,000 - __main__ - INFO - ================================================================================
2025-11-02 16:51:00,001 - __main__ - INFO - YT Music API Starting Up
2025-11-02 16:51:00,002 - __main__ - INFO - Startup Time: 2025-11-02T16:51:00.000000
2025-11-02 16:51:00,003 - __main__ - INFO - ================================================================================
```

---

## Integration with Monitoring Tools

The log format is compatible with:

| Tool | Integration Method |
|------|--------------------|
| **Splunk** | Parse timestamp and log level directly |
| **ELK Stack** | Use Filebeat to ship logs to Elasticsearch |
| **CloudWatch** | Ingest the log file directly |
| **Papertrail** | Forward via remote_syslog2 |
