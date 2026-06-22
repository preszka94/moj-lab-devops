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
- AlmaLinux migration + the layer-caching
- the docker compose up vs up --build


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

---

## 2026-06-22 — Repo hygiene: sparse-checkout and SafeDoc cleanup

**What we did**

- Removed SafeDoc duplicate files and an orphan submodule left in the root; hardened `.gitignore`.
- Used `git sparse-checkout` to scope the working tree to just the `trader-workstation-platform/` sub-tree, so unrelated files in the monorepo don't clutter day-to-day work.
- Stashed an uncommitted edit in `web_app/app.py` (which contained hardcoded Oracle credentials) before applying sparse-checkout.
- Committed: `chore: remove SafeDoc duplicates, drop orphan submodule, harden gitignore`.

**Key commands**

- `git sparse-checkout init --cone` — switches sparse-checkout to cone mode, which operates on directory prefixes rather than arbitrary path patterns; faster and simpler to reason about.
- `git sparse-checkout set trader-workstation-platform` — tells Git to only materialise that directory in the working tree; everything else is still in the repo, just not checked out.
- `git stash` / `git stash pop` — save and restore uncommitted changes before a context switch that would otherwise conflict.

**Gotchas**

Sparse-checkout refuses to apply when there are uncommitted changes in paths it's about to remove from the working tree. Had to `git stash` the `web_app/app.py` edit first or the command errored out.

**Revisit later**

- Decide whether to fully split SafeDoc and trader-workstation-platform into separate repos or keep the monorepo with sparse-checkout scoping. Deferred to a later session.
- `web_app/app.py` contains hardcoded Oracle credentials (spotted during the stash). Strip those before the file ever reaches a shared or public branch.

---

## 2026-06-22 — Phase 8 warm-up: Azure DevOps and smoke-test pipeline

**What we built**

- Created Azure DevOps organisation `piotr-trader-lab` and project `trader-workstation-platform`.
- Wrote `azure-pipelines.yml` with a minimal smoke-test job (`ubuntu-latest`, `echo` steps) triggered by push to `main`.
- Connected the pipeline to GitHub via the Azure Pipelines OAuth app install.
- Diagnosed and fixed a YAML parse error in the pipeline file.
- Committed: `ci: add smoke-test pipeline for Azure DevOps wiring`.

**Why self-hosted agents matter (the architecture)**

A Microsoft-hosted agent runs in the Azure cloud and can't reach an on-prem target because the AlmaLinux VM has no inbound port open to the internet. A self-hosted agent installed on the VM polls outward over HTTPS — it initiates the connection, so no inbound firewall rule is ever needed. This is the standard pattern at banks where CI/CD lives in SaaS but the deployment target is inside a private network. Every pipeline job the server queues gets picked up by the agent, not pushed to it.

**Key commands**

- `git diff --staged` — shows exactly what will go into the next commit; used to verify the pipeline YAML before pushing.
- `git pull` — sync local `main` with origin before pushing, to avoid a non-fast-forward rejection.
- `sed -n '12p' azure-pipelines.yml | cut -c39` — print the single character at column 39 of line 12; used to pinpoint the exact character tripping the YAML parser.

**Gotchas**

YAML parse error: the script line `echo "Pipeline smoke check: OK"` — the colon after `check` was read by the YAML parser as the start of a second mapping key, breaking the job. Diagnosed by counting characters with `sed -n '12p' | cut -c39` to find the exact offending position. Fixed by wrapping the value in single quotes: `echo 'Pipeline smoke check: OK'`. Rule: any unquoted colon inside a YAML scalar can be misread as a key separator — when in doubt, quote the whole string.

Pushing to `main` auto-triggered the pipeline via the `trigger: - main` block — no manual run needed. That's the intended behaviour, but was surprising the first time.

**Revisit later**

- Phase 8 proper: install the self-hosted agent on the AlmaLinux VM and add a real deployment job (Ansible or `docker compose pull && up`).
- Add a `docker build` job before the smoke test so the pipeline catches broken Dockerfiles before they reach the VM.

---

## 2026-06-22 — Phase 1.3: AlmaLinux 9 Dockerfile migration

**What we built**

- Replaced `FROM python:3.11-slim` with `FROM almalinux:9-minimal` in `backend/Dockerfile`.
- Added manual Python 3.11 install steps using `microdnf` (the minimal package manager on AlmaLinux 9).
- Verified the container builds and reports healthy.
- Committed: `feat: migrate backend image to AlmaLinux 9 minimal base`.

**Why this matters**

The on-prem deployment target is an AlmaLinux 9 VM. Using the same OS family in the container reduces surprises when the image runs on the VM — same `dnf`/`rpm` ecosystem, same glibc version, same filesystem layout. What works in the container will work on the server.

**Key commands**

- `docker compose build` — builds the image without starting the container; useful for fast Dockerfile iteration.
- `docker compose up` — starts the container from the already-built image.
- `curl http://localhost:8000/health` — verified the API responds with `200 OK` after the base image swap.

**Gotchas**

Docker layer caching order matters: `COPY requirements.txt` must come before `COPY app/` and the `RUN pip install` step. If the whole `app/` directory is copied first, any source-code change invalidates the pip install layer and forces a full reinstall on every build. Keeping the dependency install layer earlier means only a `requirements.txt` change triggers a reinstall — source edits stay fast.

**Revisit later**

- Compare final image size between `python:3.11-slim` and `almalinux:9-minimal + python3.11`. Worth knowing the size trade-off before committing to the approach.
- Phase 4.2: replace the Dockerfile-level `HEALTHCHECK` with a proper `/health` (liveness) + `/ready` (readiness, checks Oracle) split in the FastAPI app itself.

---

## 2026-06-22 — Phase 1.5: GET /positions endpoint

**What we built**

- Added a `Position` Pydantic model (`symbol`, `quantity`, `avg_price`, `current_price`).
- Added `GET /positions` returning four mock positions: ING stock (INGA.AS), ASML, a German government bond (DBR 0% 2032), and EURUSD — chosen to represent a realistic multi-instrument trading desk.
- Fixed a pre-existing bug: `datetime()` called with no arguments raises a `TypeError`; corrected to `datetime.now()` on both `GET /` and `GET /health`.
- Committed: `feat: add GET /positions endpoint with mock data`.

**Key commands**

- `docker compose up -d --build` — rebuilds the image and starts the container in detached mode. The `--build` flag is required whenever Python source changes; without it Docker reuses the old image and your edits have no effect.
- `curl http://localhost:8000/positions` — confirmed the endpoint returns the four mock positions as a JSON array.

**Gotchas**

`docker compose up` without `--build` does not pick up source code changes — it reuses the existing image. This is standard Docker caching behaviour but easy to forget mid-development; the symptom is that edits appear to have no effect at all. Fix: always use `docker compose up -d --build` when Python files have changed.

`datetime()` with no arguments raises `TypeError: __new__() missing required argument: 'year'`. It was silently broken in earlier code and only caught now during a review of the endpoint responses. `datetime.now()` is the correct call for the current timestamp.

**Revisit later**

- Phase 2: replace the hardcoded mock list with a real `SELECT` from Oracle Database Free.
- Add an `unrealised_pnl` computed field to `Position` (`(current_price - avg_price) * quantity`) — straightforward Pydantic computed field, good exercise for the next session.
