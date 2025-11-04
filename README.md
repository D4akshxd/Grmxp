# AI PDF Translator

An end-to-end web application that translates uploaded PDFs into multiple languages with AI assistance. The FastAPI backend handles PDF text extraction, language-aware translations, and export bundles, while the React frontend delivers a polished workflow for choosing languages, reviewing results, and downloading artifacts.

## Features

- **Instant multi-language translation** – Upload a PDF and generate translations across up to six target languages in a single run.
- **Context-rich previews** – Inspect each translated page alongside the original source text directly in the dashboard.
- **Downloadable bundles** – Export Markdown + JSON manifests for every translation job in a timestamped ZIP package.
- **Persistent history** – Revisit previous translations at any time, re-open previews, and fetch bundles with one click.
- **Secure workflow** – JWT-secured authentication, durable storage for uploads/exports, and configurable translation providers (LibreTranslate by default).

## Project structure

```
backend/         # FastAPI service, translation pipeline, persistence
frontend/        # React + Vite UI for uploads, previews, history
infrastructure/  # Docker Compose environment for local orchestration
```

### Backend (FastAPI)

- `app/main.py` – application factory, CORS setup, router registration
- `app/routers/translations.py` – upload endpoint, supported language listing, history + bundle download
- `app/services/translator.py` – PDF text extraction & LibreTranslate integration
- `app/services/translation_bundle.py` – Markdown/manifest ZIP packaging
- `app/models.py` – `TranslationJob` ORM plus user/document tables
- Storage paths: `storage/uploads` for raw PDFs, `storage/exports/translations/<timestamp>` for generated bundles

### Frontend (React + Vite + TypeScript)

- `src/pages/Dashboard.tsx` – main translation workspace with upload, language picker, preview, and history
- `src/components/LanguageSelect.tsx` – multi-select widget with selection limits
- `src/components/TranslationViewer.tsx` – tabbed translation preview per language and per page
- `src/components/TranslationHistory.tsx` – job history list with view/download actions
- `src/hooks/useTranslations.ts` – orchestration hook for API calls, status flags, and downloads
- `src/styles/global.css` – cohesive styling, including new translator-specific components

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
cp .env.example .env  # adjust secrets/provider config as needed
uvicorn app.main:app --reload
```

### Frontend setup

```bash
cd frontend
npm install
npm run dev  # http://localhost:5173
```

Set `VITE_API_BASE_URL` in a `.env` file if you are proxying to a different backend origin (defaults to `/api/v1`).

### Integrated Docker environment

```bash
cd infrastructure
docker compose up --build
```

Services:

- `backend` – FastAPI on `http://localhost:8000`
- `frontend` – Vite dev server (or Nginx build) on `http://localhost:5173`
- `mailhog` – SMTP test harness (`smtp://localhost:1025`, UI `http://localhost:8025`)

Override the frontend API base during image builds:

```bash
docker compose build frontend --build-arg VITE_API_BASE_URL=http://localhost:8000/api/v1
```

## Configuration

Environment variables (`backend/.env`):

- `DATABASE_URL` – default `sqlite:///./gem_analyzer.db`
- `JWT_SECRET_KEY` – 32+ character secret
- `ALLOWED_ORIGINS` – JSON array of permitted origins for CORS
- `TRANSLATION_PROVIDER` – currently supports `libretranslate`
- `LIBRETRANSLATE_URL` – base URL for the LibreTranslate instance (default `https://libretranslate.de`)
- `LIBRETRANSLATE_API_KEY` – optional API key for secured instances
- `TRANSLATION_CHUNK_SIZE` / `TRANSLATION_CHUNK_OVERLAP` – character limits used while chunking PDF text (defaults: 3500 / 200)
- SMTP settings – `SMTP_HOST`, `SMTP_PORT`, `SMTP_USERNAME`, `SMTP_PASSWORD`, `SMTP_USE_TLS`, `EMAIL_SENDER`

Frontend build arg: `VITE_API_BASE_URL` controls the API root used by the SPA.

## Operational notes

- LibreTranslate is the default translation engine; configure the URL to point at your own instance for higher throughput or reliability.
- Translation bundles (Markdown + manifest) are saved under `storage/exports/translations/<timestamp>/` and exposed via `/api/v1/translations/{job_id}/download`.
- Upload size/timeouts depend on the upstream translation service; consider introducing background jobs for very large PDFs.
- Existing authentication and document models remain compatible with the new translation workflow.

## Roadmap ideas

- Background worker queue for long-running translation batches
- Additional providers (OpenAI, Azure Translator, DeepL) with automatic fallback
- Richer preview modes (side-by-side diff, search, glossary highlighting)
- Shared workspaces and collaboration on translation jobs
