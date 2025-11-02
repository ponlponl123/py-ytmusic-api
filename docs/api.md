# API Reference

This page provides interactive API documentation for all endpoints.

## Interactive Documentation

You can explore and test the API endpoints directly below:

{% swagger-ui-try-it-out %}
{% swagger-ui-set-url openapi.json %}

## OpenAPI Specification

The complete OpenAPI specification is available here:

[Download OpenAPI JSON](openapi.json){ .md-button .md-button--primary }

## Endpoint Categories

### Search Endpoints

- **GET /search** - Search YouTube Music content
- **GET /search/suggestions** - Get search suggestions
- **DELETE /search/suggestions** - Remove search suggestions
- **GET /search/health** - Search service health check

### Browse Endpoints

- **GET /browse/home** - Get home content
- **GET /browse/artist/{channelId}** - Get artist information
- **GET /browse/artist/{channelId}/albums** - Get artist albums
- **GET /browse/artist/{channelId}/videos** - Get artist videos
- **GET /browse/album/{browseId}** - Get album details
- **GET /browse/song/{videoId}** - Get song information
- **GET /browse/lyrics/{browseId}** - Get song lyrics

### Library Endpoints

- **GET /library/playlists** - Get library playlists
- **GET /library/songs** - Get library songs
- **POST /library/history/{videoId}** - Add item to history
- **DELETE /library/history** - Remove history items
- **POST /library/rate/song/{videoId}** - Rate a song
- **POST /library/rate/playlist/{playlistId}** - Rate a playlist

### Playlist Endpoints

- **GET /playlists/{playlistId}** - Get playlist details
- **POST /playlists** - Create new playlist
- **PUT /playlists/{playlistId}** - Edit playlist
- **DELETE /playlists/{playlistId}** - Delete playlist
- **POST /playlists/{playlistId}/items** - Add items to playlist
- **DELETE /playlists/{playlistId}/items** - Remove items from playlist

### Explore Endpoints

- **GET /explore/mood-playlists** - Get mood-based playlists
- **GET /explore/charts** - Get music charts

### Watch Endpoints

- **GET /watch/mood-categories** - Get mood categories
- **GET /watch/playlist/{videoId}** - Get watch playlist

### Podcast Endpoints

- **GET /podcasts/channel/{channelId}** - Get podcast channel
- **GET /podcasts/channel/{channelId}/episodes** - Get channel episodes

### Upload Endpoints

- **POST /uploads/song** - Upload song
- **DELETE /uploads/{entityId}** - Delete upload entity

## Authentication

Some endpoints require authentication. When authentication is needed, you'll receive a 401 error with instructions on how to authenticate with YouTube Music.

## Rate Limiting

The API implements rate limiting to prevent abuse. If you exceed the rate limits, you'll receive a 429 error with retry information.

## Error Responses

All endpoints return structured error responses with:

- **error**: Error category
- **message**: Human-readable error message
- **technical_details**: Technical information for debugging (when applicable)
- **operation**: The operation that failed
- **identifier**: The resource identifier (when applicable)
