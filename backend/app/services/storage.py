import secrets
from pathlib import Path
from typing import Optional

from fastapi import UploadFile

from ..core.config import get_settings


settings = get_settings()


def _generate_filename(original_name: str) -> str:
    random_token = secrets.token_hex(8)
    sanitized = "".join(char for char in original_name if char.isalnum() or char in (".", "_", "-"))
    return f"{random_token}_{sanitized[:200]}"


async def save_upload_file(upload: UploadFile) -> Path:
    target_dir = settings.upload_dir
    target_dir.mkdir(parents=True, exist_ok=True)

    filename = _generate_filename(upload.filename or "document.pdf")
    file_path = target_dir / filename

    with file_path.open("wb") as buffer:
        while chunk := await upload.read(1024 * 1024):
            buffer.write(chunk)
    await upload.close()
    return file_path


def delete_file(path: Optional[Path]) -> None:
    if path and path.exists():
        path.unlink()
