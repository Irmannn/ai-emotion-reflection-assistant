# Backend

FastAPI backend for the AI emotion reflection assistant.

## Local Development

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
uvicorn app.main:app --reload
```

Health check:

```bash
curl http://localhost:8000/health
```

Expected response:

```json
{"status":"ok"}
```

API docs:

```text
http://localhost:8000/docs
```

Stage 2 database APIs:

```text
POST   /api/reflections
GET    /api/reflections?session_id=demo-session
GET    /api/reflections/{id}?session_id=demo-session
DELETE /api/reflections/{id}?session_id=demo-session
POST   /api/reflections/{id}/feedback
```
