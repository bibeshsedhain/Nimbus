# Nimbus

Nimbus is a cloud-native serverless compute platform inspired by AWS Lambda, Vercel, and Render.

The platform enables developers to:
- Upload backend functions/services
- Execute workloads inside isolated containers
- Automatically orchestrate infrastructure
- Scale workloads dynamically
- Monitor executions and logs

---

# Core Features

## Compute
- Containerized execution
- Runtime isolation
- Dynamic execution

## Infrastructure
- Docker-based workloads
- Kubernetes orchestration
- Queue-based execution
- Autoscaling

## Observability
- Metrics dashboards
- Centralized logging
- Health monitoring

## DevOps
- CI/CD pipelines
- Infrastructure as code
- Cloud deployment

---

# Tech Stack

## Backend
- Python
- FastAPI

## Frontend
- React
- TypeScript
- TailwindCSS

## Infrastructure
- Docker
- Kubernetes
- Terraform

## Database
- PostgreSQL

## Queue System
- Redis

## Monitoring
- Prometheus
- Grafana

## Cloud
- AWS

---

# MVP Goal

The MVP should:
1. Accept uploaded Python functions
2. Build Docker containers dynamically
3. Execute functions safely
4. Capture execution logs
5. Return results to users

---

# Long-Term Goal

Build a production-style cloud platform capable of:
- Orchestrating workloads
- Scaling automatically
- Monitoring infrastructure
- Managing distributed execution

---

# Architecture

```text
                Frontend Dashboard
                        |
                        v
                 API Gateway Service
                        |
        ---------------------------------
        |               |               |
        v               v               v
 Deployment       Scheduler        Auth Service
   Service          Service
        |               |
        -----------------
                |
                v
          Redis Queue
                |
                v
        Execution Workers
                |
                v
      Kubernetes Pods/Jobs
                |
        ----------------
        |              |
        v              v
   PostgreSQL      Object Storage
                |
                v
      Prometheus + Grafana
```

---

# Repository Structure

```text
nimbus/
│
├── frontend/
│
├── services/
│   ├── api-gateway/
│   ├── deployment-service/
│   ├── execution-worker/
│   ├── scheduler/
│   └── auth-service/
│
├── infrastructure/
│   ├── docker/
│   ├── kubernetes/
│   └── terraform/
│
├── shared/
│   ├── models/
│   ├── utils/
│   └── configs/
│
├── docs/
│
└── scripts/
```
