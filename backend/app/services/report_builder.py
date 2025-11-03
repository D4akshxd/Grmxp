from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional
from zipfile import ZipFile, ZIP_DEFLATED

from jinja2 import Environment, FileSystemLoader, select_autoescape

from ..core.config import get_settings
from ..schemas import SectionInsight


settings = get_settings()


env = Environment(
    loader=FileSystemLoader(settings.template_dir),
    autoescape=select_autoescape(["html", "xml"]),
)


@dataclass
class ReportContext:
    document_name: str
    generated_at: datetime
    summary: str
    highlights: Dict[str, str]
    sections: Dict[str, SectionInsight]
    rule_config: Dict[str, dict]
    owner_email: str


def _ensure_export_dir() -> Path:
    settings.export_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")
    export_folder = settings.export_dir / timestamp
    export_folder.mkdir(parents=True, exist_ok=True)
    return export_folder


def render_html_report(context: ReportContext) -> str:
    template = env.get_template("report.html")
    return template.render(
        document_name=context.document_name,
        generated_at=context.generated_at,
        summary=context.summary,
        highlights=context.highlights,
        sections=context.sections,
        rule_config=context.rule_config,
        owner_email=context.owner_email,
    )


def build_markdown_report(context: ReportContext) -> str:
    lines = [
        f"# GeM Bid Summary - {context.document_name}",
        "",
        f"Generated at: {context.generated_at.isoformat()} UTC",
        f"Prepared for: {context.owner_email}",
        "",
        "## Executive Summary",
        context.summary,
        "",
        "## Highlights",
    ]
    if context.highlights:
        for key, value in context.highlights.items():
            lines.append(f"- **{key.replace('_', ' ').title()}**: {value}")
    else:
        lines.append("- No highlights identified.")

    for section_key, section in context.sections.items():
        lines.extend([
            "",
            f"## {section.title}",
            section.summary or "No content detected.",
            "",
            f"**Importance score:** {section.importance_score}",
            f"**Keywords found:** {', '.join(section.keywords_found) if section.keywords_found else 'None'}",
        ])

    return "\n".join(lines)


def generate_report_assets(
    *,
    document_name: str,
    summary: str,
    highlights: Dict[str, str],
    sections: Dict[str, SectionInsight],
    rule_config: Dict[str, dict],
    owner_email: str,
) -> Dict[str, str]:
    context = ReportContext(
        document_name=document_name,
        generated_at=datetime.utcnow(),
        summary=summary,
        highlights=highlights,
        sections=sections,
        rule_config=rule_config,
        owner_email=owner_email,
    )

    html_content = render_html_report(context)
    markdown_content = build_markdown_report(context)
    json_payload = json.dumps(
        {
            "document_name": context.document_name,
            "generated_at": context.generated_at.isoformat() + "Z",
            "summary": context.summary,
            "highlights": context.highlights,
            "sections": {key: section.model_dump() for key, section in sections.items()},
            "rule_config": rule_config,
            "owner_email": context.owner_email,
        },
        indent=2,
    )

    return {
        "report.html": html_content,
        "report.md": markdown_content,
        "report.json": json_payload,
    }


def create_export_bundle(
    *,
    document_name: str,
    summary: str,
    highlights: Dict[str, str],
    sections: Dict[str, SectionInsight],
    rule_config: Dict[str, dict],
    owner_email: str,
) -> Path:
    export_dir = _ensure_export_dir()
    bundle_name = f"{Path(document_name).stem}_analysis.zip"
    bundle_path = export_dir / bundle_name

    assets = generate_report_assets(
        document_name=document_name,
        summary=summary,
        highlights=highlights,
        sections=sections,
        rule_config=rule_config,
        owner_email=owner_email,
    )

    with ZipFile(bundle_path, mode="w", compression=ZIP_DEFLATED) as archive:
        for filename, content in assets.items():
            archive.writestr(filename, content)

    return bundle_path
