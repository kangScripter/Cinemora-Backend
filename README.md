# API Streamripper

This project is a FastAPI-based API for movies and shows. Changes were made to prepare the project for production and Docker Compose deployment.

Quick start (local, using docker-compose):

1. Copy the example env file and edit values:

```powershell
cp .env.example .env
notepad .env
```

2. Build and start with docker-compose:

```powershell
docker-compose up --build -d
```

3. Access the API at http://localhost:8000 (or the port set in `HOST_PORT`).

Custom subdomain / base URL

- Set `BASE_URL` to a full URL (e.g. https://api.example.com) to make `sitemap.xml` use it.
- Or set `SUBDOMAIN` and `SCHEME` (and `HOST_PORT`) to construct a URL like `http://subdomain:8000`.

Notes & security

- The previous repository contained a hard-coded MongoDB connection string; it's recommended you set `MONGO_URI` in the environment and keep secrets out of the repository.
- The Dockerfile uses a minimal Python base image.

What's changed

- Endpoints made async where appropriate.
- Configuration via environment variables (MONGO_URI, BASE_URL, SUBDOMAIN).
- Added Dockerfile, docker-compose.yml and .env.example.
- Added python-dotenv to requirements and load .env in `web.py`.
