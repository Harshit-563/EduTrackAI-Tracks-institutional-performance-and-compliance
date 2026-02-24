# Backend (FastAPI)

## Setup

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

## Frontend Integration

Frontend API base URL defaults to `http://localhost:8000`.
If needed, set `VITE_API_BASE_URL` in frontend env.

## Available Endpoints

- POST `/auth/login`
- GET `/auth/me`
- GET `/reviewer/queue`
- GET `/reviewer/document/{id}`
- POST `/reviews/{id}/action`
- POST `/upload-analyze`
- GET `/institutions/{id}/overview`
- GET `/institutions/{id}/dss-trend`
- GET `/institutions/{id}/submissions`
- GET `/health`
