# Error Logging Improvements

## Summary

Improved error logging to distinguish between genuine server errors and expected client errors (bad requests).

## Changes Made

### `src/routers/browsing.py`

#### `get_artist()` endpoint

| Before | After |
|--------|-------|
| All `KeyError` exceptions logged as `ERROR` | Playlist/album ID detection → `INFO` |
| No distinction for client mistakes | Wrong endpoint detection → `INFO` |
| | Genuine API errors → still `ERROR` |

#### `get_user()` endpoint

- **Added**: Playlist/album ID detection with `INFO`-level logging
- **Result**: Consistent error handling across user and artist endpoints

### `src/main.py`

#### `http_exception_handler()`

| Status Range | Log Level |
|---|---|
| 4xx (client errors) | `INFO` |
| 5xx (server errors) | `ERROR` |

#### `validation_exception_handler()`

- Validation errors (422) are now logged at `INFO` — they represent client input mistakes, not server failures.

---

## Benefits

### Cleaner Error Logs

- True server errors stand out clearly
- Expected client errors don't clutter the logs
- Easier to monitor application health

### Better Debugging

- `ERROR` now indicates actual problems requiring attention
- `INFO` shows normal operational events
- Reduced "false alarm" errors

### Improved Monitoring

- Log analysis tools can focus on `ERROR` level
- Alert systems won't trigger on expected client errors
- Clearer distinction between server issues and user input issues

---

## Error Classification

### INFO Level (Expected Issues)

- Client uses wrong endpoint (e.g., playlist ID on artist endpoint)
- Client provides invalid ID format
- Client provides invalid query parameters
- HTTP 400–499 status codes

### ERROR Level (Unexpected Issues)

- YouTube Music API structure changes unexpectedly
- Genuine parsing / `KeyError` issues
- HTTP 500–599 status codes
- Uncaught exceptions
- Network / connection issues

---

## Example Log Output

### Before

```
2025-11-02 20:05:16,372 - src.routers.browsing - ERROR - KeyError in get_artist for VLPLR48NTfP0M0OtpJgD2obWAuQF8yk0_F77: ...
2025-11-02 20:05:16,379 - src.main - ERROR - HTTP Exception: 400 - {...}
```

### After

```
2025-11-02 20:10:25,123 - src.routers.browsing - INFO - Client attempted to use playlist/album ID 'VLPLR...' on artist endpoint
2025-11-02 20:10:25,125 - src.main - INFO - HTTP Exception: 400 - {...}
```

---

## Testing

```bash
# 1. Start the server
python -m src.main

# 2. Send a bad request
curl http://localhost:8000/browse/artist/VLPLR48NTfP0M0OtpJgD2obWAuQF8yk0_F77

# 3. Inspect logs
python scripts/view_logs.py errors   # Should be empty (no ERROR for bad request)
python scripts/view_logs.py view 10  # Should show INFO for the request
```

**Expected error response:**

```json
{
  "error": "Invalid ID type",
  "message": "This appears to be a playlist or album ID, not an artist/channel ID",
  "channelId": "VLPLR48NTfP0M0OtpJgD2obWAuQF8yk0_F77",
  "recommendation": "Use /playlists/PLR48NTfP0M0OtpJgD2obWAuQF8yk0_F77 for playlists"
}
```

---

## Monitoring Recommendations

### Production

1. Set up alerts only for `ERROR` and `CRITICAL` levels
2. Use `INFO` level for audit trails and debugging
3. Periodically review `INFO` logs to identify patterns of client errors
4. Consider rate limiting if specific clients repeatedly make bad requests

### Log Rotation

```bash
# Archive logs daily/weekly
python scripts/view_logs.py archive

# Monitor error trends
python scripts/view_logs.py stats
```

---

## Future Enhancements

1. **Structured Logging**: JSON format for easier parsing
2. **Request IDs**: Track requests across multiple log entries
3. **Client Identification**: Log API keys or client IDs for abuse detection
4. **Rate Limiting**: Automatic throttling of clients with high error rates
5. **Metrics Export**: Prometheus/Grafana integration for real-time monitoring
