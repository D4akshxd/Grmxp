from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Iterable
from zipfile import ZIP_DEFLATED, ZipFile

from ..core.config import get_settings
from .translator import TranslationLanguageResult


settings = get_settings()


def _ensure_translation_export_dir() -> Path:
    base_dir = settings.export_dir / "translations"
    base_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")
    export_dir = base_dir / timestamp
    export_dir.mkdir(parents=True, exist_ok=True)
    return export_dir


def _language_markdown(document_name: str, translation: TranslationLanguageResult) -> str:
    lines = [
        f"# Translation - {document_name}",
        f"Language: {translation.language_name} ({translation.language_code})",
        "",
    ]
    for page in translation.pages:
        lines.extend(
            [
                f"## Page {page.page_number}",
                page.translated_text or "_No translatable text extracted for this page._",
                "",
            ]
        )
    return "\n".join(lines)


def create_translation_bundle(
    *, document_name: str, translations: Iterable[TranslationLanguageResult]
) -> Path:
    export_dir = _ensure_translation_export_dir()
    bundle_path = export_dir / f"{Path(document_name).stem}_translations.zip"

    translations_list = list(translations)

    with ZipFile(bundle_path, mode="w", compression=ZIP_DEFLATED) as archive:
        manifest = []
        for translation in translations_list:
            filename = f"{Path(document_name).stem}_{translation.language_code}.md"
            archive.writestr(filename, _language_markdown(document_name, translation))
            manifest.append(
                {
                    "language_code": translation.language_code,
                    "language_name": translation.language_name,
                    "filename": filename,
                    "word_count": translation.word_count,
                    "character_count": translation.character_count,
                }
            )

        archive.writestr(
            "manifest.json",
            json.dumps(
                {
                    "document_name": document_name,
                    "generated_at": datetime.utcnow().isoformat() + "Z",
                    "translations": manifest,
                },
                indent=2,
            ),
        )

    return bundle_path
