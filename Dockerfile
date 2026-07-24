# syntax=docker/dockerfile:1
# ACLIMATE v3 — Admin Dockerfile
# =============================================================================
# Stack: Flask + Gunicorn + PostgreSQL + Babel i18n
# Port: 3003 (configurable via PORT env var)
# =============================================================================

FROM python:3.11-slim

# ── Build-time environment ──────────────────────────────────────────────────
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

# ── System dependencies ─────────────────────────────────────────────────────
# git: required to install dependencies from git+https:// URLs
# gcc + python3-dev: required to compile psycopg2 (dependency of aclimate_v3_orm)
# libpq-dev: required for psycopg2 build
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        git \
        gcc \
        python3-dev \
        libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# ── Create non-root user ────────────────────────────────────────────────────
RUN useradd -l -u 10001 appuser

# ── Working directory ───────────────────────────────────────────────────────
WORKDIR /app

# ── Layer 1: Install Python dependencies (cacheable) ───────────────────────
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# ── Cleanup build-time system packages ──────────────────────────────────────
RUN apt-get remove -y git gcc python3-dev && \
    apt-get autoremove -y && \
    rm -rf /var/lib/apt/lists/*

# ── Layer 2: Copy application source code ──────────────────────────────────
COPY src/ ./src/
COPY conf_files/ ./conf_files/

# ── Compile translations (.po → .mo) ────────────────────────────────────────
RUN cd src && pybabel compile -d app/translations

# ── Runtime configuration ───────────────────────────────────────────────────
ENV PORT=3003

EXPOSE ${PORT}

# ── Health check ────────────────────────────────────────────────────────────
HEALTHCHECK --interval=30s --timeout=5s --start-period=45s --retries=5 \
  CMD python -c "import urllib.request, os; urllib.request.urlopen('http://127.0.0.1:' + os.environ.get('PORT', '3003') + '/health')" || exit 1

# ── Drop privileges ─────────────────────────────────────────────────────────
USER appuser

# ── Start command (Gunicorn) ────────────────────────────────────────────────
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:3003", \
     "--access-logfile", "-", \
     "--error-logfile", "-", \
     "--forwarded-allow-ips", "*", \
     "--pythonpath", "src", \
     "run:app"]
