# YT Music API Documentation

Welcome to the comprehensive YouTube Music API wrapper documentation!

## Overview

This FastAPI-based service provides a robust interface to YouTube Music with comprehensive error handling and monitoring capabilities.

## Features

- 🎵 **Complete YouTube Music Integration** - Search, browse, and interact with YouTube Music content
- 🛡️ **Robust Error Handling** - Comprehensive error handling for API structure changes
- 📊 **Health Monitoring** - Real-time API status and health checks
- 🔄 **Automatic Fallbacks** - Graceful degradation when YouTube Music API changes
- 📚 **Comprehensive Documentation** - Full API documentation with examples
- 🚀 **Production Ready** - Docker support and deployment guides

## Quick Start

### Local Development

1. Clone the repository:

```bash
git clone https://github.com/ponlponl123/py-ytmusic-api.git
cd py-ytmusic-api
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Run the server:

```bash
python -m src.main
```

4. Access the API documentation:

- Interactive docs: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### Docker Deployment

```bash
# Build the image
docker build -t ytmusic-api .

# Run the container
docker run -p 8000:8000 ytmusic-api
```

## API Endpoints

The API is organized into several main categories:

### 🔍 Search (`/search`)

- Search for songs, artists, albums, and playlists
- Get search suggestions
- Remove search history

### 🎼 Browse (`/browse`)

- Get artist information and content
- Browse albums and songs
- Access user profiles and content
- Get lyrics and related content

### 🎯 Explore (`/explore`)

- Discover mood-based playlists
- Browse music charts by country

### 📺 Watch (`/watch`)

- Get watch playlists for videos
- Access mood categories

### 📚 Library (`/library`)

- Manage personal music library
- Rate songs and playlists
- Subscribe to artists
- Edit library status

### 📋 Playlists (`/playlists`)

- Create, edit, and delete playlists
- Add and remove playlist items
- Manage playlist metadata

### 🎙️ Podcasts (`/podcasts`)

- Access podcast channels
- Get podcast episodes

### 📤 Uploads (`/uploads`)

- Upload music files
- Manage uploaded content

## Error Handling

The API includes comprehensive error handling for:

- YouTube Music API structure changes
- Network connectivity issues
- Authentication errors
- Rate limiting
- Invalid input parameters

See the [Error Handling Guide](error-handling.md) for detailed information.

## Health Monitoring

Monitor API status at:

- Global status: `/api/status`
- Search health: `/search/health`

## Support

For issues and support, please visit the [GitHub repository](https://github.com/ponlponl123/py-ytmusic-api).
