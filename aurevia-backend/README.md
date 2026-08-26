# Aurevia Backend

FastAPI backend for the Aurevia mental health app: auth, journaling, and an
AI chat companion, backed by a relational database.

## Project structure

```
app/
  main.py              # app entrypoint, wires everything together
  core/
    config.py           # env-based settings
    security.py          # password hashing + JWT
  db/
    database.py           # SQLAlchemy engine/session
  models/                 # SQLAlchemy ORM models (User, JournalEntry, ChatSession, ChatMessage)
  schemas/                # Pydantic request/response models
  services/                # business logic (auth, journal, chat, AI integration)
  api/                     # route definitions (thin — call services)
  middleware/              # request logging + global error handling
  tests/                   # pytest suite, in-memory DB, mocked AI calls
```

## 1. Setup

```bash
cd aurevia-backend
python -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env              # then fill in real values
```

By default `.env` points at Postgres. For quick local testing without
installing Postgres, set in `.env`:
```
DATABASE_URL=sqlite:///./aurevia.db
```

Fill in `AI_API_KEY` with your provider key (Anthropic key works as-is
against the default `AI_API_URL`/`AI_MODEL`).

## 2. Run the server

```bash
uvicorn app.main:app --reload
```

- API root: http://127.0.0.1:8000
- Interactive docs: http://127.0.0.1:8000/docs
- Health check: http://127.0.0.1:8000/health

Tables are auto-created from the models on startup in dev. For production,
switch to Alembic migrations (`alembic init alembic`) instead of relying on
`Base.metadata.create_all`.

## 3. Run tests

```bash
pytest app/tests -v
```

Tests use an isolated in-memory SQLite DB and mock the AI service call, so
they never hit your real database or the AI provider.

## 4. API overview

| Endpoint              | Method | Auth | Purpose                        |
|------------------------|--------|------|---------------------------------|
| `/auth/register`      | POST   | No   | Create an account               |
| `/auth/login`         | POST   | No   | Get a JWT access token          |
| `/users/me`           | GET    | Yes  | Current user profile            |
| `/journal`            | POST   | Yes  | Create a journal/mood entry     |
| `/journal`            | GET    | Yes  | List your journal entries       |
| `/journal/{id}`       | DELETE | Yes  | Delete a journal entry          |
| `/chat`               | POST   | Yes  | Send a message to the AI companion |
| `/health`             | GET    | No   | Liveness check                  |

Auth: pass `Authorization: Bearer <token>` on protected routes. Get a token
from `/auth/login`.

## 5. Notes on the AI chat safety layer

`app/services/ai_service.py` does a lightweight keyword check for
crisis-related language and prepends crisis-resource messaging when it
fires. This is a starting point, not a substitute for a real safety
pipeline — before shipping anything user-facing you'll want a proper
classifier, human escalation path, and review from someone with clinical/
safety expertise, given the subject matter.

## 6. Suggested next steps

- Add Alembic for real migrations instead of `create_all`.
- Add rate limiting on `/chat` (AI calls are the most expensive/abusable route).
- Add refresh tokens / token revocation if you need logout-everywhere.
- Add structured logging + request IDs for easier debugging in production.
- Wire this up against your actual frontend and confirm CORS origins in `.env`.
