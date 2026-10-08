# DevOps-Lab

## Czym jest projekt

Repozytorium do nauki DevOps, Pythona i Basha (remote: `github.com/preszka94/moj-lab-devops`). Główny projekt to `trader-workstation-platform`: symulacja wewnętrznej aplikacji tradingowej z infrastrukturą on-prem (VM-ki VMware, Ansible, Docker, CI). Szczegółowe instrukcje dla tego projektu są w `trader-workstation-platform/CLAUDE.md`.

Repo ma sparse checkout: lokalnie widać tylko część plików.

## Jak uruchomić

```bash
cd ~/Projekty/DevOps-Lab
source venv/bin/activate
pip install -r trader-workstation-platform/backend/requirements.txt   # tylko gdy venv jest nowy
cd trader-workstation-platform && docker compose up                   # cały stos
```

## Struktura folderów

- `trader-workstation-platform/`: backend (FastAPI), frontend, baza, nginx, ansible, CI, dokumentacja, notatki
- `docker/`: dane runtime (MinIO, poza gitem)
- `scripts/`: skrypty pomocnicze
- `venv/`: środowisko Pythona (poza gitem)

## Zasady

- Proste ponad sprytne: każdą linijkę mam rozumieć.
- Nie commituj sekretów: `.env`, kluczy, plików credentials i recovery codes (lista w `.gitignore`).
