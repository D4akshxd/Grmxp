from __future__ import annotations

import json
from pathlib import Path
from typing import Annotated, List

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from ..core.config import get_settings
from ..core.database import get_db
from ..core.dependencies import get_current_user
from ..models import Document, TranslationJob, User
from ..schemas import (
    TranslationCreateResponse,
    TranslationJobListResponse,
    TranslationJobRead,
    TranslationLanguage,
    TranslationOutput,
)
from ..services.storage import save_upload_file
from ..services.translation_bundle import create_translation_bundle
from ..services.translator import PDFTranslationService, TranslationProviderError


router = APIRouter(prefix="/translations", tags=["translations"])
settings = get_settings()
translation_service = PDFTranslationService()


def _parse_language_codes(raw_languages: str | None) -> List[str]:
    if not raw_languages:
        return []

    parsed: List[str] = []
    try:
        data = json.loads(raw_languages)
    except json.JSONDecodeError:
        data = None

    if isinstance(data, list):
        parsed = [str(item).strip().lower() for item in data if str(item).strip()]
    else:
        parsed = [code.strip().lower() for code in raw_languages.split(",") if code.strip()]

    # Deduplicate while preserving order
    seen: set[str] = set()
    unique_codes: List[str] = []
    for code in parsed:
        if code not in seen:
            seen.add(code)
            unique_codes.append(code)
    return unique_codes


@router.get("/languages", response_model=List[TranslationLanguage])
def list_languages() -> List[TranslationLanguage]:
    return [TranslationLanguage(**item) for item in translation_service.list_supported_languages()]


@router.get("", response_model=TranslationJobListResponse)
def list_translation_jobs(
    *,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> TranslationJobListResponse:
    jobs = (
        db.query(TranslationJob)
        .join(Document)
        .filter(Document.owner_id == current_user.id)
        .order_by(TranslationJob.created_at.desc())
        .all()
    )

    items: List[TranslationJobRead] = []
    for job in jobs:
        translations_payload = job.translations or []
        translation_outputs = [TranslationOutput(**payload) for payload in translations_payload]
        download_url = (
            f"{settings.api_v1_prefix}/translations/{job.id}/download" if job.export_path else None
        )
        items.append(
            TranslationJobRead(
                id=job.id,
                document_id=job.document_id,
                document_name=job.document.original_filename,
                created_at=job.created_at,
                status=job.status,
                target_languages=job.target_languages or [],
                translations=translation_outputs,
                download_url=download_url,
            )
        )

    return TranslationJobListResponse(items=items, total=len(items))


@router.post("/translate", response_model=TranslationCreateResponse, status_code=status.HTTP_201_CREATED)
async def translate_document(
    *,
    file: UploadFile = File(...),
    languages: Annotated[str | None, Form(alias="languages")] = None,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> TranslationCreateResponse:
    if file.content_type not in {"application/pdf"}:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Only PDF files are supported")

    language_codes = _parse_language_codes(languages)
    if not language_codes:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="At least one target language is required")

    for code in language_codes:
        if not translation_service.get_language_name(code):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unsupported language code: {code}",
            )

    stored_path = await save_upload_file(file)

    document = Document(
        owner_id=current_user.id,
        original_filename=file.filename or stored_path.name,
        stored_filename=stored_path.name,
        content_type=file.content_type or "application/pdf",
        file_size=stored_path.stat().st_size,
        status="translating",
    )
    db.add(document)
    db.commit()
    db.refresh(document)

    job = TranslationJob(
        document_id=document.id,
        status="processing",
        target_languages=language_codes,
    )
    db.add(job)
    db.commit()
    db.refresh(job)

    try:
        translation_results = translation_service.translate_pdf(stored_path, language_codes)
    except TranslationProviderError as exc:
        document.status = "failed"
        job.status = "failed"
        db.add_all([document, job])
        db.commit()
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=f"Translation failed: {exc}")
    except Exception:
        document.status = "failed"
        job.status = "failed"
        db.add_all([document, job])
        db.commit()
        raise

    job.translations = [result.to_dict() for result in translation_results]
    document.status = "completed"
    job.status = "completed"

    export_path = None
    if translation_results:
        export_path = create_translation_bundle(
            document_name=document.original_filename,
            translations=translation_results,
        )
        job.export_path = str(export_path)

    db.add_all([document, job])
    db.commit()
    db.refresh(job)

    download_url = (
        f"{settings.api_v1_prefix}/translations/{job.id}/download" if job.export_path else None
    )

    return TranslationCreateResponse(
        document_id=document.id,
        job_id=job.id,
        status=job.status,
        translations=[TranslationOutput(**payload) for payload in job.translations],
        download_url=download_url,
    )


@router.get("/{job_id}/download")
def download_translation_bundle(
    *,
    job_id: int,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    job = (
        db.query(TranslationJob)
        .join(Document)
        .filter(TranslationJob.id == job_id, Document.owner_id == current_user.id)
        .first()
    )
    if not job or not job.export_path:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Translation bundle not found")

    export_path = Path(job.export_path)
    if not export_path.exists():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Translation bundle missing on server")

    document_name = job.document.original_filename
    filename = f"{Path(document_name).stem}_translations.zip"
    return FileResponse(path=str(export_path), filename=filename)
