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

## 🔜 Next Up: Phase 2 (Persistence)
- Integrating **PostgreSQL**.
- Managing Migrations with **Alembic**.
- Implementing **JWT Authentication**.