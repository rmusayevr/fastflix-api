# FastFlix API 🎬

A progressive backend engineering project to build a production-grade Movie Recommendation Service.

This repository follows a strict 100-day "Deep Dive" roadmap, transitioning from Django patterns to high-performance FastAPI architecture.

## 🎯 Project Goals
- **Architecture:** Moving from Django's "batteries-included" to FastAPI's explicit architecture.
- **Engineering:** Implementing Repository pattern, Dependency Injection, and Async patterns.
- **Quality Assurance:** Comprehensive testing suite with robust code coverage.
- **DevOps:** Building a 100% automated CI/CD pipeline and containerized production environment.
- **Documentation:** Following a "Learning in Public" philosophy.

## 🛠 Tech Stack
- **Framework:** FastAPI
- **Language:** Python 3.11+ (AsyncIO)
- **Database:** PostgreSQL 15 (Neon Serverless in Prod, Dockerized in Dev)
- **ORM:** SQLAlchemy 2.0 (Async via `asyncpg`)
- **Migrations:** Alembic
- **Testing:** Pytest, HTTPX, Pytest-Asyncio
- **CI/CD:** GitHub Actions (Linting & Automated Testing)
- **Containerization:** Docker (Multi-stage builds)
- **Production Server:** Gunicorn with Uvicorn workers

---

## 🚀 How to Run

### 1. Local Development (Docker Compose)
The easiest way to get started is using Docker Compose, which handles the app and the database:

```bash
# Clone the repository
git clone [https://github.com/yourusername/fastflix-api.git](https://github.com/yourusername/fastflix-api.git)
cd fastflix-api

# Create your .env file
cp .env.example .env

# Start everything
docker-compose up --build
```

### 2. Manual Setup
```bash
# Create virtual environment
python -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run migrations & start
alembic upgrade head
uvicorn app.main:app --reload
```

Visit docs at: `http://localhost:8000/docs`

## 🧪 Testing & CI/CD

This project uses a robust asynchronous testing suite and automated quality gates.
- **Local Testing:** Run `pytest` to execute the full suite.
- **CI Pipeline:** Every push to `main` triggers GitHub Actions to run:
  - **Ruff:** For lightning-fast linting and code formatting.
  - **Pytest:** To ensure zero regressions before deployment.

Run all tests:
```bash
pytest
```

Run with coverage report:
```bash
pytest --cov=app --cov-report=html tests/
```

Open `htmlcov/index.html` to view the coverage heatmap.

## 🔐 Security Features
- **Authentication:** OAuth2 Password Bearer flow.
- **Authorization:** Role-based ownership logic (Users can only edit their own data).
- **Cryptography:**
  - Passwords hashed via `bcrypt` (using `passlib`).
  - Stateless authentication via JWT (HS256).
- **Dependencies:** `get_current_user` allows protecting routes with a single line of code.

## 🗺️ Roadmap & Progress

✅ **Phase 1: The Foundation (Basics)**
- [x] **Structure:** Domain-driven layout (`api/`, `core/`, `services/`).
- [x] **Config:** Type-safe settings with Pydantic `BaseSettings`.
- [x] **Routing:** Modular `APIRouter` implementation.
- [x] **Validation:** Strict Pydantic schemas (Input vs Output models).

✅ **Phase 2: Architecture & Database**
- [x] **Database:** Dockerized PostgreSQL.
- [x] **ORM:** Asynchronous SQLAlchemy 2.0.
- [x] **Migrations:** Alembic version control.
- [x] **Pattern:** Repository Pattern (Service -> Repository -> DB).

✅ **Phase 3: Security & Auth**
- [x] **Auth Flow:** OAuth2 Password Bearer (JWT).
- [x] **Hashing:** Secure password storage using `bcrypt`.
- [x] **Authorization:** Row-level security (Users manage only their own data).
- [x] **Relationships:** One-to-Many logic (User -> Movies) enforced via Foreign Keys.

✅ **Phase 4: Reliability & Testing**
- [x] **Test Harness:** Configured `pytest-asyncio` for Windows/Linux compatibility.
- [x] **Fixtures:** Modular `conftest.py` with transaction rollbacks and data cleaning.
- [x] **Integration Tests:** End-to-end API testing using `httpx.AsyncClient`.
- [x] **Unit Tests:** Isolated Service layer testing.
- [x] **Coverage:** Automated reporting with `pytest-cov`.

✅ **Phase 5: DevOps & Deployment**
- [x] **Dockerization:** Optimized multi-stage Dockerfile.
- [x] **Process Management:** Production-ready Gunicorn configuration.
- [x] **CI/CD:** Fully automated GitHub Actions pipeline.
- [x] **Cloud Migration:** Deployed to Railway with Neon Postgres (SSL enforced).

## 📂 Project Structure
```
fastflix-api/
├── app/
│   ├── api/            # Routes & Endpoints
│   ├── core/           # Config, Security & Exceptions
│   ├── db/             # Database session & Base models
│   ├── models/         # SQLAlchemy Table Definitions
│   ├── repositories/   # DB Access Layer (Repository Pattern)
│   ├── schemas/        # Pydantic Models (Validation)
│   ├── services/       # Business Logic Layer
│   └── main.py         # FastAPI Entrypoint
├── alembic/            # Migration scripts & env.py
├── tests/              # Pytest Suite (Integration & Unit)
├── Dockerfile          # Multi-stage production build
├── docker-compose.yml  # Local dev orchestration
├── gunicorn_conf.py    # Production server configuration
├── prestart.sh         # Migration & startup automation script
└── requirements.txt    # Project dependencies
```

**Live Demo:** https://fastflix-api-production.up.railway.app/docs
