# Nimbus Architecture

# Overview

Nimbus is a distributed cloud-native platform composed of multiple services responsible for deployment, orchestration, execution, monitoring, and scaling.

---

# Core Services

## API Gateway
Responsibilities:
- Authentication
- Request routing
- Rate limiting
- API management

---

## Deployment Service
Responsibilities:
- Accept uploaded code
- Generate Dockerfiles
- Build images
- Register deployments

---

## Scheduler Service
Responsibilities:
- Workload scheduling
- Queue coordination
- Resource management
- Execution dispatching

---

## Execution Workers
Responsibilities:
- Execute workloads
- Manage runtime environments
- Capture logs/output
- Update execution state

---

## Redis Queue
Responsibilities:
- Async task management
- Retry handling
- Background processing

---

## Kubernetes Layer
Responsibilities:
- Pod orchestration
- Autoscaling
- Health checks
- Service discovery

---

## Observability Stack

### Prometheus
Collects metrics.

### Grafana
Visualizes metrics and dashboards.

---

# Execution Flow

```text
User Uploads Function
        ↓
Deployment Service
        ↓
Docker Image Build
        ↓
Image Registered
        ↓
Execution Request Sent
        ↓
Redis Queue
        ↓
Worker Consumes Task
        ↓
Kubernetes Pod Executes Function
        ↓
Logs + Metrics Stored
        ↓
Response Returned
```
