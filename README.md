# subtitlesinswahili

Production-ready, containerized MVP for translating English `.srt` subtitles to Swahili using Django + React + Celery + Redis + Ollama.

## Architecture

- **backend**: Django API (`/api/upload`, `/api/status/<id>`, `/api/download/<id>`) running with Gunicorn.
- **celery_worker**: Asynchronous translation jobs via Celery.
- **frontend**: React app served by Nginx.
- **redis**: Broker/result backend for Celery.
- **ollama**: LLM translation engine endpoint (`/api/generate`).

## Local development with Docker Compose

1. Copy environment file:
   ```bash
   cp .env.example .env
   ```
2. Build and run:
   ```bash
   docker-compose up --build
   ```
3. Access:
   - Frontend: `http://localhost:3000`
   - Backend API: `http://localhost:8000`
   - Ollama API: `http://localhost:11434`

> If you run Ollama externally, set `OLLAMA_BASE_URL` in `.env` (for example `http://host.docker.internal:11434`) and keep the `ollama` service disabled.

## Running tests

### Backend
```bash
cd backend
pip install -r requirements.txt
pytest
```

### Frontend
```bash
cd frontend
npm install
npm test -- --watchAll=false
```

## CI/CD (GitHub Actions)

Workflow: `.github/workflows/ci-cd.yml`

On every push to `main`, GitHub Actions will:
1. Run backend tests.
2. Run frontend tests.
3. Build backend/frontend Docker images.
4. Push images to GHCR with tags:
   - `latest`
   - commit SHA (`sha-<shortsha>`)
   - git tag ref when available (semantic version tags supported if tags exist).

Image names:
- `ghcr.io/<repo>/backend:latest`
- `ghcr.io/<repo>/backend:<git-sha>`
- `ghcr.io/<repo>/frontend:latest`
- `ghcr.io/<repo>/frontend:<git-sha>`

## Required GitHub Secrets

Set repository secrets:
- `GHCR_USERNAME`: GHCR username.
- `GHCR_TOKEN`: token with `write:packages` permission.
- Any runtime secrets used by your deployment environment (for example `SECRET_KEY`) should remain in secret stores, not in source control.

## Deployment notes

- Backend runs migrations automatically at container start.
- Media/static are persisted via Docker volumes (`media_data`, `static_data`).
- Services use `restart: unless-stopped` for resiliency.
