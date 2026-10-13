from pathlib import Path
from uuid import uuid4
import os

from fastapi import HTTPException, UploadFile, status

UPLOAD_DIR = Path("uploads/tickets").resolve()

MAX_FILE_SIZE = 5 * 1024 * 1024
MAX_FILES = 5

ALLOWED_TYPES = {
    "image/jpeg": ".jpg",
    "image/png": ".png",
    "application/pdf": ".pdf",
}


async def save_attachment(file: UploadFile) -> dict:
    if file.content_type not in ALLOWED_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only JPG, PNG and PDF files are allowed",
        )

    stored_filename = f"{uuid4().hex}{ALLOWED_TYPES[file.content_type]}"

    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

    destination = UPLOAD_DIR / stored_filename
    total_size = 0

    try:
        with destination.open("wb") as output:
            while chunk := await file.read(1024 * 1024):
                total_size += len(chunk)

                if total_size > MAX_FILE_SIZE:
                    raise HTTPException(
                        status_code=status.HTTP_413_CONTENT_TOO_LARGE,
                        detail="File exceeds the 5 MB limit",
                    )

                output.write(chunk)

        if total_size == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Empty files are not allowed",
            )

        return {
            "original_filename": Path(file.filename or "attachment").name[:255],
            "stored_filename": stored_filename,
            "file_path": str(destination),
            "content_type": file.content_type,
            "file_size": total_size,
        }

    except Exception:
        destination.unlink(missing_ok=True)
        raise

    finally:
        await file.close()
