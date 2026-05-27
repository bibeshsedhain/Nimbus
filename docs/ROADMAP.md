# Nimbus Development Roadmap

# PHASE 0 — Learning Foundations

## Learn
- Docker
- Docker Compose
- Basic Kubernetes
- FastAPI
- PostgreSQL
- Redis

---

# PHASE 1 — Core Execution MVP

## Goal
Execute uploaded Python functions inside Docker containers.

## Features
- Upload function
- Generate temporary execution directory
- Build Docker image
- Execute container
- Capture logs
- Return output

## Deliverables
- FastAPI backend
- Docker execution engine
- PostgreSQL integration
- Local execution support

---

# PHASE 2 — Persistent Deployments

## Features
- User authentication
- Deployment storage
- Execution history
- Dashboard UI

---

# PHASE 3 — Async Queue System

## Features
- Redis queue
- Worker service
- Retry handling
- Background execution

---

# PHASE 4 — Kubernetes Migration

## Features
- Kubernetes Jobs
- Pod orchestration
- Service discovery
- Cluster deployment

---

# PHASE 5 — Observability

## Features
- Prometheus metrics
- Grafana dashboards
- Centralized logging
- Health monitoring

---

# PHASE 6 — Autoscaling

## Features
- Horizontal Pod Autoscaler
- Dynamic worker scaling
- Queue-length scaling

---

# PHASE 7 — CI/CD + Infrastructure as Code

## Features
- GitHub Actions
- Terraform
- Automated deployment pipelines

---

# PHASE 8 — Advanced Features

## Optional
- Live logs
- Multi-runtime support
- AI log summaries
- Cold start optimization
- Usage analytics
