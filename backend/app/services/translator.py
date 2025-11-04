from __future__ import annotations

import logging
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Sequence

import pdfplumber
from deep_translator import LibreTranslateTranslator

from ..core.config import get_settings


LOGGER = logging.getLogger(__name__)


SUPPORTED_LANGUAGES: List[Dict[str, str]] = [
    {"code": "ar", "name": "Arabic"},
    {"code": "bn", "name": "Bengali"},
    {"code": "de", "name": "German"},
    {"code": "en", "name": "English"},
    {"code": "es", "name": "Spanish"},
    {"code": "fr", "name": "French"},
    {"code": "gu", "name": "Gujarati"},
    {"code": "hi", "name": "Hindi"},
    {"code": "it", "name": "Italian"},
    {"code": "ja", "name": "Japanese"},
    {"code": "kn", "name": "Kannada"},
    {"code": "ko", "name": "Korean"},
    {"code": "ml", "name": "Malayalam"},
    {"code": "mr", "name": "Marathi"},
    {"code": "nl", "name": "Dutch"},
    {"code": "pa", "name": "Punjabi"},
    {"code": "pl", "name": "Polish"},
    {"code": "pt", "name": "Portuguese"},
    {"code": "ru", "name": "Russian"},
    {"code": "ta", "name": "Tamil"},
    {"code": "te", "name": "Telugu"},
    {"code": "th", "name": "Thai"},
    {"code": "tr", "name": "Turkish"},
    {"code": "uk", "name": "Ukrainian"},
    {"code": "ur", "name": "Urdu"},
    {"code": "vi", "name": "Vietnamese"},
    {"code": "zh", "name": "Chinese (Simplified)"},
]

LANGUAGE_LOOKUP: Dict[str, str] = {entry["code"]: entry["name"] for entry in SUPPORTED_LANGUAGES}


class TranslationProviderError(RuntimeError):
    """Raised when the configured translation provider fails."""


@dataclass
class PageExtraction:
    page_number: int
    original_text: str


@dataclass
class TranslationPageResult:
    page_number: int
    original_text: str
    translated_text: str

    def to_dict(self) -> Dict[str, str | int]:
        return {
            "page_number": self.page_number,
            "original_text": self.original_text,
            "translated_text": self.translated_text,
        }


@dataclass
class TranslationLanguageResult:
    language_code: str
    language_name: str
    pages: List[TranslationPageResult]

    @property
    def full_text(self) -> str:
        return "\n\n".join(page.translated_text for page in self.pages if page.translated_text)

    @property
    def word_count(self) -> int:
        return sum(len(page.translated_text.split()) for page in self.pages if page.translated_text)

    @property
    def character_count(self) -> int:
        return sum(len(page.translated_text) for page in self.pages if page.translated_text)

    def to_dict(self) -> Dict[str, object]:
        return {
            "language_code": self.language_code,
            "language_name": self.language_name,
            "pages": [page.to_dict() for page in self.pages],
            "full_text": self.full_text,
            "word_count": self.word_count,
            "character_count": self.character_count,
        }


def _normalize_for_chunking(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def _chunk_text(text: str, *, chunk_size: int, overlap: int) -> List[str]:
    normalized = _normalize_for_chunking(text)
    if not normalized:
        return []

    length = len(normalized)
    if length <= chunk_size:
        return [normalized]

    chunks: List[str] = []
    start = 0
    while start < length:
        end = min(length, start + chunk_size)
        chunk = normalized[start:end].strip()
        if chunk:
            chunks.append(chunk)
        if end >= length:
            break
        start = max(0, end - overlap)
    return chunks


class LibreTranslateProvider:
    def __init__(self, *, base_url: str, api_key: str | None):
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key

    def translate(self, segments: Sequence[str], target_language: str) -> List[str]:
        if not segments:
            return []
        try:
            translator = LibreTranslateTranslator(
                source="auto",
                target=target_language,
                url=self.base_url,
                api_key=self.api_key,
            )
            if len(segments) == 1:
                translated = translator.translate(segments[0])
                return [translated]
            return list(translator.translate_batch(list(segments)))
        except Exception as exc:  # pragma: no cover - depends on external HTTP service
            LOGGER.exception("Translation provider request failed: target=%s", target_language)
            raise TranslationProviderError(str(exc)) from exc


class PDFTranslationService:
    def __init__(self) -> None:
        self.settings = get_settings()
        provider_key = self.settings.translation_provider.lower()
        if provider_key != "libretranslate":
            raise ValueError(f"Unsupported translation provider: {provider_key}")
        self.provider = LibreTranslateProvider(
            base_url=self.settings.libretranslate_url,
            api_key=self.settings.libretranslate_api_key,
        )

    @staticmethod
    def list_supported_languages() -> List[Dict[str, str]]:
        return SUPPORTED_LANGUAGES

    @staticmethod
    def get_language_name(code: str) -> str | None:
        return LANGUAGE_LOOKUP.get(code.lower())

    def _extract_pages(self, pdf_path: Path) -> List[PageExtraction]:
        pages: List[PageExtraction] = []
        with pdfplumber.open(str(pdf_path)) as pdf:
            for index, page in enumerate(pdf.pages, start=1):
                content = page.extract_text() or ""
                cleaned = content.strip()
                if not cleaned:
                    continue
                pages.append(PageExtraction(page_number=index, original_text=cleaned))
        return pages

    def translate_pdf(self, pdf_path: Path, language_codes: Sequence[str]) -> List[TranslationLanguageResult]:
        if not language_codes:
            return []

        pages = self._extract_pages(pdf_path)
        if not pages:
            LOGGER.info("No extractable text found in PDF: %s", pdf_path)
            return []

        chunk_size = max(500, self.settings.translation_chunk_size)
        overlap = max(0, min(self.settings.translation_chunk_overlap, chunk_size // 2))

        results: List[TranslationLanguageResult] = []
        for code in language_codes:
            language_code = code.lower()
            language_name = self.get_language_name(language_code)
            if not language_name:
                raise ValueError(f"Unsupported language code: {code}")

            translated_pages: List[TranslationPageResult] = []
            for page in pages:
                segments = _chunk_text(page.original_text, chunk_size=chunk_size, overlap=overlap)
                translated_segments = self.provider.translate(segments, language_code)
                translated_text = " ".join(translated_segments).strip()
                translated_pages.append(
                    TranslationPageResult(
                        page_number=page.page_number,
                        original_text=page.original_text,
                        translated_text=translated_text,
                    )
                )

            results.append(
                TranslationLanguageResult(
                    language_code=language_code,
                    language_name=language_name,
                    pages=translated_pages,
                )
            )

        return results


def translate_pdf(pdf_path: Path, language_codes: Sequence[str]) -> List[TranslationLanguageResult]:
    service = PDFTranslationService()
    return service.translate_pdf(pdf_path, language_codes)
