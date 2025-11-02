# YT Music API

A comprehensive YouTube Music API wrapper with robust error handling and monitoring capabilities.

Thanks to [ytmusicapi](https://github.com/sigma67/ytmusicapi) for the YouTube Music client/API and [FastAPI](https://github.com/fastapi/fastapi) for the API framework!

## 📚 Documentation

- **📖 Full Documentation:** [https://ponlponl123.github.io/py-ytmusic-api](https://ponlponl123.github.io/py-ytmusic-api)
- **🔧 Interactive API Docs:** [localhost:8000/docs](http://localhost:8000/docs) (when running locally)
- **📋 ReDoc:** [localhost:8000/redoc](http://localhost:8000/redoc) (when running locally)

## ✨ Features

- 🎵 Complete YouTube Music integration
- 🛡️ Comprehensive error handling for API changes
- 📊 Built-in health monitoring
- 🔄 Automatic fallback mechanisms
- 📚 Full API documentation
- 🐳 Docker support

## Setup

- create a virtual environment (optional)

- install python and pip

- install requirements: `pip install -r requirements.txt`

## run

- `default port: 8000`, `default host: 0.0.0.0`

- run the development server: `fastapi dev ./src/main.py`

- run the production server: `uvicorn src.main:app --host <specific-host> --port <specific-port>`

### run with gunicorn

- install gunicorn: `pip install gunicorn`

- run gunicorn: `gunicorn --bind <specific-host>:<specific-port>./src/main:app`

- or run with workers: `gunicorn -k uvicorn.workers.UvicornWorker src.main:app --bind 0.0.0.0:8000 --workers 4`

### for docker

- build the docker image: `docker build -t yt_music_api:latest .`
- run the docker container: `docker run -p 8000:8000 yt_music_api:latest`

## Usage

- API endpoints:
  - `/search/<query>`: search for a song, album, or artist.
  - `/lyrics/<videoid>`: get lyrics from video.
  - `/top_tracks?limit=<limit>`: get top tracks.
  - etc. **( More information in [localhost:8000/docs](localhost:8000/docs) )**
