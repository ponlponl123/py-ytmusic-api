# YouTube Music API Error Handling & Troubleshooting Guide

This document provides comprehensive information about error handling in this YouTube Music API wrapper and how to troubleshoot common issues.

## 🚨 Common Error Types

### 1. KeyError: "Unable to find 'header'"

**This is the most common error and occurs when YouTube Music changes their internal API structure.**

#### **Symptoms:**

```
KeyError: "Unable to find 'header' using path ['header', 'musicCardShelfHeaderBasicRenderer', 'title', 'runs', 0, 'text'] on {...}"
```

#### **Causes:**

- YouTube Music has updated their internal API response structure
- The ytmusicapi library hasn't been updated to handle the new structure yet
- Specific search queries may trigger different response formats

#### **Solutions:**

1. **Try simplified search parameters:**

   - Reduce the `limit` parameter (try 5-10 instead of 20+)
   - Remove `scope` parameter from search requests
   - Use basic queries without special characters

2. **Use the health check endpoint:**

   ```bash
   GET /search/health
   ```

   This will tell you if the API is working and suggest workarounds.

3. **Update ytmusicapi:**

   ```bash
   pip install --upgrade ytmusicapi
   ```

4. **Retry with different parameters:**
   - If searching for artists, try searching for songs instead
   - Use more specific or generic search terms
   - Try different filters (`songs`, `videos`, `artists`, `albums`)

### 2. Authentication Errors (401)

#### **Symptoms:**

- "Authentication required" messages
- Unable to access library, playlists, or upload features

#### **Solutions:**

1. **For library/personal data access:** This API wrapper runs in read-only mode by default. Personal library access requires authentication setup.

2. **Check if the feature requires authentication:** Many browse features work without authentication, but library features require it.

### 3. Rate Limiting (429)

#### **Symptoms:**

- "Rate limit exceeded" or "Quota exceeded" messages
- Temporary inability to make requests

#### **Solutions:**

1. **Implement retry logic with exponential backoff**
2. **Reduce request frequency**
3. **Wait 60+ seconds before retrying**

### 4. Content Not Found (404)

#### **Symptoms:**

- "Not found" errors for specific content IDs
- Empty results for valid-looking IDs

#### **Causes:**

- Content has been removed or made private
- Invalid ID format
- Regional restrictions

#### **Solutions:**

1. **Validate ID formats:**

   - Video IDs: 11 characters (e.g., `dQw4w9WgXcQ`)
   - Channel IDs: 24 characters starting with `UC`
   - Playlist IDs: Various prefixes (`PL`, `RD`, `UU`, etc.)

2. **Try alternative content or search methods**

## 🔧 API Response Handling

### Graceful Degradation

All endpoints now implement graceful degradation:

1. **Primary attempt**: Try the full request with all parameters
2. **Fallback attempt**: If KeyError occurs, try simplified version
3. **Error response**: Return detailed error information with suggestions

### Error Response Format

All errors return structured JSON responses:

```json
{
  "error": "error_type",
  "message": "Human-readable error description",
  "operation": "operation_name",
  "identifier": "content_id_if_applicable",
  "technical_details": "raw_error_message",
  "solution": "suggested_workaround"
}
```

## 📊 Health Monitoring

### Health Check Endpoint

Use the health check endpoint to monitor API status:

```bash
GET /search/health
```

**Possible responses:**

- `healthy`: API working normally
- `degraded`: API has issues but may work with simplified requests
- `unhealthy`: API not working

### Logging

All errors are logged with appropriate severity levels:

- `ERROR`: Unexpected errors and KeyErrors
- `WARNING`: Fallback attempts and degraded service
- `INFO`: Normal operations and successful fallbacks

## 🛠️ Development Tips

### Testing Error Handling

1. **Test with known problematic queries** (queries that historically cause KeyErrors)
2. **Test with invalid IDs** to verify proper error responses
3. **Test rate limiting** by making rapid requests
4. **Monitor logs** for patterns in errors

### Handling Errors in Your Application

```python
import requests

try:
    response = requests.get("/search", params={"query": "test"})
    response.raise_for_status()
    data = response.json()

    # Check if response includes warnings
    if "warning" in data:
        print(f"Warning: {data['warning']}")

    return data["result"]

except requests.exceptions.HTTPError as e:
    if e.response.status_code == 503:
        # API structure issue - try again later or use simpler parameters
        print("YouTube Music API temporarily unavailable")
    elif e.response.status_code == 429:
        # Rate limited - wait and retry
        print("Rate limited - waiting...")
        time.sleep(60)
    else:
        # Handle other errors
        print(f"Error: {e.response.json()}")
```

## 📈 Best Practices

### 1. Implement Retry Logic

```python
import time
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# Configure retry strategy
retry_strategy = Retry(
    total=3,
    status_forcelist=[503, 504, 429],
    backoff_factor=1
)
```

### 2. Use Appropriate Timeouts

- Set reasonable timeout values for requests
- Implement circuit breaker patterns for repeated failures

### 3. Monitor API Health

- Regularly check the health endpoint
- Implement alerting for degraded service
- Have fallback strategies ready

### 4. Handle Partial Failures

- Many endpoints return partial results even when some data is unavailable
- Check for `warning` fields in responses
- Implement graceful degradation in your UI

## 🔍 Troubleshooting Checklist

When encountering issues:

1. ✅ **Check the health endpoint** first
2. ✅ **Review recent error logs** for patterns
3. ✅ **Try simplified parameters** (lower limits, fewer filters)
4. ✅ **Verify ID formats** for content-specific requests
5. ✅ **Check for rate limiting** (429 status codes)
6. ✅ **Update ytmusicapi** to latest version
7. ✅ **Test with different search queries** or content
8. ✅ **Implement proper error handling** in your application

## 📞 Getting Help

If you continue experiencing issues:

1. **Check the logs** for detailed error information
2. **Try the health check endpoint** for current status
3. **Review this troubleshooting guide**
4. **Check if the issue is widespread** by testing different queries
5. **Report persistent issues** with full error details and reproduction steps

## 🔄 Version Compatibility

- **ytmusicapi**: 1.11.1 (latest)
- **Python**: 3.8+
- **FastAPI**: Latest compatible version

Regular updates are recommended as YouTube Music frequently changes their internal APIs.
