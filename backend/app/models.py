from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Optional

from sqlalchemy import JSON, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    full_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    organization: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)

    documents: Mapped[List["Document"]] = relationship(back_populates="owner", cascade="all, delete-orphan")


class Document(Base):
    __tablename__ = "documents"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    owner_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    original_filename: Mapped[str] = mapped_column(String(512), nullable=False)
    stored_filename: Mapped[str] = mapped_column(String(512), nullable=False, unique=True)
    content_type: Mapped[str] = mapped_column(String(128), nullable=False)
    file_size: Mapped[int] = mapped_column(Integer, nullable=False)
    status: Mapped[str] = mapped_column(String(64), default="pending")
    rule_config: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict)
    metadata_notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    uploaded_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)

    owner: Mapped[User] = relationship(back_populates="documents")
    analyses: Mapped[List["AnalysisReport"]] = relationship(back_populates="document", cascade="all, delete-orphan")
    translations: Mapped[List["TranslationJob"]] = relationship(
        back_populates="document", cascade="all, delete-orphan"
    )


class AnalysisReport(Base):
    __tablename__ = "analysis_reports"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    document_id: Mapped[int] = mapped_column(ForeignKey("documents.id", ondelete="CASCADE"), nullable=False, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    summary: Mapped[str] = mapped_column(Text, nullable=False)
    highlights: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict)
    sections: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict)
    rule_config: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict)
    zip_path: Mapped[Optional[str]] = mapped_column(String(512), nullable=True)
    export_path: Mapped[Optional[str]] = mapped_column(String(512), nullable=True)
    emailed_to: Mapped[Optional[List[str]]] = mapped_column(JSON, default=list)

    document: Mapped[Document] = relationship(back_populates="analyses")


class TranslationJob(Base):
    __tablename__ = "translation_jobs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    document_id: Mapped[int] = mapped_column(ForeignKey("documents.id", ondelete="CASCADE"), nullable=False, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    status: Mapped[str] = mapped_column(String(64), default="pending")
    target_languages: Mapped[List[str]] = mapped_column(JSON, default=list)
    translations: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict)
    export_path: Mapped[Optional[str]] = mapped_column(String(512), nullable=True)

    document: Mapped[Document] = relationship(back_populates="translations")
