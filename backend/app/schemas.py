from __future__ import annotations

from datetime import datetime
from typing import Dict, List, Optional

from pydantic import BaseModel, EmailStr, Field


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenPayload(BaseModel):
    sub: str
    exp: int


class UserBase(BaseModel):
    email: EmailStr
    full_name: Optional[str] = None
    organization: Optional[str] = None


class UserCreate(UserBase):
    password: str = Field(min_length=8)


class UserRead(UserBase):
    id: int
    created_at: datetime

    class Config:
        orm_mode = True


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class RuleSectionConfig(BaseModel):
    enabled: bool = True
    keywords: List[str] = Field(default_factory=list)
    min_confidence: float = Field(default=0.2, ge=0, le=1)


class RuleConfig(BaseModel):
    technical_specifications: RuleSectionConfig = RuleSectionConfig(keywords=["specification", "technical", "compliance"])
    certificates: RuleSectionConfig = RuleSectionConfig(keywords=["certificate", "certification", "iso"])
    atc_documents: RuleSectionConfig = RuleSectionConfig(keywords=["ATC", "terms", "conditions", "amendment"])
    boq: RuleSectionConfig = RuleSectionConfig(keywords=["bill of quantity", "boq", "pricing", "rate"])
    eligibility: RuleSectionConfig = RuleSectionConfig(keywords=["eligibility", "experience", "turnover"])
    important_dates: RuleSectionConfig = RuleSectionConfig(keywords=["bid end", "submission", "opening"])


class AnalysisMetadata(BaseModel):
    status: str
    uploaded_at: datetime
    rule_config: RuleConfig


class SectionInsight(BaseModel):
    title: str
    summary: str
    importance_score: float
    keywords_found: List[str]


class AnalysisResult(BaseModel):
    document_id: int
    analysis_id: int
    summary: str
    highlights: Dict[str, str]
    sections: Dict[str, SectionInsight]
    created_at: datetime


class DocumentRead(BaseModel):
    id: int
    original_filename: str
    uploaded_at: datetime
    status: str
    latest_analysis: Optional[AnalysisResult]


class DocumentListResponse(BaseModel):
    items: List[DocumentRead]
    total: int


class EmailDispatchRequest(BaseModel):
    recipients: List[EmailStr]
    subject: str = "GeM Bid Summary"
    message: Optional[str] = None


class AnalysisCreateResponse(BaseModel):
    document_id: int
    analysis_id: int
    status: str
    summary_preview: str


class ExportResponse(BaseModel):
    download_url: str
