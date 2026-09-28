# AI CareerPilot

**AI-Powered Career Readiness & Employability Platform** — Campus → Skills → Preparation → Employment.

Built for the MPOnline Idea & Innovation Hackathon 2026 — Challenge 1: *AI-Powered Career Readiness & Employability Platform*.

AI CareerPilot builds a personalized Career Readiness Profile for every student: it analyzes their academic
background, skills and resume; recommends suitable career paths; identifies skill gaps; generates a
month-by-month learning roadmap; improves their resume; runs AI-scored mock interviews; and surfaces
relevant internships, jobs and government opportunities.

## Table of contents

- [Architecture](#architecture)
- [Tech stack](#tech-stack)
- [Project structure](#project-structure)
- [Quick start](#quick-start)
- [Running with Docker](#running-with-docker)
- [Configuration](#configuration)
- [Seed data](#seed-data)
- [Admin access](#admin-access)
- [API overview](#api-overview)
- [Testing](#testing)
- [The Golden Path demo flow](#the-golden-path-demo-flow)

## Architecture

The platform uses a **hybrid AI architecture** — the whole system never depends on an LLM to function:

| Layer | Owns | Implementation |
|---|---|---|
| Deterministic Python | Auth, authorization, CRUD, eligibility, skill-gap math, career scoring, roadmap ordering | `backend/services/*` |
| ML / NLP | Semantic skill/career/course matching | `backend/ai/embeddings.py` (Sentence Transformers, falls back to a scikit-learn `HashingVectorizer`) |
| Vector search | Fast similarity retrieval over catalog text | `backend/vector/faiss_index.py` (FAISS, falls back to a NumPy cosine scan) |
| LLM | Natural-language explanations, resume rewriting, interview questions/feedback | `backend/ai/llm_service.py` (any OpenAI-compatible endpoint; falls back to deterministic templates when no API key is set) |

An LLM is **never** allowed to decide eligibility, scores, or skill gaps — those are always computed in
plain Python first, and the LLM (when configured) only explains or phrases the result in natural language.
If no `LLM_API_KEY` is set, every AI-flavored feature (career explanations, resume coaching, interview
questions/feedback) still works, using template-based fallbacks instead.

```
React + Tailwind  →  FastAPI (REST/JSON)  →  Career Intelligence (skill-gap, scoring, roadmap)
                                            →  Resume pipeline (pypdf / python-docx → skill extraction)
                                            →  Sentence Transformers + FAISS (semantic matching)
                                            →  LLM (explanations, resume/interview coaching)
                                            →  SQLAlchemy → SQLite (dev) / PostgreSQL (production)
```

## Tech stack

- **Frontend:** React 19, Vite, Tailwind CSS v4, React Router, Axios
- **Backend:** Python 3.12+, FastAPI, Uvicorn, Pydantic v2, SQLAlchemy 2, Alembic migrations
- **Database:** SQLite (dev/MVP) → PostgreSQL-compatible (via `DATABASE_URL`)
- **Auth:** JWT (PyJWT), OAuth2 password flow, Argon2 password hashing, role-based access control
- **AI:** Provider-neutral OpenAI-compatible LLM client, Sentence Transformers, scikit-learn, FAISS
- **Resume processing:** pypdf, python-docx, optional Tesseract/pdf2image OCR
- **Testing:** pytest + FastAPI `TestClient`
- **DevOps:** Docker, docker-compose, `.env` configuration

## Project structure

```
AI_CareerPilot/
├── backend/
│   ├── main.py                  FastAPI app, router registration, CORS
│   ├── core/                    settings, JWT/password security, shared dependencies
│   ├── database/                SQLAlchemy Base, engine/session, 16 entity models, init_db
│   ├── schemas/                 Pydantic request/response schemas per entity
│   ├── api/routes/               one router per domain (auth, students, academic, skills, career,
│   │                             courses, resume, roadmap, interview, opportunities,
│   │                             recommendations, dashboard)
│   ├── services/                 deterministic business logic (skill gap, scoring, roadmap gen, ...)
│   ├── ai/                       llm_service, prompts, embeddings, career/resume/interview AI wrappers
│   ├── processing/               pdf_parser, docx_parser, ocr, skill_extractor
│   ├── vector/                   FAISS-backed (or NumPy fallback) semantic index
│   ├── seed/                     careers/skills/courses/certifications/opportunities JSON + loader
│   └── scripts/create_admin.py   out-of-band admin account provisioning (no public endpoint)
├── frontend/                     React + Vite + Tailwind SPA (see frontend/README below)
├── tests/                        pytest suite (auth, career flow, resume, interview, recommendations, ...)
├── alembic/                      migration environment (env.py reads DATABASE_URL from settings)
├── uploads/                      resume file storage (gitignored)
├── requirements.txt              core backend dependencies (always installed)
├── requirements-ai-extra.txt     optional heavier deps: sentence-transformers, faiss-cpu, OCR
├── Dockerfile / docker-compose.yml
└── .env.example
```

## Quick start

### Backend

Requires Python 3.12+.

```bash
python -m venv .venv
.venv\Scripts\activate          # Windows
# source .venv/bin/activate     # macOS/Linux

pip install -r requirements.txt
copy .env.example .env          # Windows: copy; macOS/Linux: cp

python -m backend.database.init_db
python -m backend.seed.seed_data
uvicorn backend.main:app --reload
```

Open `http://127.0.0.1:8000/docs` for the interactive Swagger UI (auto-generated OpenAPI docs).

**Optional AI extras** (Sentence Transformers, FAISS, OCR — the app runs correctly without these;
see [Architecture](#architecture)):

```bash
pip install -r requirements-ai-extra.txt
```

### Frontend

Requires Node.js 18+.

```bash
cd frontend
npm install
copy .env.example .env          # points VITE_API_BASE_URL at the backend
npm run dev
```

Open `http://localhost:5173`.

## Running with Docker

```bash
docker compose up --build
```

- Backend: `http://localhost:8000` (Swagger at `/docs`)
- Frontend: `http://localhost:8080`

The backend container runs `init_db` + `seed_data` automatically on startup (both are idempotent). Set
`SECRET_KEY` and, optionally, `LLM_API_KEY` via a `.env` file at the repo root before running compose —
`docker-compose.yml` reads them from the environment.

## Deploying to Render

`render.yaml` is a ready-to-use [Render Blueprint](https://render.com/docs/blueprint-spec) that
provisions a free Postgres database, the backend (as a Docker web service), and the frontend
(as a static site) in one go.

1. Push this repo to GitHub (see [Sharing this project](#sharing-this-project)).
2. In the Render dashboard: **New → Blueprint**, connect the repo, and apply. Render provisions
   `careerpilot-db`, `careerpilot-backend`, and `careerpilot-frontend`.
3. Once `careerpilot-backend` is live, copy its URL (e.g. `https://careerpilot-backend-xxxx.onrender.com`).
4. On `careerpilot-frontend` → Environment, set `VITE_API_BASE_URL` to `<that URL>/api`, then trigger
   **Manual Deploy** to rebuild with it baked in (Vite env vars are build-time only).
5. On `careerpilot-backend` → Environment, set `CORS_ALLOW_ORIGINS` to the frontend's URL
   (e.g. `https://careerpilot-frontend-xxxx.onrender.com`), then redeploy.
6. Optional: set `LLM_API_KEY` (and `LLM_BASE_URL`/`LLM_MODEL` if not using OpenAI) on the backend
   service to enable live LLM calls — everything works without it, via template fallbacks.

**Free-tier notes:** free web services spin down after inactivity (first request after idling takes
~30–60s to wake up), and the backend's filesystem is ephemeral, so uploaded resumes won't survive a
redeploy/restart — fine for a demo, not for production use. The database is real Postgres and persists.

## Sharing this project

**As source (GitHub):**

```bash
git init
git add .
git commit -m "AI CareerPilot: complete platform"
git branch -M main
git remote add origin <your-empty-github-repo-url>
git push -u origin main
```

Anyone can then clone it and follow [Quick start](#quick-start) or [Running with Docker](#running-with-docker).

**As a runnable package (Docker, no GitHub needed):** zip the project excluding build/dependency
artifacts, and anyone with Docker Desktop installed runs `docker compose up --build` and opens
`http://localhost:8080` — no Python/Node setup required on their machine. Exclude when zipping:
`.venv/`, `frontend/node_modules/`, `frontend/dist/`, `__pycache__/`, `.pytest_cache/`, `careerpilot.db`,
`uploads/`, `.env`, `frontend/.env` (all already in `.gitignore`, so `git archive` handles this
automatically once the repo is initialized).

## Configuration

All configuration is via environment variables (see `.env.example`). Key ones:

| Variable | Purpose |
|---|---|
| `DATABASE_URL` | SQLAlchemy URL. Defaults to local SQLite; swap for a PostgreSQL URL in production — no code changes needed. |
| `SECRET_KEY` | JWT signing secret. **Change this before any real deployment.** |
| `LLM_API_KEY` | If unset, all AI features use deterministic template fallbacks instead of calling an LLM. |
| `LLM_BASE_URL` / `LLM_MODEL` | Point at any OpenAI-compatible chat-completions endpoint (OpenAI, Azure OpenAI, a local vLLM/Ollama gateway, etc.). |
| `CORS_ALLOW_ORIGINS` | Comma-separated list of allowed frontend origins. |

## Database migrations

The dev workflow uses `init_db` (create-all) for speed, but the project is also Alembic-wired for
production-style migrations against the same `DATABASE_URL`:

```bash
alembic upgrade head                              # apply migrations
alembic revision --autogenerate -m "add X"         # generate a new migration after model changes
```

`alembic/env.py` reads `DATABASE_URL` from the app's own settings, so it always targets the same
database as the running app — no separate config to keep in sync.

## Seed data

`backend/seed/*.json` ships with 40 skills, 10 careers (with weighted career-skill requirements), 18
courses, 10 certifications, and 12 opportunities (internships, jobs, and government recruitment postings).
`python -m backend.seed.seed_data` loads them idempotently — safe to re-run any time.

## Admin access

There is **no public endpoint that grants admin access** — self-registration always creates a `student`
account (this was audited and locked down; see `backend/schemas/user.py`). To create or promote an admin:

```bash
python -m backend.scripts.create_admin admin@example.com "Admin Name" "StrongPassword123"
# or, to promote an existing user:
python -m backend.scripts.create_admin existing.user@example.com --promote
```

Admins can create/manage the catalog (skills, careers, career-skill requirements, courses,
certifications, opportunities) via the same REST API, gated by role.

## API overview

All endpoints are under `/api`, documented live at `/docs`. Highlights:

- `POST /api/auth/register`, `POST /api/auth/login`, `GET /api/auth/me`
- `POST /api/students/profiles`, `GET/PATCH /api/students/profiles/{id}`, `GET /api/students/profiles/me`
- `GET/POST /api/academic-records`, `GET /api/academic-records/me`
- `GET/POST /api/skills`, `GET /api/skills/me`, `POST /api/skills/assign`
- `GET/POST /api/careers`, `GET /api/careers/{id}/skill-gap`, `GET /api/careers/recommendations/me`
- `GET/POST /api/courses`, `GET/POST /api/certifications`
- `POST /api/resumes/upload`, `POST /api/resumes/{id}/improve`, `POST /api/resumes/{id}/sync-skills`
- `POST /api/roadmaps/generate/{career_id}`, `GET /api/roadmaps/me`, `PATCH /api/roadmaps/items/{id}`
- `POST /api/interview/sessions`, `.../next-question`, `.../submit`, `.../complete`
- `GET/POST /api/opportunities`, `GET /api/opportunities/matches/me`
- `GET /api/recommendations/me`, `POST /api/recommendations/{careers,courses,certifications}/generate...`
- `GET /api/dashboard/me` — aggregated readiness score, top career match, skill gaps, roadmap, courses

## Testing

```bash
.venv\Scripts\python.exe -m pytest tests/ -v
```

19 tests cover authentication/authorization (including the admin-escalation fix), the full
profile → skills → career → skill-gap → roadmap → dashboard flow, resume upload/extraction/skill-sync,
interview sessions, opportunity matching, and recommendation deduplication.

## The Golden Path demo flow

The strongest end-to-end story to demo to judges (see `project overview.docx`, §31):

```
Register → Create profile → Add skills → Explore a career → View skill gap
  → Generate roadmap → Generate course/certification recommendations
  → Upload resume → Get AI resume feedback → Run a mock interview
  → Browse matched internships/jobs/government opportunities
```

Every step above is wired end-to-end in both the API and the React dashboard.
