# Troubleshooting Guide

## Common Issues

### 1. KeyError: "Unable to find 'header'" in Search API

This is a common issue that occurs when YouTube Music changes their internal data structure, causing the ytmusicapi library to fail when parsing search results.

#### Symptoms

- Search requests return `KeyError` with message about missing `'header'` path
- Error occurs in ytmusicapi's `parse_top_result` function
- API was working previously but suddenly stopped

#### Solutions

1. **Check API Health**

   ```bash
   curl http://localhost:8000/search/health
   ```

2. **Use Simplified Search Parameters**
   - Remove the `scope` parameter
   - Use smaller `limit` values (≤ 10)
   - Avoid complex filters when possible

3. **Update ytmusicapi**

   ```bash
   pip install --upgrade ytmusicapi
   ```

4. **Retry with Fallback Options**
   The API automatically tries simplified parameters when the full search fails.

#### API Responses During Issues

When YouTube Music API structure changes occur, the API will:

- Return status code `503` (Service Unavailable) for parsing errors
- Attempt fallback searches with simplified parameters
- Include warning messages about reduced functionality
- Provide technical details in error responses

#### Example Error Response

```json
{
  "detail": {
    "error": "YouTube Music API structure has changed",
    "message": "The search service is temporarily experiencing issues due to YouTube Music API changes. Please try again later or contact support.",
    "query": "your search term",
    "technical_details": "Unable to find 'header' using path..."
  }
}
```

#### Prevention

- Keep ytmusicapi updated to the latest version
- Monitor the health endpoint regularly
- Implement proper error handling in client applications

---

### 2. Authentication Errors (401)

- **Cause**: Accessing library, playlists, or uploads without authentication
- **Solution**: Personal library access requires authentication credentials. Browse features work unauthenticated.

---

### 3. Rate Limiting (429)

YouTube Music may rate limit requests. If you experience this:

- Add delays between requests
- Reduce request frequency
- Implement exponential backoff with retries

---

### 4. Wrong ID Type on Endpoint

If you pass a playlist ID to an artist endpoint (or vice versa), the API returns a helpful `400 Bad Request` with a recommendation:

```json
{
  "error": "Invalid ID type",
  "message": "This appears to be a playlist or album ID, not an artist/channel ID",
  "recommendation": "Use /playlists/<id> for playlist IDs"
}
```

---

### 5. Network Issues

- Check internet connectivity
- Verify no firewall blocking
- Test with simple queries first

---

## Quick Diagnostic Steps

```bash
# 1. Is the server running?
curl http://localhost:8000/

# 2. Is the YTMusic backend reachable?
curl http://localhost:8000/api/status

# 3. Is search working?
curl http://localhost:8000/search/health

# 4. Check logs for errors
python scripts/view_logs.py errors
python scripts/view_logs.py stats
```

---

## Additional Resources

- [Error Handling Guide](error-handling-guide.md) — Detailed guide for all error types
- [Logging Guide](logging-guide.md) — How to view and manage logs
- [API Reference](api.md) — Full API documentation

---

## Getting Help

If issues persist:

1. Check the logs for detailed error information
2. Review the [Error Handling Guide](error-handling-guide.md)
3. Check if the issue is widespread by testing different queries
4. Report persistent issues with full error details and reproduction steps to the [GitHub repository](https://github.com/ponlponl123/py-ytmusic-api/issues)
