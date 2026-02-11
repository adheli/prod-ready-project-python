# Taskflow - Mini Production-Ready Task Management System

This folder contains a production-style FastAPI skeleton with two microservices:

- **user_service**: registration, authentication, and profile management with lightweight JWT-like token creation.
- **task_service**: task CRUD operations, status updates, deadline filtering, and user ownership validation via REST calls to the user service.

## Stack

- FastAPI
- SQLAlchemy
- PostgreSQL
- Redis (events + cache)
- Docker / Docker Compose
- Pytest + Hypothesis
- GitHub Actions CI

## Architecture

```text
taskflow/
├── user_service/
│   ├── app/
│   ├── tests/
│   ├── Dockerfile
│   └── requirements.txt
├── task_service/
│   ├── app/
│   ├── tests/
│   ├── Dockerfile
│   └── requirements.txt
├── docker-compose.yml
└── .github/workflows/ci.yml
```

## Local Run

```bash
cd taskflow
docker compose up --build
```

- User Service: `http://localhost:8000/docs`
- Task Service: `http://localhost:8001/docs`

## Testing

Run tests per service:

```bash
cd taskflow/user_service && pytest
cd taskflow/task_service && pytest
```

Includes:

- route/integration-level tests with `TestClient`
- service-layer unit tests
- property-based tests with `hypothesis`
