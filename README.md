# GeM Bid Analyzer Platform

Complete tender intelligence workspace that ingests Government e-Marketplace (GeM) bid PDFs, extracts compliance-critical insights, packages branded summary reports, and lets teams collaborate over secure, authenticated workflows.

## Features

- **Automated PDF intelligence** ? detects technical specifications, certificates, ATC updates, BOQ/pricing, eligibility, and milestone dates using configurable keyword rules.
- **Executive reporting** ? generates HTML/Markdown/JSON outputs, compresses them into share-ready ZIP bundles, and offers one-click downloads and email dispatch.
- **Modern UI/UX** ? responsive React dashboard with drag-and-drop uploads, rule tuning panel, and real-time analysis history.
- **Authentication & security** ? JWT-based login/registration backed by hashed credentials and role-ready structure.
- **Deployment ready** ? Docker images for FastAPI backend and Vite/React frontend with optional MailHog for SMTP testing.

## Project structure

```
backend/         # FastAPI service and analysis pipeline
frontend/        # React + Vite web client
infrastructure/  # Docker Compose environment
```

### Backend (FastAPI)

- `app/main.py` ? application factory, CORS, routers
- `app/routers/` ? authentication, document ingest, report/email endpoints
- `app/services/` ? PDF parsing, NLP summariser (NLTK), report templating, email
- `app/templates/report.html` ? Jinja2 report template rendered into ZIP exports
- Storage paths: `storage/uploads` for raw PDFs, `storage/exports` for ZIP bundles

### Frontend (React + Vite + TypeScript)

- `src/pages/Login|Register|Dashboard` ? auth and main workflows
- `src/components` ? upload widget, rule editor, analysis cards, protected layout
- `src/hooks/useDocuments` ? fetch/upload/download/email orchestration
- `src/styles/global.css` ? cohesive UI theme tailored for bid teams

## Local development

### Prerequisites

- Python 3.11+
- Node.js 18+
- (Optional) Docker 24+

### Backend setup

```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env  # adjust secrets/SMTP as needed
uvicorn app.main:app --reload
```

### Frontend setup

```bash
cd frontend
npm install
npm run dev  # http://localhost:5173
```

Set `VITE_API_BASE_URL` in a `.env` file (defaults to `/api/v1` when using the Vite proxy).

### Integrated Docker environment

```bash
cd infrastructure
docker compose up --build
```

Services:

- `backend` ? FastAPI on `http://localhost:8000`
- `frontend` ? Nginx-hosted SPA on `http://localhost:5173`
- `mailhog` ? SMTP catcher (`smtp://localhost:1025`, UI `http://localhost:8025`)

Override the frontend API base during builds:

```bash
docker compose build frontend --build-arg VITE_API_BASE_URL=http://localhost:8000/api/v1
```

## Configuration

Environment variables (`backend/.env`):

- `DATABASE_URL` ? default SQLite file `sqlite:///./gem_analyzer.db`
- `JWT_SECRET_KEY` ? 32+ character secret
- `ALLOWED_ORIGINS` ? JSON array of permitted origins for CORS
- SMTP settings ? `SMTP_HOST`, `SMTP_PORT`, `SMTP_USERNAME`, `SMTP_PASSWORD`, `SMTP_USE_TLS`, `EMAIL_SENDER`

Frontend build arg: `VITE_API_BASE_URL` controls API root; defaults to `/api/v1` for same-origin proxy setups.

## Operational notes

- First-run downloads NLTK tokenizers/stopwords automatically.
- Email dispatch relies on the configured SMTP relay; use MailHog in development.
- Generated bundles (HTML/Markdown/JSON) are timestamped and stored under `storage/exports/<timestamp>/`.
- Extendable rule engine ? adjust default keywords or add new sections inside `app/schemas.py`.

## Roadmap ideas

- Background job queue (e.g., Celery) for long-running PDF parsing
- Multi-user organizations with role-based access
- Advanced NLP via transformer summarizers and named entity recognition
- Integration with GeM APIs for automated bid retrieval
