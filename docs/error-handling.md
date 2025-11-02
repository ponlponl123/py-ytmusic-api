# Error Handling Guide

This guide explains the comprehensive error handling implemented in the YT Music API and how to troubleshoot common issues.

## Overview

The YT Music API implements robust error handling to gracefully manage:

- YouTube Music API structure changes
- Network connectivity issues
- Authentication requirements
- Rate limiting
- Invalid parameters

## Common Error Types

### KeyError: "Unable to find 'header'"

This is the most frequent error, occurring when YouTube Music changes their internal API structure.

**Symptoms:**

```json
{
  "error": "API structure error",
  "message": "YouTube Music API structure has changed, search temporarily unavailable",
  "technical_details": "KeyError: Unable to find 'header'..."
}
```

**Solutions:**

1. Use simplified search parameters (lower limits)
2. Check the health endpoint: `/search/health`
3. Update ytmusicapi: `pip install --upgrade ytmusicapi`
4. Try different search filters

### Authentication Errors (401)

Some endpoints require YouTube Music authentication.

**Response:**

```json
{
  "error": "Authentication required",
  "message": "Authentication required to access library playlists"
}
```

**Solution:**
Set up authentication following the [ytmusicapi authentication guide](https://ytmusicapi.readthedocs.io/en/stable/setup.html).

### Rate Limiting (429)

**Response:**

```json
{
  "error": "Rate limit exceeded",
  "message": "API rate limit exceeded. Please try again later.",
  "retry_after": "60"
}
```

**Solution:**
Implement exponential backoff in your client code.

### Network Issues (503/504)

**Responses:**

```json
{
  "error": "Connection failed",
  "message": "Unable to connect to YouTube Music"
}
```

**Solution:**
Check internet connectivity and retry the request.

## Error Response Structure

All errors follow a consistent structure:

```json
{
  "error": "error_category",
  "message": "Human readable message",
  "operation": "operation_name",
  "identifier": "resource_id",
  "technical_details": "detailed_error_info"
}
```

## Health Monitoring

Monitor API health using these endpoints:

- **Global Status:** `/api/status`
- **Search Health:** `/search/health`

### Health Check Responses

**Operational:**

```json
{
  "status": "operational",
  "message": "All systems operational",
  "test_search_successful": true
}
```

**Degraded:**

```json
{
  "status": "degraded",
  "message": "YouTube Music API structure issues detected",
  "recommendation": "Use simplified search parameters"
}
```

**Error:**

```json
{
  "status": "error",
  "message": "API connectivity issues",
  "recommendation": "Check internet connection and try again"
}
```

## Fallback Mechanisms

The API implements automatic fallbacks:

1. **Simplified Parameters:** Reduces complexity when structure errors occur
2. **Alternative Endpoints:** Uses different ytmusicapi methods when available
3. **Graceful Degradation:** Returns partial results when possible
4. **Retry Logic:** Automatic retries with exponential backoff

## Best Practices

### For Client Applications

1. **Always check health endpoints** before making requests
2. **Implement retry logic** with exponential backoff
3. **Handle rate limiting** gracefully
4. **Parse error responses** to provide user-friendly messages
5. **Monitor API status** for proactive issue detection

### Example Client Code

```python
import requests
import time
import random

def safe_api_call(url, max_retries=3):
    for attempt in range(max_retries):
        try:
            response = requests.get(url)

            if response.status_code == 200:
                return response.json()
            elif response.status_code == 429:
                # Rate limited - wait and retry
                wait_time = 2 ** attempt + random.uniform(0, 1)
                time.sleep(wait_time)
                continue
            elif response.status_code == 503:
                # Service degraded - check health
                health = requests.get("/search/health").json()
                if health["status"] != "operational":
                    print(f"API Issue: {health['message']}")
                    return None

        except requests.exceptions.RequestException as e:
            print(f"Network error: {e}")
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)
                continue

    return None
```

## Troubleshooting Steps

1. **Check API Status**

   ```bash
   curl https://your-api-url/api/status
   ```

2. **Test Basic Search**

   ```bash
   curl "https://your-api-url/search?query=test&limit=5"
   ```

3. **Check Logs**
   Review `ytmusic_api.log` for detailed error information

4. **Update Dependencies**

   ```bash
   pip install --upgrade ytmusicapi fastapi
   ```

5. **Verify Network Connectivity**
   ```bash
   curl https://music.youtube.com
   ```

## Getting Help

If issues persist:

1. Check the [GitHub Issues](https://github.com/ponlponl123/py-ytmusic-api/issues)
2. Review the [ytmusicapi documentation](https://ytmusicapi.readthedocs.io/)
3. Create a detailed bug report with:
   - Error messages
   - Request parameters
   - Health check results
   - Log excerpts
