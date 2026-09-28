FROM python:3.12-slim

WORKDIR /app

# System deps: none required for the core (non-OCR) install. If you build
# with requirements-ai-extra.txt for OCR, also install tesseract-ocr and
# poppler-utils here (see README "Optional AI extras").
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY backend ./backend

# Configuration is supplied via real environment variables (see docker-compose.yml),
# not a .env file -- pydantic-settings falls back to env vars when .env is absent.
ENV UPLOADS_DIR=/app/uploads
RUN mkdir -p /app/uploads

EXPOSE 8000

CMD ["sh", "-c", "python -m backend.database.init_db && python -m backend.seed.seed_data && uvicorn backend.main:app --host 0.0.0.0 --port 8000"]
