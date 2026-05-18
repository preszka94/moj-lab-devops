# Project Journal — trader-workstation-platform

A running log of what we built, key commands, gotchas, and things to revisit.
Short and honest, not promotional.

---

## 2026-05-18 — Phase 0: runnable backend in Docker (Phase 1.1–1.2 cleanup)

**What's actually on disk now (honest)**

- `backend/app/main.py` — FastAPI app with two endpoints: `GET /` and
  `GET /health`, both with pydantic response models. Real and runnable.
- `backend/Dockerfile` — builds on `python:3.11-slim`. **Temporary base** —
  will be replaced with `almalinux:9-minimal` in Phase 1.3 so the image
  matches the on-prem AlmaLinux VM we'll deploy to.
- `backend/requirements.txt` — pinned `fastapi`, `uvicorn`, `pydantic`,
  `pydantic-settings` (last one installed but not yet used).
- `docker-compose.yml` — one service (`backend`), exposes port 8000, defines
  `trader-network`.
- Empty placeholder dirs (with `.gitkeep`): `frontend/`, `database/`,
  `nginx/`, `ansible/`, `ci/`, `docs/`.

**What we verified works**

- `docker-compose up --build` completes the 5-step build and starts the
  container.
- `curl http://localhost:8000/health` returns `200 OK` with the expected
  JSON body.

**Cleanups done today (Phase 1.1 + 1.2 from the Notion roadmap)**

- Deleted stray empty `app/` directory at the project root (left over from a
  debugging detour where we ran `mkdir app` while the docker-compose build
  context was wrong).
- Removed the obsolete `version: '3.9'` key from `docker-compose.yml` — it
  was emitting a deprecation warning on every build.
- Fixed the silently-broken `HEALTHCHECK` in `backend/Dockerfile`: it was
  using `import requests`, but `requests` isn't in `requirements.txt`. The
  probe was failing on every run, just quietly. Replaced with stdlib
  `urllib.request` so the probe actually works until we replace it in
  Phase 4 with a proper `/health` vs `/ready` split.
- Rewrote `README.md` and `CLAUDE.md` to match the on-prem plan from the
  Notion note. Previous versions still said "deploy to Azure" and
  "PostgreSQL by default." Now both reflect:
    - on-prem only (VMware Fusion + AlmaLinux 9, no public cloud)
    - Oracle Database Free
    - Ansible-driven deployment to the VM fleet
    - Azure DevOps Pipelines with a self-hosted agent for CI/CD
    - Citrix-via-RDP for the trader workstation simulation

**Key commands run**

- `docker-compose up --build` — builds the image from the Dockerfile and
  starts the container in the foreground.
- `docker-compose down` — stops and removes the container and network.
- `curl http://localhost:8000/health` — verifies the API is responding.

**Gotchas**

- The first build failed with `requirements.txt: not found` because the
  compose build `context: .` (project root) didn't match where `requirements.txt`
  actually lives (`backend/requirements.txt`). Fixed by setting
  `context: ./backend` and `dockerfile: Dockerfile`. Lesson: the COPY paths
  in a Dockerfile are always relative to the build context, not to the
  Dockerfile's own location.
- Running `pip install -r requirements.txt` in my Mac shell while
  troubleshooting the Docker build was a category error — pip lives inside
  the container, not on the host. I don't have system pip and don't need it
  for this project.
- The `HEALTHCHECK` was a textbook silent failure: container reported
  "healthy" sometimes because Docker re-tries, but every probe was actually
  crashing with `ModuleNotFoundError`. Worth remembering — health checks
  that "work" can still be broken.

**Revisit later**

- Phase 1.3: replace `python:3.11-slim` with `almalinux:9-minimal` and
  install Python 3.11 manually. Compare image size and rebuild time.
- Phase 4.2: replace the Dockerfile-level `HEALTHCHECK` with a proper
  `/health` (liveness) and `/ready` (readiness, checks Oracle) split in
  the FastAPI app itself.
- Phase 2: actually use `pydantic-settings` — it's in `requirements.txt`
  doing nothing right now.
- Phase 3: figure out whether `frontend/` becomes the static page served
  by nginx, or gets deleted entirely. Currently empty placeholder.
- Decide whether `.vscode/` should be tracked for shared editor settings.
- Add a `LICENSE` file before the repo ever goes public.
