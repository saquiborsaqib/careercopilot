"""Optional OCR support for scanned/image-based PDFs.

OCR is a secondary capability: pypdf/python-docx text extraction is always
tried first (see pdf_parser). This module only activates if pytesseract,
Pillow and a Tesseract binary are actually available; otherwise it no-ops so
the resume pipeline keeps working without OCR installed.
"""

from __future__ import annotations

import logging
from pathlib import Path

logger = logging.getLogger(__name__)


def ocr_available() -> bool:
    try:
        import pytesseract  # noqa: F401
        from pdf2image import convert_from_path  # noqa: F401
    except ImportError:
        return False
    return True


def ocr_extract_text(file_path: str | Path) -> str:
    if not ocr_available():
        return ""
    try:
        import pytesseract
        from pdf2image import convert_from_path

        images = convert_from_path(str(file_path))
        text_parts = [pytesseract.image_to_string(image) for image in images]
        return "\n".join(text_parts).strip()
    except Exception:
        logger.warning("OCR extraction failed; continuing without OCR text", exc_info=True)
        return ""
