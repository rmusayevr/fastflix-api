# FastFlix API 🎬

A progressive backend engineering project to build a production-grade Movie Recommendation Service.

This repository follows a strict 100-day "Deep Dive" roadmap, transitioning from Django patterns to high-performance FastAPI architecture.

## 🎯 Project Goals
- **Architecture:** Moving from Django's "batteries-included" to FastAPI's explicit architecture.
- **Engineering:** Implementing Repository pattern, Dependency Injection, and Async patterns.
- **Quality Assurance:** Comprehensive testing suite with robust code coverage.
- **Documentation:** Following a "Learning in Public" philosophy.

## 🛠 Tech Stack
- **Framework:** FastAPI
- **Language:** Python 3.12+ (AsyncIO)
- **Database:** PostgreSQL 16 (Async via `asyncpg`)
- **ORM:** SQLAlchemy 2.0
- **Migrations:** Alembic
- **Testing:** Pytest, HTTPX, Pytest-Asyncio

---

## 🚀 How to Run

### 1. Prerequisites
- Docker & Docker Compose
- Python 3.10+

### 2. Start Services
```bash
# Spin up PostgreSQL container
docker-compose up -d
```

### 3. Application Setup
```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows

# Install dependencies
pip install -r requirements.txt

# Apply database migrations
alembic upgrade head

# Run the server
uvicorn app.main:app --reload
```

Visit docs at: `http://localhost:8000/docs`

## 🧪 Testing

This project uses a robust asynchronous testing suite powered by `pytest`.

Run all tests:
```bash
pytest
```

Run with coverage report:
```bash
pytest --cov=app --cov-report=html tests/
```

Open `htmlcov/index.html` to view the coverage heatmap.

## 🔐 Security Features (Phase 3)
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

🚧 **Phase 5: DevOps & Deployment (Coming Soon)**
- [ ] Dockerizing the Application.
- [ ] CI/CD Pipeline (GitHub Actions).
- [ ] Cloud Deployment.

## 📂 Project Structure

```
fastflix-api/
├── app/
│   ├── api/            # Routes (v1/endpoints)
│   ├── core/           # Config & Security
│   ├── db/             # Database connection & Base models
│   ├── models/         # SQLAlchemy Tables
│   ├── repositories/   # DB Access Layer
│   ├── schemas/        # Pydantic Models (Validation)
│   ├── services/       # Business Logic
│   └── main.py         # App Entrypoint
├── tests/              # Pytest Suite
│   ├── conftest.py     # Shared Fixtures
│   └── ...
├── alembic/            # Migration scripts
├── docker-compose.yml  # Database services
└── pytest.ini          # Test configuration
```