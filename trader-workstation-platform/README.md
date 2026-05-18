# trader-workstation-platform

A DevOps learning project simulating an internal trading-style application
end to end, deployed **on-prem** — no public cloud anywhere. The point isn't
the trading platform; the point is the muscle memory for the kind of system
ING and other tier-one banks actually run.

## Project context

Real trading desks at large banks don't run on managed cloud services. The
application servers are physical Linux boxes in a server room, traders reach
them through Citrix-fronted Windows sessions, and there's no AWS or Azure to
fall back on. This project reproduces that topology faithfully on a single
Mac: an AlmaLinux 9 VM in VMware Fusion stands in for the physical server,
a Windows VM stands in for the trader workstation, and RDP simulates the
Citrix ICA flow.

The authoritative roadmap and phase-by-phase task list live in the Notion
"Trading App Note." This README is the in-repo summary; the per-task study
log lives in [notes/journal.md](notes/journal.md).

## Current state

**Phase 0 — Repo skeleton and runnable backend.** Complete.

- FastAPI app with `GET /` and `GET /health`, runnable in a container
- Dockerfile builds on `python:3.11-slim` (temporary; Phase 1.3 switches to
  AlmaLinux)
- Single-service `docker-compose.yml` exposing port 8000
- Placeholder directories for every layer that comes later (database, nginx,
  ansible, ci, docs)

## Roadmap (high level)

The detailed task list with checkboxes is in the Notion note. The phases:

1. **Stabilize and extend the API** — cleanup, AlmaLinux base, Git workflow,
   real `/positions` `/prices/{symbol}` `/trades` endpoints.
2. **Oracle Database Free** — multi-service docker-compose, schema in Oracle
   syntax (`VARCHAR2`, `NUMBER`, sequences), config via `.env` and
   `pydantic-settings`.
3. **nginx reverse proxy** — every request goes `browser → nginx → backend
   → Oracle`. The internal-app pattern at every bank.
4. **Observability** — structured JSON logging, `/health` (liveness) vs
   `/ready` (readiness), `/metrics` in Prometheus format.
5. **Ansible against localhost** — get fluent on inventory, modules, and
   playbooks before pointing them at a remote VM.
6. **On-prem lab in VMware Fusion** — provision an AlmaLinux 9 VM, configure
   networking and SSH keys, deploy the full stack with Ansible. systemd
   units, firewalld, the lot.
7. **Citrix-style trader workstation** — Windows VM connects via RDP to the
   AlmaLinux session host. Network segmentation locks the backend down.
8. **Azure DevOps Pipelines with a self-hosted agent** — the SaaS pipeline
   can't reach a private subnet, so an agent inside the network pulls work
   out. End-to-end CI/CD without any cloud-hosted workload.

## Local development

**Prerequisites**
- Docker Desktop
- Bash

**Build and run the backend**

```bash
docker-compose up --build
```

**Test the API**

```bash
curl http://localhost:8000/health
curl http://localhost:8000/
```

**Stop**

```bash
docker-compose down
```

## Project layout

```
trader-workstation-platform/
├── README.md                   # this file
├── CLAUDE.md                   # in-repo project brief for Claude Code
├── docker-compose.yml          # local orchestration
├── .gitignore
├── backend/
│   ├── app/main.py             # FastAPI application
│   ├── requirements.txt        # pinned Python deps
│   └── Dockerfile              # backend image (python:3.11-slim → AlmaLinux)
├── frontend/                   # placeholder static page (Phase 3.3)
├── database/                   # Oracle init.sql, wait scripts (Phase 2)
├── nginx/                      # reverse proxy config (Phase 3)
├── ansible/                    # local and remote playbooks (Phases 5-6)
├── ci/                         # azure-pipelines.yml + optional ci.yml (Phase 8)
├── docs/                       # architecture notes and diagrams
└── notes/                      # journal and audits
```

## Target topology

The end state, reproduced on one Mac:

```
Windows VM (VMware Fusion)              <-- trader workstation
   │ RDP — stands in for Citrix ICA
   ▼
Session host
   │ HTTPS over internal virtual network
   ▼
AlmaLinux 9 VM (VMware Fusion)          <-- "physical server"
   └─ nginx → FastAPI → Oracle Database Free
```

Why this matters: in a cloud setup the network just works and you wire things
up by clicking in a portal. On-prem, every box has an IP, every firewall has
rules, every service has a systemd unit, every credential lives in a file
somewhere on disk. Those are the things a junior DevOps engineer actually
gets paid to manage.

## Out of scope (deliberately)

- **No public cloud.** No Azure VMs, AWS, GCP, managed databases, Key Vault.
  Secrets live on disk with proper permissions.
- **No real Citrix** — licensing and weight. RDP simulates the architecture.
- **No Kubernetes, Helm, Kafka, Terraform.** Each is a multi-week rabbit
  hole that adds zero clarity to the on-prem fundamentals.
- **No real broker integration.** Market data and trades are mock.
- **No microservices.** One backend service is plenty.

## Learning principles

- Every config, every command, every script gets walked through line by line.
  No black boxes.
- Heavy inline `#` comments on anything generated — they explain *why* a
  line exists, not *what* it does.
- I write the small things first; Claude Code reviews instead of rewriting
  from scratch.
- Troubleshoot before fix: read the error, form a hypothesis, verify, then
  change code.
