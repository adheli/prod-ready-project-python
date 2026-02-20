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

user_service/
├── app/
├── tests/
task_service/
├── app/
├── tests/
docker-compose.yml
task.Dockerfile
user.Dockerfile
requirements.txt
.github/workflows/ci.yml
```

## Local Run

```bash
docker compose up --build
```

- User Service: `http://localhost:8000/docs`
- Task Service: `http://localhost:8001/docs`

## Testing

Run tests per service:

```bash
cd user_service && pytest
cd task_service && pytest
```

Includes:

- route/integration-level tests with `TestClient`
- service-layer unit tests
- property-based tests with `hypothesis`
