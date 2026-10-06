
# Project Journal — trader-workstation-platform

A concise running log of what we built, key commands, gotchas, and items to revisit.

---

## 2026-05-18 — Phase 0: runnable backend in Docker (Phase 1.1–1.2 cleanup)

**Current state (on disk)**

- `backend/app/main.py` — FastAPI app with `GET /` and `GET /health` endpoints, using Pydantic response models.
- `backend/Dockerfile` — currently `FROM python:3.11-slim` (temporary). Phase 1.3 will switch this to `almalinux:9-minimal` to match the on-prem AlmaLinux VM.
- `backend/requirements.txt` — pinned `fastapi`, `uvicorn`, `pydantic`, and `pydantic-settings` (listed but not yet used).
- `docker-compose.yml` — single `backend` service exposing port 8000 and defining `trader-network`.
- Empty placeholder dirs (contain `.gitkeep`): `frontend/`, `database/`, `nginx/`, `ansible/`, `ci/`, `docs/`.

**What we verified**

- `docker compose up --build` completes the build and starts the container.
- `curl http://localhost:8000/health` returns `200 OK` with the expected JSON.

**Cleanups performed (Phase 1.1–1.2)**

- Removed a stray empty `app/` directory accidentally created at the project root.
- Removed the obsolete `version: '3.9'` key from `docker-compose.yml` to stop deprecation warnings.
- Fixed a broken `HEALTHCHECK` in `backend/Dockerfile`: it relied on `requests` (not in `requirements.txt`) and crashed on each probe. Rewrote the probe with `urllib.request` as a temporary fix; Phase 4 will add proper `/health` (liveness) and `/ready` (readiness) endpoints in the app.
- Rewrote `README.md` and `CLAUDE.md` to reflect the on-prem plan: VMware Fusion + AlmaLinux 9, Oracle Database Free, Ansible-driven deployment, Azure DevOps with a self-hosted agent, and Citrix-via-RDP for the trader workstation simulation.

**Key commands**

- `docker compose up --build` — build and run the container in the foreground.
- `docker compose down` — stop and remove containers and networks.
- `curl http://localhost:8000/health` — verify the API.

**Gotchas / lessons learned**

- Build context matters: the `COPY` paths in a Dockerfile are relative to the build context (not the Dockerfile location). The initial build failed because `context: .` did not include `backend/requirements.txt`; switching to `context: ./backend` fixed it.
- `pip install -r requirements.txt` runs inside the container during the image build — running it on macOS during the Docker build troubleshooting is unnecessary and can be confusing.
- Health checks can appear to succeed while actually failing (Docker retries). Ensure the probe uses only installed/available modules and test it locally.
- Keep Docker layer caching in mind: copy `requirements.txt` and run dependency install before copying source files to avoid reinstalling dependencies on every code change.

**Revisit later**

- Phase 1.3: migrate to `almalinux:9-minimal` and install Python 3.11; compare image size and rebuild time.
- Phase 4.2: replace Dockerfile `HEALTHCHECK` with app-level `/health` (liveness) and `/ready` (readiness/DB checks).
- Phase 2: start using `pydantic-settings` where appropriate.
- Phase 3: decide whether `frontend/` will be served by nginx or removed.
- Decide whether to track `.vscode/` for shared editor settings; add a `LICENSE` before making the repo public.

---

## 2026-06-22 — Repo hygiene: sparse-checkout and SafeDoc cleanup

**What we did**

- Removed duplicate SafeDoc files and an orphan submodule; hardened `.gitignore`.
- Used `git sparse-checkout` to scope the working tree to `trader-workstation-platform/` so unrelated files in the monorepo don't clutter development.
- Stashed an uncommitted edit in `web_app/app.py` (it contained hardcoded Oracle credentials) before changing the sparse checkout.
- Committed: `chore: remove SafeDoc duplicates, drop orphan submodule, harden gitignore`.

**Key commands**

- `git sparse-checkout init --cone`
- `git sparse-checkout set trader-workstation-platform`
- `git stash` / `git stash pop`

**Gotchas**

- `git sparse-checkout` will refuse to proceed if it would remove files with uncommitted changes; stash first.

**Revisit later**

- Decide whether to split SafeDoc and `trader-workstation-platform` into separate repos or keep the monorepo with sparse-checkout.
- Remove hardcoded Oracle credentials from `web_app/app.py` before sharing.

---

## 2026-06-22 — Phase 8 warm-up: Azure DevOps and smoke-test pipeline

**What we built**

- Created Azure DevOps organization `piotr-trader-lab` and project `trader-workstation-platform`.
- Added `azure-pipelines.yml` with a minimal smoke-test job, connected via the Azure Pipelines OAuth app.
- Diagnosed and fixed a YAML parse error; committed `ci: add smoke-test pipeline for Azure DevOps wiring`.

**Why self-hosted agents matter**

- Microsoft-hosted agents can't reach on-prem VMs behind private networks. A self-hosted agent runs on the VM and polls the server, allowing deployments into private networks without inbound firewall changes.

**Key commands**

- `git diff --staged`
- `git pull`
- `sed -n '12p' azure-pipelines.yml | cut -c39` (used to locate a single-character YAML parse issue)

**Gotchas**

- YAML scalars containing colons should be quoted. For example, `echo 'Pipeline smoke check: OK'` avoids YAML parsing pitfalls.

**Revisit later**

- Phase 8: install the self-hosted agent on the AlmaLinux VM and add a deployment job (Ansible or `docker compose pull && up`).
- Add a `docker build` job to the pipeline to catch Dockerfile issues early.

---

## 2026-06-22 — Phase 1.3: AlmaLinux 9 Dockerfile migration

**What we built**

- Replaced `FROM python:3.11-slim` with `FROM almalinux:9-minimal` in `backend/Dockerfile` and added `microdnf` steps to install Python 3.11.
- Verified the container builds and reports healthy; committed `feat: migrate backend image to AlmaLinux 9 minimal base`.

**Why this matters**

- Matching the container base to the on-prem OS reduces runtime surprises (package manager, glibc, filesystem layout).

**Key commands**

- `docker compose build`
- `docker compose up`
- `curl http://localhost:8000/health`

**Gotchas**

- Order Dockerfile steps to maximise layer cache re-use: copy `requirements.txt` and install dependencies before copying application source.

**Revisit later**

- Compare image size and rebuild time between `python:3.11-slim` and `almalinux:9-minimal + python3.11`.
- Phase 4.2: move health/readiness checks into the app.

---

## 2026-06-22 — Phase 1.5: GET /positions endpoint

**What we built**

- Added a `Position` Pydantic model (`symbol`, `quantity`, `avg_price`, `current_price`).
- Implemented `GET /positions` returning four mock positions (INGA.AS, ASML, DBR 0% 2032, EURUSD).
- Fixed a bug where `datetime()` was used instead of `datetime.now()`.
- Committed: `feat: add GET /positions endpoint with mock data`.

**Key commands**

- `docker compose up -d --build` — rebuild and run in detached mode.
- `curl http://localhost:8000/positions` — validate the endpoint.

**Gotchas**

- `docker compose up` without `--build` does not pick up source changes; use `--build` when updating code.
- Use `datetime.now()` for current timestamps (calling `datetime()` without args raises a `TypeError`).

**Revisit later**

- Phase 2: replace mocks with a real `SELECT` from Oracle Database Free.
- Add an `unrealised_pnl` computed field to `Position` (`(current_price - avg_price) * quantity`).
