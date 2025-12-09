# Project Context

## Project Overview
This is a B2C Flask Monorepo containing two self-contained Flask microservices: `user-service` and `order-service`. The project uses a monorepo structure where each service has its own Dockerfile and requirements.txt.

## Purpose
- Provide user registration, login, and profile management (user-service)
- Enable product browsing and order placement (order-service)
- Demonstrate microservices architecture with service-to-service communication
- Support selective CI/CD builds (only changed services are built)

## Architecture
- **Framework**: Flask (Python)
- **Architecture**: Microservices (monorepo)
- **Services**: 
  - `user-service` (port 5001) - User management and authentication
  - `order-service` (port 5002) - Product catalog and order management
- **Authentication**: Demo-only signed tokens using `itsdangerous` (⚠️ NOT for production)
- **Deployment**: Docker containers, GitHub Container Registry (GHCR)
- **CI/CD**: GitHub Actions with selective build based on changed paths

## Key Components
- `services/user-service/` - User registration, login, profile endpoints
- `services/order-service/` - Product catalog, order creation, order retrieval
- `.github/workflows/ci.yml` - CI/CD pipeline that builds only changed services
- `docker-compose.yml` - Local development environment
- `helm/` - Kubernetes deployment charts
- `gitops/` - GitOps configuration for ArgoCD

## Service Details

### user-service
- Registration, login, profile management
- Issues signed tokens for authentication
- Endpoints: `/register`, `/login`, `/profile`, `/healthz`

### order-service
- Product catalog browsing
- Order creation and retrieval
- Validates tokens from user-service
- Endpoints: `/products`, `/create_order`, `/orders`, `/orders/<id>`, `/healthz`

## Deployment Environments
- **Local**: Docker Compose (ports 5001, 5002)
- **Dev**: Kubernetes via GitOps (b2c-dev namespace)
- **Stage**: Kubernetes via GitOps (b2c-stage namespace)
- **Production**: Kubernetes via GitOps (b2c-prod namespace)

## Important Notes
- ⚠️ Authentication is demo-only - uses `itsdangerous` signed tokens
- CI/CD builds only services that have changed (path-based detection)
- Images are pushed to GitHub Container Registry (GHCR)
- Each service is independently deployable
- GitOps workflow updates image tags automatically
