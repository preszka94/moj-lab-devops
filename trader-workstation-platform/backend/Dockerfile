# ==============================================================================
# BASE IMAGE LAYER
# ==============================================================================
# Migrated from python:3.11-slim to almalinux:9-minimal to simulate production.
# AlmaLinux 9 is 1:1 binary-compatible with Red Hat Enterprise Linux (RHEL),
# the exact OS standard deployed across tier-one banks like ING.
# The 'minimal' flavor strips out non-essential utilities, manuals, and bundles,
# forcing us to explicitly control every package entering our application boundary.
FROM almalinux:9-minimal

# ==============================================================================
# SYSTEM DEPENDENCIES & RUNTIME LAYER
# ==============================================================================
# Install the exact Python 3.11 runtime environment and pip package manager manually.
# microdnf is the lightweight package manager built into AlmaLinux minimal.
# -y flags 'yes' automatically to non-interactive prompts to keep the pipeline automated.
# The '&& \' chains commands to minimize the final layer count in the storage graph.
# microdnf clean all destroys transient metadata and cache files instantly, 
# preventing dead installer bytes from being permanently baked into the image layer.
RUN microdnf install -y python3.11 python3.11-pip && \
    microdnf clean all

# ==============================================================================
# FILESYSTEM CONFIGURATION
# ==============================================================================
# /app is the container-side working directory. App code lands at /app/app/...
# so the import path "app.main:app" (used by uvicorn below) resolves correctly.
# WORKDIR automatically initializes and builds this folder path if it does not exist.
WORKDIR /app

# ==============================================================================
# DEPENDENCY RESOLUTION & LAYER CACHING
# ==============================================================================
# Copy the Python dependencies manifest file into the current container directory (.)
COPY requirements.txt .

# Install Python deps before copying source so this layer caches across rebuilds.
# Touching main.py shouldn't trigger a full pip reinstall.
# We explicitly invoke pip3.11 to avoid relying on generic 'pip' system aliases.
# --no-cache-dir tells pip not to cache downloaded .whl files inside the container,
# saving critical disk space and maintaining a slim, audit-ready footprint.
RUN pip3.11 install --no-cache-dir -r requirements.txt

# ==============================================================================
# APPLICATION SOURCE LAYER
# ==============================================================================
# Copy the FastAPI source last, in its own layer.
# Placing the source code copy step at the absolute bottom preserves our cache.
# Now, editing a single line of Python code only invalidates this tiny final layer,
# allowing local development code modifications to compile and rebuild in milliseconds.
COPY app/ ./app/

# ==============================================================================
# NETWORKING METADATA
# ==============================================================================
# Document the port uvicorn listens on. docker-compose maps host:8000 to this.
# EXPOSE serves purely as configuration documentation for network proxies like nginx;
# it does not actually open firewall ports on the host system automatically.
EXPOSE 8000

# ==============================================================================
# RUNTIME OBSERVABILITY & HEALTH MONITORING
# ==============================================================================
# Liveness probe Docker uses to mark the container healthy/unhealthy.
# Uses urllib.request from the Python stdlib so we don't need a runtime
# dependency on `requests` (the previous version imported `requests` which
# wasn't in requirements.txt, so the probe always failed silently).
# Phase 4 will replace this with a proper /health vs /ready split in code.
# CHANGED: Switched execution string to 'python3.11' because AlmaLinux minimal 
# does not map an unversioned 'python' binary link out of the box.
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python3.11 -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health').read()" || exit 1

# ==============================================================================
# CONTAINER EXECUTION ENTRYPOINT
# ==============================================================================
# Start uvicorn as PID 1.
# --host 0.0.0.0 listens on all container interfaces so the host can reach it.
# --port 8000 matches EXPOSE above and the docker-compose port mapping.
# --workers 1 keeps things deterministic while we're learning.
# CHANGED: Wrapped execution via 'python3.11 -m uvicorn' to prevent command
# path resolution bugs, ensuring the engine calls the explicit versioned runtime module.
CMD ["python3.11", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "1"]