# SafeDoc - Invoice Processing System

**Project Status**: Learning Project #1 (Learning Backend + Infrastructure)  
**Started**: Early 2024  
**Purpose**: Build automated invoice processing pipeline with Oracle database and cloud infrastructure

## 📋 Project Overview

SafeDoc is a full-stack learning project that combines:
- **Backend API**: Flask-based REST API (`src/web_app/`)
- **Data Processing Pipeline**: Batch invoice processor (`src/scripts/`)
- **Database**: Oracle Database with invoice data models
- **Storage**: MinIO S3-compatible object storage
- **Infrastructure**: Docker, Ansible, Google Cloud Build
- **Deployment**: GCP with Tailscale VPN integration

## 🏗️ Architecture

### Source Code Structure

```
src/
├── web_app/              # Flask web application
│   ├── app.py           # Main Flask app
│   └── templates/       # HTML templates
└── scripts/             # Data processing & utilities
    ├── backend_app.py   # Main invoice processing backend
    ├── setup_db.py      # Database initialization
    ├── test_minio.py    # MinIO storage testing
    ├── view_invoices.sql # Database queries
    └── insert_test_data.py # Test data generation
```

### Infrastructure Structure

```
infrastructure/
├── docker/
│   └── docker-compose.yml    # Docker Compose orchestration
├── ansible/
│   ├── inventory.ini         # Ansible inventory
│   └── inspect-mac.yml       # Mac inspection playbook
├── cloudbuild.yaml           # Google Cloud Build config
└── deploy.yml                # Ansible deployment playbook
```

### Data & Configuration

```
data/
├── input_invoices/           # Sample invoice PDFs
└── diagrams/                 # Business process diagrams (BPMN)

config/
├── gcp-credentials.json      # GCP service account (git-ignored)
└── hosts.ini                 # Host configuration
```

## 🚀 Quick Start

### Prerequisites
- Docker & Docker Compose
- Python 3.x
- Ansible
- Oracle Database (via Docker)
- MinIO (via Docker)

### Running the Stack

```bash
cd projects/safedoc

# Start infrastructure (Docker Compose)
docker-compose -f infrastructure/docker/docker-compose.yml up -d

# Initialize database
python3 src/scripts/setup_db.py

# Run batch invoice processing
./process_all.sh

# Start web application
python3 src/web_app/app.py
```

## 📚 Key Learning Concepts

### Python
- Flask web framework basics
- File I/O and PDF processing
- Database connectivity (Oracle)
- Batch processing patterns
- Object storage (MinIO) integration

### DevOps & Infrastructure
- Docker Compose for multi-service orchestration
- Ansible for configuration management & deployment
- Google Cloud Build for CI/CD
- Environment variable management
- Infrastructure as Code principles

### Database
- Oracle Database setup & management
- SQL queries and views
- Data modeling for invoice processing

### Tools & Practices
- Bash scripting for automation
- Git workflow and version control
- Configuration management
- Secrets management (git-ignoring credentials)

## 📂 Important Files Reference

| File | Purpose |
|------|---------|
| `process_all.sh` | Main batch processing orchestration script |
| `infrastructure/docker/docker-compose.yml` | Docker services configuration |
| `infrastructure/deploy.yml` | Ansible deployment playbook |
| `infrastructure/cloudbuild.yaml` | GCP CI/CD pipeline config |
| `src/scripts/backend_app.py` | Core invoice processing logic |
| `src/web_app/app.py` | REST API and web interface |

## 📝 Documentation

- [Commands Reference](docs/commands.txt) - Useful CLI commands
- Business Process Diagram: `data/diagrams/diagram_business_Piotr_Reszka.bpmn`

## 🔗 Integration Points

- **GCP**: Cloud Build, GCP credentials for deployment
- **Tailscale VPN**: Secure tunnel for deployment
- **MinIO**: Object storage for invoice files
- **Oracle Database**: Persistent invoice data

## ⚠️ Notes for Future Development

- Credentials are git-ignored (`.gitignore`)
- Update path references if moving files within `infrastructure/`
- Docker services require proper environment variables
- Ansible playbooks assume specific host configurations

## 📊 Learning Progress Checklist

- [ ] Understand Flask application structure
- [ ] Run Oracle Database via Docker
- [ ] Process sample invoices with `process_all.sh`
- [ ] Write custom Ansible playbook
- [ ] Deploy to GCP using Cloud Build
- [ ] Implement custom invoice extraction logic
- [ ] Add error handling and logging
- [ ] Set up monitoring and alerting

---

**Next Learning Project**: Check root `README.md` for additional projects and learning goals.
