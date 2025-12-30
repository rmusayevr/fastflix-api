# FastFlix API 🎬

A progressive backend engineering project to build a production-grade Movie Recommendation Service.

## 🎯 Project Goals
- **Architecture:** Moving from Django's "batteries-included" to FastAPI's explicit architecture.
- **Engineering:** Implementing Repository pattern, Dependency Injection, and Async patterns.
- **Documentation:** Following a 100-day "Learning in Public" roadmap.

## 🛠 Tech Stack
- **Framework:** FastAPI
- **Validation:** Pydantic
- **Database:** SQLite (Phase 1) -> PostgreSQL (Phase 2)

## 🚀 Progress: Phase 1 (The Foundation) - COMPLETED
- [x] **Project Structure:** Domain-driven layout (`api/`, `core/`, `services/`).
- [x] **Configuration:** Type-safe settings with Pydantic.
- [x] **Routing:** Modular `APIRouter` implementation.
- [x] **Validation:** Strict Pydantic schemas (Input vs Output models).
- [x] **Architecture:** Dependency Injection and Service Layer pattern.

## 🏗️ Progress: Phase 2 (Architecture) - COMPLETED
- [x] **Database:** PostgreSQL 15 (Dockerized)
- [x] **ORM:** SQLAlchemy 2.0 (Async)
- [x] **Migrations:** Alembic
- [x] **Pattern:** Repository Pattern (Service -> Repository -> DB)

## 🔐 Progress: Phase 3 (Security Features) - COMPLETED
- [x] **Authentication:** OAuth2 Password Bearer flow.
- [x] **Authorization:** Role-based ownership logic (Users can only edit their own data).
- [x] **Cryptography:**
  - Passwords hashed via `bcrypt`.
  - Stateless authentication via JWT (HS256).
- [x] **Dependencies:** `get_current_user` allows protecting routes with a single line of code.
