from pathlib import Path

from pypdf import PdfReader

from backend.processing.ocr import ocr_extract_text


def extract_text_from_pdf(file_path: str | Path) -> str:
    """Extract text from a PDF. Falls back to OCR for scanned/image-only pages."""
    reader = PdfReader(str(file_path))
    pages_text = []
    for page in reader.pages:
        pages_text.append(page.extract_text() or "")
    text = "\n".join(pages_text).strip()

    if len(text) < 30:
        ocr_text = ocr_extract_text(file_path)
        if ocr_text:
            return ocr_text

    return text
