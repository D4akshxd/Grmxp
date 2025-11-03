from __future__ import annotations

import logging
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List, Tuple

import pdfplumber

from ..schemas import RuleConfig, SectionInsight
from .summarizer import summarize_text


LOGGER = logging.getLogger(__name__)


SECTION_TITLES = {
    "technical_specifications": "Technical Specifications",
    "certificates": "Certificates",
    "atc_documents": "ATC Documents",
    "boq": "Bill of Quantities",
    "eligibility": "Eligibility Criteria",
    "important_dates": "Important Dates",
}


@dataclass
class SectionMatch:
    key: str
    sentences: List[str]
    keywords_found: List[str]


def _normalize_text(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def _extract_sentences(text: str) -> List[str]:
    text = _normalize_text(text)
    sentences = re.split(r"(?<=[.!?])\s+", text)
    return [sentence.strip() for sentence in sentences if sentence.strip()]


class PDFAnalyzer:
    def __init__(self, rule_config: RuleConfig):
        self.rule_config = rule_config

    def load_pdf_text(self, pdf_path: Path) -> str:
        LOGGER.info("Extracting text from %s", pdf_path)
        text_parts: List[str] = []
        with pdfplumber.open(str(pdf_path)) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text() or ""
                text_parts.append(page_text)
        combined = "\n".join(text_parts)
        return _normalize_text(combined)

    def _match_section(self, sentences: Iterable[str], section_key: str, keywords: Iterable[str]) -> SectionMatch:
        matched_sentences: List[str] = []
        keywords_found: List[str] = []

        keyword_patterns: List[Tuple[str, re.Pattern[str]]] = [
            (keyword, re.compile(rf"\b{re.escape(keyword)}\b", re.IGNORECASE)) for keyword in keywords
        ]

        for sentence in sentences:
            sentence_lower = sentence.lower()
            hits = [keyword for keyword, pattern in keyword_patterns if pattern.search(sentence_lower)]
            if hits:
                matched_sentences.append(sentence)
                keywords_found.extend(hits)

        unique_keywords = sorted(set(keywords_found), key=str.lower)
        return SectionMatch(key=section_key, sentences=matched_sentences, keywords_found=unique_keywords)

    def analyze(self, pdf_path: Path) -> Dict[str, SectionInsight]:
        full_text = self.load_pdf_text(pdf_path)
        sentences = _extract_sentences(full_text)
        if not sentences:
            return {}

        section_results: Dict[str, SectionInsight] = {}
        total_sentences = len(sentences)

        for section_key, config in self.rule_config.model_dump().items():
            if not config.get("enabled", True):
                continue
            keywords = config.get("keywords", [])
            match = self._match_section(sentences, section_key, keywords)
            if not match.sentences:
                continue

            summary = summarize_text(" ".join(match.sentences), max_sentences=4)
            keyword_coverage = len(set(match.keywords_found)) / max(1, len(keywords)) if keywords else 0
            sentence_ratio = len(match.sentences) / max(1, total_sentences)
            confidence = keyword_coverage if keywords else sentence_ratio
            min_confidence = config.get("min_confidence", 0.2)
            if confidence < min_confidence:
                continue

            importance = min(1.0, max(sentence_ratio, confidence))
            section_results[section_key] = SectionInsight(
                title=SECTION_TITLES.get(section_key, section_key.replace("_", " ").title()),
                summary=summary,
                importance_score=round(importance, 3),
                keywords_found=match.keywords_found,
            )

        return section_results

    def summarize(self, pdf_path: Path) -> str:
        text = self.load_pdf_text(pdf_path)
        return summarize_text(text, max_sentences=8)


def analyze_pdf(pdf_path: Path, rule_config: RuleConfig) -> Tuple[str, Dict[str, SectionInsight]]:
    analyzer = PDFAnalyzer(rule_config)
    summary = analyzer.summarize(pdf_path)
    sections = analyzer.analyze(pdf_path)
    return summary, sections
