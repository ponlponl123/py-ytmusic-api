# Troubleshooting

This guide helps you troubleshoot common issues with the YT Music API.

## Common Issues

### KeyError: "Unable to find 'header'"

The most frequent issue occurs when YouTube Music changes their internal API structure.

**Symptoms:**

- Search requests fail with KeyError messages
- Previously working queries suddenly stop working
- Error mentions missing 'header' path in API response

**Quick Fixes:**

1. **Check API Health First**

   ```bash
   curl http://your-api-url/search/health
   ```

2. **Use Simplified Parameters**

   - Remove `scope` parameter from search
   - Reduce `limit` to 5-10 items
   - Use basic search queries

3. **Update Dependencies**
   ```bash
   pip install --upgrade ytmusicapi
   ```

**Expected API Response During Issues:**

```json
{
  "error": "API structure error",
  "message": "YouTube Music API structure has changed",
  "recommendation": "Use simplified search parameters",
  "status_code": 503
}
```

### Authentication Errors (401)

**Symptoms:**

- Requests to `/library/*` endpoints fail
- Error messages about authentication required
- Playlist creation/modification fails

**Solutions:**

1. **Set Up Authentication**
   Follow the [ytmusicapi authentication guide](https://ytmusicapi.readthedocs.io/en/stable/setup.html)

2. **Check Authentication File**
   Ensure your authentication file is properly configured and accessible

3. **Refresh Credentials**
   Re-authenticate if credentials have expired

### Rate Limiting (429)

**Symptoms:**

- Requests return 429 status code
- Error messages about rate limits exceeded
- Temporary blocking of requests

**Solutions:**

1. **Implement Backoff Strategy**

   ```python
   import time
   import random

   def retry_with_backoff(func, max_retries=3):
       for attempt in range(max_retries):
           try:
               return func()
           except RateLimitError:
               if attempt < max_retries - 1:
                   wait_time = (2 ** attempt) + random.uniform(0, 1)
                   time.sleep(wait_time)
       raise
   ```

2. **Reduce Request Frequency**
   - Add delays between requests
   - Batch operations when possible
   - Use lower limits in search queries

### Network Issues (503/504)

**Symptoms:**

- Connection timeouts
- Service unavailable errors
- Intermittent failures

**Solutions:**

1. **Check Internet Connectivity**

   ```bash
   curl https://music.youtube.com
   ```

2. **Verify API Status**

   ```bash
   curl http://your-api-url/api/status
   ```

3. **Implement Retry Logic**

   ```python
   import requests
   from requests.adapters import HTTPAdapter
   from urllib3.util.retry import Retry

   session = requests.Session()
   retry_strategy = Retry(
       total=3,
       backoff_factor=1,
       status_forcelist=[503, 504]
   )
   adapter = HTTPAdapter(max_retries=retry_strategy)
   session.mount("http://", adapter)
   session.mount("https://", adapter)
   ```

## Diagnostic Steps

### 1. Health Check Workflow

```bash
# Check global API status
curl http://your-api-url/api/status

# Check search functionality specifically
curl http://your-api-url/search/health

# Test basic search with minimal parameters
curl "http://your-api-url/search?query=test&limit=5"
```

### 2. Log Analysis

**Check Application Logs:**

```bash
tail -f ytmusic_api.log
```

**Common Log Patterns to Look For:**

- `KeyError: "Unable to find 'header'"` - API structure changes
- `ConnectionError` - Network issues
- `TimeoutError` - Request timeouts
- `AuthenticationError` - Authentication problems

### 3. Dependency Verification

**Check Installed Versions:**

```bash
pip list | grep -E "(ytmusicapi|fastapi|uvicorn)"
```

**Update Dependencies:**

```bash
pip install --upgrade ytmusicapi fastapi uvicorn
```

### 4. Configuration Validation

**Verify Environment:**

- Check Python version (3.8+ required)
- Validate virtual environment activation
- Confirm all dependencies installed

## Error Patterns & Solutions

### Pattern: Intermittent Failures

**Symptoms:** API works sometimes but fails randomly

**Likely Causes:**

- YouTube Music API instability
- Network connectivity issues
- Rate limiting

**Solutions:**

- Implement comprehensive retry logic
- Add jitter to request timing
- Monitor health endpoints

### Pattern: All Requests Failing

**Symptoms:** Every API call returns errors

**Likely Causes:**

- YouTube Music API major changes
- Authentication issues
- Network problems

**Solutions:**

1. Check API status endpoints
2. Verify internet connectivity
3. Update ytmusicapi library
4. Review authentication setup

### Pattern: Specific Endpoint Failures

**Symptoms:** Some endpoints work, others don't

**Likely Causes:**

- Partial API structure changes
- Feature-specific issues
- Permission problems

**Solutions:**

- Check individual router health
- Review endpoint-specific logs
- Test with minimal parameters

## Prevention Best Practices

### 1. Monitoring Setup

**Health Check Automation:**

```bash
#!/bin/bash
# health_check.sh
response=$(curl -s http://your-api-url/api/status | jq '.status')
if [ "$response" != '"operational"' ]; then
    echo "API Issue Detected: $response"
    # Send alert
fi
```

### 2. Client Implementation

**Robust Client Code:**

```python
class YTMusicAPIClient:
    def __init__(self, base_url):
        self.base_url = base_url
        self.session = self._create_session()

    def _create_session(self):
        session = requests.Session()
        retry_strategy = Retry(total=3, backoff_factor=1)
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        return session

    def safe_request(self, endpoint, params=None):
        try:
            response = self.session.get(
                f"{self.base_url}{endpoint}",
                params=params,
                timeout=30
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            # Handle specific error types
            return self._handle_error(e)
```

### 3. Update Strategy

**Regular Maintenance:**

- Monitor ytmusicapi releases
- Update dependencies weekly
- Test after YouTube Music updates
- Keep authentication fresh

## Getting Help

### 1. Information to Gather

When reporting issues, include:

- Error messages and stack traces
- Request parameters used
- Health check results
- Log file excerpts
- ytmusicapi version
- Operating system and Python version

### 2. Support Channels

- [GitHub Issues](https://github.com/ponlponl123/py-ytmusic-api/issues)
- [ytmusicapi Documentation](https://ytmusicapi.readthedocs.io/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)

### 3. Community Resources

- Check existing GitHub issues for similar problems
- Review ytmusicapi changelog for recent changes
- Monitor YouTube Music developer forums
