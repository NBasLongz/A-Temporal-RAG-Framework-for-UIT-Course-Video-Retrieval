# Project Guidelines

## Code Style
- **Language**: Python 3.12+
- **Frameworks**: FastAPI, SQLAlchemy 2.0+ (async via `asyncpg`), Pydantic V2 for data validation, LangGraph & LangChain for Agentic RAG, Gradio for the secondary UI.
- **RAG Stack**: LangChain Core, LangGraph for stateful agent orchestration, ChromaDB (Vector) matched with BM25 (Keyword) for Hybrid Retrieval, and Langfuse for telemetry. Google GenAI (Gemini) is used as the LLM provider.
- **Auth & Rate Limit**: JWT bearer auth is used for API protection. SlowAPI provides shared request rate limiting for protected endpoints.
- **Async**: Use asynchronous operations exclusively (FastAPI and SQLAlchemy). Any synchronous I/O operations must be deferred to `asyncio.to_thread`.
- **Primary Keys**: Use `uuid.UUID` for Primary Keys across all database models by default.

## Architecture
Clean layered architecture following the repository pattern:
- **`src/api/`**: FastAPI route handlers and endpoint definitions. Keep routes thin. Choose appropriate REST patterns. Use `Annotated` typing for `Depends` injections (e.g., from `src/dependencies.py`).
- **`src/schemas/`**: Pydantic V2 models for request/response validation. Always enable `model_config = {"from_attributes": True}` for proper ORM serialization.
- **`src/services/`**: Business logic layer.
  - **`src/services/rag/`**: Contains the full LangGraph setup (`agent_graph.py`, `state.py`, `nodes/`), Vector DB (`vectordb.py`), Hybrid Search (`bm25.py`), and RAG Prompts.
  - **`src/services/langfuse/`**: Integration for LLM observability.
- **`src/repositories/`**: Data access layer. Isolate all SQLAlchemy `select`, `insert`, `update`, `delete` queries here. Never use direct `session.execute` within `api/`.
- **`src/models/`**: SQLAlchemy 2.0 declarative models (strict use of `Mapped` and `mapped_column`).
- **`src/dependencies.py`**: Centralize all FastAPI dependency injection (e.g., retrieving `App.state.rag_service` or database sessions). Avoid shadowing imports.
- **`src/database/`**: Database configuration (`config.py`), session management (`session.py`), and auto-seeding logic (`seed.py`).
- **`scripts/`**: Utility scripts like `data_preparation.py` and evaluation using Ragas (`evaluate_rag.py`).
- **`src/api/auth.py`**: OAuth2 password login endpoint returning JWT access tokens.
- **`src/core/rate_limit.py`**: Shared SlowAPI limiter instance used by protected API routes.
- **`src/gradio_ui/`**: Modular Gradio UI package. Keep client calls, handlers, styles, and component layout separated.
- **`gradio_app.py`**: Thin launcher for the Gradio frontend application.

## Conventions
- **Routing Modules**: Delegate business logic strictly to `services/` and database access to `repositories/`. Avoid processing states manually in routers.
- **Transactions**: Evaluate when to use `session.commit()` (e.g., in services for multi-step transactions rather than deep inside repositories). 
- **Error Handling**: Throw `HTTPException` early at the `api/` or `dependencies.py` edges instead of bubbling raw python exceptions from the internal services. 
- **Graph State Tracking**: For `langgraph` state nodes, always preserve state integrity enforcing strict `TypedDict` keys (e.g., watch out for pluralization issues like `source` vs `sources`).
- **Authentication Flow**: Use `OAuth2PasswordBearer` + `Authorization: Bearer <token>` for protected API access. Gradio login should call `/auth/login/token`, store the token in UI state, and pass it on RAG requests.
- **Rate Limiting**: Apply the shared SlowAPI limiter to the RAG endpoint(s). Keep the limiter instance centralized so API routes and decorators use the same object.
- **Resource Initialization**: Retrievers (BM25, Chroma) and the Agentic RAG Service are initialized in the FastAPI `lifespan` inside `main.py` and stored in `app.state` to be injected via `dependencies.py`.
- **Networking**: Default database connections refer to internal Docker networking (`db:5432`), not `localhost:5432`.

## Build and Developer Environment
- **Package Manager**: `uv` (as defined in `pyproject.toml`)
- **Docker Compose**: The application runs entirely via Docker Compose (`backend`, `db` as Postgres 16, and `adminer`). Hot-reload mapping via `docker compose watch` runs sync without container rebuilding.
- **Database Initialization**: `Base.metadata.create_all`, schema backfill for `users.hashed_password`, CSV seeding (using `data/*.csv`), and VectorDB seeding are automatically handled during the FastAPI lifespan.
- **Gradio Run Command**: Start the UI with `uv run python gradio_app.py`. The launcher picks the first free port in the `7860-7869` range and expects the FastAPI backend at `http://localhost:8000` by default.
