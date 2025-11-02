# Troubleshooting Guide

## Common Issues

### KeyError: "Unable to find 'header'" in Search API

This is a common issue that occurs when YouTube Music changes their internal data structure, causing the ytmusicapi library to fail when parsing search results.

#### Symptoms

- Search requests return KeyError with message about missing 'header' path
- Error occurs in ytmusicapi's parse_top_result function
- API was working previously but suddenly stopped

#### Solutions

1. **Check API Health**

   ```bash
   curl http://localhost:8000/search/health
   ```

2. **Use Simplified Search Parameters**

   - Remove the `scope` parameter
   - Use smaller `limit` values (≤10)
   - Avoid complex filters when possible

3. **Update ytmusicapi Library**

   ```bash
   pip install --upgrade ytmusicapi
   ```

4. **Retry with Fallback Options**
   The API now automatically tries simplified parameters when the full search fails.

#### API Responses During Issues

When YouTube Music API structure changes occur, the API will:

- Return status code 503 (Service Unavailable) for parsing errors
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

### Other Common Issues

#### Rate Limiting

YouTube Music may rate limit requests. If you experience this:

- Add delays between requests
- Reduce request frequency
- Implement exponential backoff

#### Network Issues

- Check internet connectivity
- Verify no firewall blocking
- Test with simple queries first

## Contact

If issues persist, check the ytmusicapi GitHub repository for updates or file an issue with reproduction steps.
