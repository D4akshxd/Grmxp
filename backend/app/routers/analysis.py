from __future__ import annotations

import json
from pathlib import Path
from typing import Annotated, Dict, Optional

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from ..core.config import get_settings
from ..core.database import get_db
from ..core.dependencies import get_current_user
from ..models import AnalysisReport, Document, User
from ..schemas import AnalysisCreateResponse, AnalysisResult, DocumentListResponse, RuleConfig, SectionInsight
from ..services.pdf_analyzer import analyze_pdf
from ..services.report_builder import create_export_bundle
from ..services.storage import save_upload_file
from ..services.emailer import send_email


router = APIRouter(prefix="/documents", tags=["documents"])
settings = get_settings()


def _parse_rule_config(raw_rule_config: Optional[str]) -> RuleConfig:
    if not raw_rule_config:
        return RuleConfig()
    try:
        data = json.loads(raw_rule_config)
    except json.JSONDecodeError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid rule config JSON") from exc
    return RuleConfig(**data)


def _build_highlights(sections: Dict[str, Dict[str, str]]) -> Dict[str, str]:
    highlights: Dict[str, str] = {}
    for key, section in sections.items():
        summary = section.get("summary", "")
        highlight = summary.split(".")[0][:240] if summary else "No insight detected."
        highlights[key] = highlight
    return highlights


@router.post("/analyze", response_model=AnalysisCreateResponse, status_code=status.HTTP_201_CREATED)
async def analyze_document(
    *,
    file: UploadFile = File(...),
    rule_config: Optional[str] = None,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> AnalysisCreateResponse:
    if file.content_type not in {"application/pdf"}:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Only PDF files are supported")

    stored_path = await save_upload_file(file)
    rule_model = _parse_rule_config(rule_config)

    document = Document(
        owner_id=current_user.id,
        original_filename=file.filename or stored_path.name,
        stored_filename=stored_path.name,
        content_type=file.content_type or "application/pdf",
        file_size=stored_path.stat().st_size,
        status="processing",
        rule_config=rule_model.model_dump(),
    )
    db.add(document)
    db.commit()
    db.refresh(document)

    summary, section_models = analyze_pdf(stored_path, rule_model)
    sections_dict = {key: value.model_dump() for key, value in section_models.items()}
    highlights = _build_highlights(sections_dict)

    export_path = create_export_bundle(
        document_name=document.original_filename,
        summary=summary,
        highlights=highlights,
        sections=section_models,
        rule_config=rule_model.model_dump(),
        owner_email=current_user.email,
    )

    analysis = AnalysisReport(
        document_id=document.id,
        summary=summary,
        highlights=highlights,
        sections=sections_dict,
        rule_config=rule_model.model_dump(),
        zip_path=str(export_path),
        export_path=str(export_path),
    )
    document.status = "completed"

    db.add(analysis)
    db.commit()
    db.refresh(analysis)

    summary_preview = summary[:400] + ("..." if len(summary) > 400 else "")
    return AnalysisCreateResponse(
        document_id=document.id,
        analysis_id=analysis.id,
        status=document.status,
        summary_preview=summary_preview,
    )


@router.get("", response_model=DocumentListResponse)
def list_documents(
    *,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> DocumentListResponse:
    documents = (
        db.query(Document)
        .filter(Document.owner_id == current_user.id)
        .order_by(Document.uploaded_at.desc())
        .all()
    )

    items = []
    for doc in documents:
        latest_analysis = (
            db.query(AnalysisReport)
            .filter(AnalysisReport.document_id == doc.id)
            .order_by(AnalysisReport.created_at.desc())
            .first()
        )
        analysis_payload = None
        if latest_analysis:
            section_map = {
                key: SectionInsight(**value) if not isinstance(value, SectionInsight) else value
                for key, value in latest_analysis.sections.items()
            }
            analysis_payload = AnalysisResult(
                document_id=doc.id,
                analysis_id=latest_analysis.id,
                summary=latest_analysis.summary,
                highlights=latest_analysis.highlights,
                sections=section_map,
                created_at=latest_analysis.created_at,
            )
        items.append(
            {
                "id": doc.id,
                "original_filename": doc.original_filename,
                "uploaded_at": doc.uploaded_at,
                "status": doc.status,
                "latest_analysis": analysis_payload,
            }
        )

    return DocumentListResponse(items=items, total=len(items))


@router.get("/{document_id}/download")
def download_latest_bundle(
    *,
    document_id: int,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    document = (
        db.query(Document)
        .filter(Document.id == document_id, Document.owner_id == current_user.id)
        .first()
    )
    if not document:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")

    analysis = (
        db.query(AnalysisReport)
        .filter(AnalysisReport.document_id == document.id)
        .order_by(AnalysisReport.created_at.desc())
        .first()
    )
    if not analysis or not analysis.export_path:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Export not available")

    return FileResponse(path=analysis.export_path, filename=f"{document.original_filename}_analysis.zip")


@router.post("/{analysis_id}/email", status_code=status.HTTP_202_ACCEPTED)
def email_analysis_bundle(
    *,
    analysis_id: int,
    recipients: str,
    subject: Optional[str] = None,
    message: Optional[str] = None,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    analysis = (
        db.query(AnalysisReport)
        .join(Document)
        .filter(AnalysisReport.id == analysis_id, Document.owner_id == current_user.id)
        .first()
    )
    if not analysis or not analysis.export_path:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Analysis not found")

    recipient_list = [email.strip() for email in recipients.split(",") if email.strip()]
    if not recipient_list:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="At least one recipient is required")

    email_subject = subject or f"GeM Bid Summary - {analysis.document.original_filename}"
    email_body = message or "Please find the attached GeM bid analysis summary."

    try:
        send_email(
            recipients=recipient_list,
            subject=email_subject,
            body=email_body,
            attachment_path=Path(analysis.export_path),
        )
    except Exception as exc:  # pragma: no cover - relies on external SMTP
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail="Failed to send email") from exc

    analysis.emailed_to = recipient_list
    db.add(analysis)
    db.commit()

    return {"status": "queued"}
