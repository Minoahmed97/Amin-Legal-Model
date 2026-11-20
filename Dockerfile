FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

RUN apt-get update && apt-get install -y --no-install-recommends \
    tesseract-ocr tesseract-ocr-ara tesseract-ocr-eng \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY pyproject.toml README.md ./
COPY src ./src
COPY configs ./configs
RUN pip install --no-cache-dir ".[documents,ocr]"

RUN useradd --create-home --uid 10001 amin \
    && mkdir -p /app/data \
    && chown -R amin:amin /app
USER amin

EXPOSE 8000
CMD ["uvicorn", "amin_legal_model.api:app", "--host", "0.0.0.0", "--port", "8000"]
