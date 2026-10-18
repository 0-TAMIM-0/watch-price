# WatchPrice 📈
[![Backend CI](https://github.com/0-TAMIM-0/watch-price/actions/workflows/backend.yml/badge.svg?branch=main)](https://github.com/0-TAMIM-0/watch-price/actions/workflows/backend.yml)
[![Worker CI](https://github.com/0-TAMIM-0/watch-price/actions/workflows/worker.yml/badge.svg?branch=main)](https://github.com/0-TAMIM-0/watch-price/actions/workflows/worker.yml)
[![Frontend CI](https://github.com/0-TAMIM-0/watch-price/actions/workflows/frontend.yml/badge.svg?branch=main)](https://github.com/0-TAMIM-0/watch-price/actions/workflows/frontend.yml/badge.svg)


**<span style="color:red;">It is not yet complete. 😢</span>**

A self-hosted price monitoring platform built as a hands-on **DevOps training project** — covering the full lifecycle from local development to CI/CD, containerized deployment, and observability.

## 🎯 About This Project

This is a personal learning project built to apply real-world DevOps skills after completing IBM's **Applied DevOps Engineering** and **DevOps, Cloud, and Agile Foundations** specializations.

Instead of a simple CRUD demo, WatchPrice simulates a realistic multi-service system: users track products, a background worker continuously checks prices, and alerts are triggered when a target price is hit. The application logic is intentionally simple — the real focus is on the **infrastructure, automation, and operational practices** around it: containerization, orchestration, CI/CD pipelines, and monitoring.

Product data and price changes are generated using the **Faker** library (simulated data) rather than live web scraping. This was a deliberate choice — it removes dependency on unstable third-party scraping or paid APIs, keeps the system fully self-contained and reproducible, and lets the project focus entirely on the DevOps lifecycle rather than scraping maintenance.

## 🏗️ Architecture

```
┌─────────────┐      ┌──────────────┐      ┌──────────────┐
│  Frontend   │ ───▶ │   Backend    │ ───▶ │  PostgreSQL  │
│ (Vue 3 + TS)│      │  (Flask API) │      │              │
└─────────────┘      └──────────────┘      └──────────────┘
                             ▲
                             │
                      ┌──────────────┐
                      │    Worker    │
                      │ (Price Sim.) │
                      └──────────────┘
```

- **Frontend** — displays tracked products and their price history
- **Backend** — REST API for managing products and reading price data
- **Worker** — independent service that periodically simulates price changes (via Faker) and writes to price history
- **Database** — stores products and historical price data

The backend and worker are deployed as **separate services**, each with its own Docker image and Kubernetes deployment, to reflect a realistic microservices setup.

## ✨ Features

- Add products to track with a target price
- Automatic periodic price simulation (background worker)
- Price history per product
- Alert/log trigger when a product hits its target price
- Health check endpoints (`/health`, `/ready`) for readiness/liveness probes

## 🛠️ Tech Stack

| Layer            | Technology              |
|-------------------|--------------------------|
| Frontend          | Vue 3 + TypeScript + Vite |
| Backend API       | Flask + SQLAlchemy       |
| Database          | PostgreSQL               |
| Data Simulation   | Faker                    |
| Containerization  | Docker, Docker Compose   |
| Orchestration     | Kubernetes               |
| CI/CD             | GitHub Actions           |

## 📁 Project Structure

```
watchprice/
├── frontend/          # Vue 3 + TypeScript app
├── backend/           # Flask API
├── worker/            # Price simulation service
├── k8s/               # Kubernetes manifests
├── .github/workflows/ # CI/CD pipelines
├── docker-compose.yml
└── README.md
```

## 🚀 Running Locally

```bash
# Clone the repository
git clone https://github.com/<your-username>/watchprice.git
cd watchprice

# Start all services
cp .env.example .env
docker compose up --build
```

- Frontend: `http://localhost:3000`
- Backend API: `http://localhost:5000`

## 📍 Roadmap

This project is being built incrementally, in phases, to reflect a realistic DevOps maturity path rather than a one-off tutorial project.

**Phase 1 — Core Application (current)**
- [x] Backend API + Vue frontend + PostgreSQL
- [x] Worker service with simulated price checks
- [x] Dockerized services with Docker Compose
- [x] CI pipeline: lint → test → build → push
- [x] Kubernetes deployment (Deployments, Services, ConfigMaps, Secrets)

**Phase 2 — Observability & Security**
- [ ] Monitoring with Prometheus + Grafana
- [ ] Centralized logging (Loki)
- [ ] Security scanning in CI (Trivy, Dependabot)
- [ ] Infrastructure as Code with Terraform

**Phase 3 — Advanced DevOps Practices**
- [ ] Ephemeral test environments (spin up → test → tear down in CI)
- [ ] Blue-Green / Canary deployment strategy
- [ ] Automated database backups with tiered storage (hot/warm/cold)
- [ ] Chaos engineering mode (fault injection & recovery testing)

## 📖 Why This Project Exists

This repo is meant to demonstrate applied DevOps thinking, not just tool usage — going from `git push` to a monitored, resilient, production-like deployment, and documenting the reasoning behind each decision along the way.