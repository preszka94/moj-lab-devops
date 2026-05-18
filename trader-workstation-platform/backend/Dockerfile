# Temporary base for Phase 0/1. Will be replaced with almalinux:9-minimal in
# Phase 1.3 so the image matches the on-prem AlmaLinux VM we'll deploy to.
# python:3.11-slim is fast and small but hides the OS layer we want to learn.
FROM python:3.11-slim

# /app is the container-side working directory. App code lands at /app/app/...
# so the import path "app.main:app" (used by uvicorn below) resolves correctly.
WORKDIR /app

# Install Python deps before copying source so this layer caches across rebuilds.
# Touching main.py shouldn't trigger a full pip reinstall.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the FastAPI source last, in its own layer.
COPY app/ ./app/

# Document the port uvicorn listens on. docker-compose maps host:8000 to this.
EXPOSE 8000

# Liveness probe Docker uses to mark the container healthy/unhealthy.
# Uses urllib.request from the Python stdlib so we don't need a runtime
# dependency on `requests` (the previous version imported `requests` which
# wasn't in requirements.txt, so the probe always failed silently).
# Phase 4 will replace this with a proper /health vs /ready split in code.
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health').read()" || exit 1

# Start uvicorn as PID 1.
# --host 0.0.0.0 listens on all container interfaces so the host can reach it.
# --port 8000 matches EXPOSE above and the docker-compose port mapping.
# --workers 1 keeps things deterministic while we're learning.
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "1"]
