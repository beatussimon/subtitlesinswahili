# subtitlesinswahili

A containerized Django + React platform for a **Swahili subtitle marketplace-style catalog**.

## What changed in this overhaul

- Main experience is now a subtitle library organized by categories (Action, Drama, Comedy, plus translated uploads).
- Users can browse publicly, but must authenticate before downloads.
- Users can bookmark subtitles, leave comments, and submit subtitle requests for new movies.
- Translation on-the-fly remains available as a feature (upload `.srt`), and completed translations are added into the subtitle library.
- Translation payout/fee is set to **TSh 1000**.
- Initial sample subtitles are seeded automatically via migrations for easy preview.

## Architecture

- **backend**: Django API for auth, catalog, social features, requests, uploads, and downloads.
- **celery_worker**: Async translation jobs.
- **frontend**: React UI focused on category browsing and subtitle discovery.
- **redis**: Celery broker/backend.
- **ollama**: Translation engine endpoint (`/api/generate`).

## Local development with Docker Compose

1. Build and run:
   ```bash
   docker-compose up --build
   ```
2. Access:
   - Frontend: `http://localhost:3000`
   - Backend API: `http://localhost:8000`

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
