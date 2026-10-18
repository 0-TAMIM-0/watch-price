# Build stage
FROM python:3.14-slim AS builder

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt


# Runtime stage
FROM python:3.14-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    && rm -rf /var/lib/apt/lists/*

# Non-root user + writable uploads folder
RUN useradd -m app \
    && mkdir -p /app/uploads \
    && chown -R app:app /app

# Packages go to /usr/local (readable by any user)
COPY --from=builder /install /usr/local

COPY --chown=app:app . .

ENV PYTHONUNBUFFERED=1
ENV FLASK_APP=run.py

USER app

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=10s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:5000/health')" || exit 1

EXPOSE 5000

CMD ["sh", "-c", "gunicorn -b 0.0.0.0:5000 -w ${WEB_CONCURRENCY:-1} --threads ${GUNICORN_THREADS:-4} --timeout 30 run:app"]
