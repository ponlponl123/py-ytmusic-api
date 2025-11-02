# Error Logging Improvements

## Summary

Improved error logging to distinguish between genuine server errors and expected client errors (bad requests).

## Changes Made

### 1. Updated `src/routers/browsing.py`

#### Changed in `get_artist()` endpoint:

- **Before**: All KeyError exceptions logged as ERROR, creating noise in logs
- **After**:
  - Playlist/album ID detection: Logged as INFO (expected client error)
  - Wrong endpoint detection: Logged as INFO (expected client error)
  - Genuine API errors: Still logged as ERROR

#### Changed in `get_user()` endpoint:

- **Added**: Playlist/album ID detection with INFO-level logging
- **Result**: Consistent error handling across user and artist endpoints

### 2. Updated `src/main.py`

#### Changed in `http_exception_handler()`:

- **Before**: All HTTP exceptions logged as ERROR
- **After**:
  - 4xx client errors (400-499): Logged as INFO
  - 5xx server errors (500-599): Logged as ERROR

#### Changed in `validation_exception_handler()`:

- **Before**: Validation errors logged as ERROR
- **After**: Validation errors logged as INFO (client-side input errors)

## Benefits

### 1. **Cleaner Error Logs**

- True server errors stand out clearly
- Expected client errors don't clutter the logs
- Easier to monitor application health

### 2. **Better Debugging**

- ERROR level now indicates actual problems requiring attention
- INFO level shows normal operational events (including client mistakes)
- Reduced "false alarm" errors

### 3. **Improved Monitoring**

- Log analysis tools can focus on ERROR level
- Alert systems won't trigger on expected client errors
- Clearer distinction between server issues and user input issues

## Error Classification

### INFO Level (Expected Issues)

- Client uses wrong endpoint (e.g., playlist ID on artist endpoint)
- Client provides invalid ID format
- Client provides invalid query parameters
- HTTP 400-499 status codes (except 500-level delegated to 4xx)

### ERROR Level (Unexpected Issues)

- YouTube Music API structure changes unexpectedly
- Genuine parsing/KeyError issues
- HTTP 500-599 status codes
- Uncaught exceptions
- Network/connection issues

## Examples

### Before:

```
2025-11-02 20:05:16,372 - src.routers.browsing - ERROR - KeyError in get_artist for VLPLR48NTfP0M0OtpJgD2obWAuQF8yk0_F77: ...
2025-11-02 20:05:16,379 - src.main - ERROR - HTTP Exception: 400 - {...}
```

### After:

```
2025-11-02 20:10:25,123 - src.routers.browsing - INFO - Client attempted to use playlist/album ID 'VLPLR48NTfP0M0OtpJgD2obWAuQF8yk0_F77' on artist endpoint
2025-11-02 20:10:25,125 - src.main - INFO - HTTP Exception: 400 - {...}
```

## Testing

To test the improvements:

1. Start the API server:

   ```bash
   python -m src.main
   ```

2. Make a bad request (playlist ID on artist endpoint):

   ```bash
   curl http://localhost:8000/browse/artist/VLPLR48NTfP0M0OtpJgD2obWAuQF8yk0_F77
   ```

3. Check logs:

   ```bash
   python view_logs.py errors
   ```

   - Should NOT show ERROR level for the bad request

   ```bash
   python view_logs.py view 10
   ```

   - Should show INFO level for the bad request

4. The client receives helpful error message:
   ```json
   {
     "error": "Invalid ID type",
     "message": "This appears to be a playlist or album ID, not an artist/channel ID",
     "channelId": "VLPLR48NTfP0M0OtpJgD2obWAuQF8yk0_F77",
     "recommendation": "Use /playlists/PLR48NTfP0M0OtpJgD2obWAuQF8yk0_F77 for playlists"
   }
   ```

## Monitoring Recommendations

### For Production:

1. Set up alerts only for ERROR and CRITICAL levels
2. Use INFO level for audit trails and debugging
3. Periodically review INFO logs to identify patterns of client errors
4. Consider rate limiting if specific clients repeatedly make bad requests

### Log Rotation:

Use the provided `view_logs.py` utility:

```bash
# Archive logs daily/weekly
python view_logs.py archive

# Monitor error trends
python view_logs.py stats
```

## Future Enhancements

Consider adding:

1. **Structured Logging**: JSON format for easier parsing
2. **Request IDs**: Track requests across multiple log entries
3. **Client Identification**: Log API keys or client IDs for abuse detection
4. **Rate Limiting**: Automatic throttling of clients with high error rates
5. **Metrics Export**: Prometheus/Grafana integration for real-time monitoring
