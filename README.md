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


## 🎥 Core Features
- **Recommendation Engine:** Item-based collaborative filtering (SQL-based) to suggest movies based on "Users who liked this also liked..." logic.
- **User Watchlists:** Many-to-Many relationship allowing users to save movies for later.
- **Ratings System:** Users can rate movies (1-10 stars), affecting global averages.
- **Background Tasks:** Asynchronous email delivery and heavy processing using Celery & Redis.
- **Rate Limiting:** Redis-backed throttling to prevent API abuse.

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

✅ **Phase 6: Advanced Logic & Performance**
- [x] **Watchlists**: Many-to-Many relationships implementation.
- [x] **Recommendations**: SQL-based collaborative filtering algorithm.
- [x] **Background Workers**: Celery + Redis for async tasks (Emails).
- [x] **Rate Limiting**: FastAPI Limiter with Redis backend.
- [x] **Model Optimization**: 
    - Native PostgreSQL Search Vectors (TSVector + GIN Index).
    - Denormalized Ratings for O(1) read performance.
    - SEO-friendly Slugs & Audit Timestamps.
    - Async CLI Data Importer with Genre Mapping.

🔄 **Phase 7: Real-Time & Interaction (Days 60-68)**
- [ ] **WebSockets**: Real-time notifications system.
- [ ] **Server-Sent Events (SSE)**: Live status streaming.
- [ ] **Advanced Celery**: Task chaining and prioritization.

🔄 **Phase 8: Observability & Monitoring (Days 69-78)**
- [ ] **Structured Logging**: JSON logging for production parsing.
- [ ] **APM**: Integration with Sentry/OpenTelemetry.
- [ ] **Metrics**: Prometheus & Grafana dashboard integration.

🔄 **Phase 9: Security Hardening (Days 79-88)**
- [ ] **OAuth2**: Social Login (Google/GitHub).
- [ ] **RBAC**: Advanced Role-Based Access Control permissions.
- [ ] **Security Headers**: Middleware hardening (CORS, HSTS).

🔄 **Phase 10: Scale & Search (Days 89-95)**
- [ ] **Search Engine**: ElasticSearch/MeiliSearch integration.
- [ ] **DB Tuning**: Query analysis and index optimization.

🏁 **Phase 11: Final Polish (Days 96-100)**
- [ ] **Documentation**: OpenAPI examples & Architecture diagrams.
- [ ] **Load Testing**: High-concurrency stress testing.
- [ ] **Final Release**: Production deployment v1.0.

## 📂 Project Structure
```
fastflix-api/
├── .github/workflows/  # CI/CD Pipelines (GitHub Actions)
├── app/
│   ├── api/            # Routes & Endpoints (v1)
│   ├── core/           # Config, Security, Celery & Exceptions
│   ├── db/             # Database session & Base models
│   ├── models/         # SQLAlchemy Tables (Movies, Users, Ratings)
│   ├── repositories/   # DB Access Layer (Repository Pattern)
│   ├── schemas/        # Pydantic Models (Request/Response)
│   ├── services/       # Business Logic Layer
│   ├── tasks/          # Background Workers (Celery + Redis)
│   ├── templates/      # Jinja2 Templates (Emails)
│   ├── utils/          # Utility functions (Storage, Helpers)
│   └── main.py         # Application Entrypoint
├── alembic/            # Database Migrations (Version Control)
├── scripts/            # Management CLI & Data Importers
├── tests/              # Pytest Suite (Unit, Integration, Load)
├── Dockerfile          # Multi-stage production build
├── docker-compose.yml  # Full stack orchestration (App, DB, Redis, MinIO)
├── gunicorn_conf.py    # Production Process Manager config
├── prestart.sh         # Migration & startup automation script
└── requirements.txt    # Python Dependencies
```

**Live Demo:** https://fastflix-api-production.up.railway.app/docs