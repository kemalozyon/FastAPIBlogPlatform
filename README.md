# FastAPI Blog

A full-stack blog platform built with **FastAPI**. It serves both a server-rendered HTML site (Jinja2 + Bootstrap) and a JSON REST API from the same app, with JWT authentication, an async PostgreSQL backend, image uploads to S3, and transactional email.

> Started as a learning project for exploring FastAPI, it has since grown real-world features: auth, an async ORM, migrations, S3 uploads, and email.

🔗 **Live demo:** [fastapiblogplatform.onrender.com](https://fastapiblogplatform.onrender.com)

## Features

- 📝 **Posts** — create, read, edit, and delete blog posts (owner-only for mutations)
- 👤 **Users & auth** — registration, login via OAuth2 password flow, JWT bearer tokens
- 🔒 **Password reset** — emailed reset links backed by single-use, hashed tokens
- 🖼️ **Profile pictures** — Pillow-processed images stored on Amazon S3
- 📄 **Pagination** — server-rendered first page + "Load More" via the API
- ✂️ **Post previews** — long posts are truncated on the listing with a "Read more" link
- 🌗 **Light / dark theme** — with an auto option
- 📱 **Responsive UI** — modern single-column layout

## Tech stack

| Area | Choice |
|------|--------|
| Framework | FastAPI |
| Templating | Jinja2 + Bootstrap 5 |
| Database | PostgreSQL (async `psycopg` driver) |
| ORM | SQLAlchemy 2.0 (typed `Mapped[...]`, async) |
| Migrations | Alembic |
| Auth | JWT (`pyjwt`), password hashing with `pwdlib` (argon2) |
| Storage | Amazon S3 (`boto3`) |
| Email | Brevo HTTP API (`httpx`) |
| Config | `pydantic-settings` |
| Tooling | [uv](https://docs.astral.sh/uv/) (Python 3.11) |

## Architecture

**Dual-surface app** — `main.py` mounts two surfaces on one FastAPI app:

- **JSON API** under `/api/*` (`routers/posts.py`, `routers/users.py`)
- **Server-rendered HTML pages** defined in `main.py` (`/`, `/posts/{id}`, `/login`, `/account`, …), excluded from the OpenAPI schema

Both share a single set of exception handlers that branch on the request path: `/api/*` gets JSON errors, everything else gets a rendered `error.html`.

**Fully async** — an `AsyncEngine` + `async_sessionmaker` (`database.py`), relationships eager-loaded with `selectinload(...)`, and blocking I/O (Pillow, boto3) offloaded to a threadpool via `run_in_threadpool` (`image_utils.py`).

**Migrations are the source of truth** — the app never calls `create_all`; schema changes go through Alembic, which reads `settings.database_url`.

## Project structure

```
main.py            # App setup, HTML routes, exception handlers, /health
config.py          # pydantic-settings (reads .env)
database.py        # Async engine, session, Base, get_db dependency
models.py          # User, Post, PasswordResetToken
schemas.py         # Pydantic request/response models
auth.py            # JWT, password hashing, CurrentUser dependency
routers/
  posts.py         # /api/posts
  users.py         # /api/users
image_utils.py     # Pillow processing + S3 upload/delete
email_utils.py     # Brevo email sending + password-reset template
alembic/           # Migration environment and versions
templates/         # Jinja2 templates (+ email/ subtemplates)
static/            # CSS, JS, icons
```

## Getting started

### Prerequisites

- [uv](https://docs.astral.sh/uv/) (manages Python 3.11 and dependencies)
- A PostgreSQL database
- An S3 bucket (for profile picture uploads)
- A [Brevo](https://www.brevo.com) account (for email) — optional if you don't need password reset

### 1. Install dependencies

```bash
uv sync
```

### 2. Configure environment

Create a `.env` file in the project root:

```dotenv
# Required
DATABASE_URL=postgresql+psycopg://user:password@host:5432/dbname
SECRET_KEY=your-long-random-secret
S3_BUCKET_NAME=your-bucket-name

# S3 (optional if using instance/role credentials)
S3_REGION=eu-north-1
S3_ACCESS_KEY_ID=...
S3_SECRET_ACCESS_KEY=...

# Email (Brevo)
BREVO_API_KEY=xkeysib-...
MAIL_FROM=noreply@yourdomain.com

# App
FRONTEND_URL=http://localhost:8000
```

> **Never commit `.env`** — it holds live secrets. Make sure it is listed in `.gitignore`.

### 3. Run migrations

```bash
uv run alembic upgrade head
```

### 4. Start the dev server

```bash
uv run uvicorn main:app --reload
```

The site is at [http://localhost:8000](http://localhost:8000); interactive API docs at [http://localhost:8000/docs](http://localhost:8000/docs).

## Common commands

| Task | Command |
|------|---------|
| Sync dependencies | `uv sync` |
| Run dev server | `uv run uvicorn main:app --reload` |
| Add a dependency | `uv add <pkg>` (`--group dev` for dev-only) |
| Generate a migration | `uv run alembic revision --autogenerate -m "<msg>"` |
| Apply migrations | `uv run alembic upgrade head` |
| Send a test email | `uv run python test_email.py you@example.com` |

## API overview

Interactive docs are available at `/docs` (Swagger) and `/redoc`. Highlights:

**Posts** (`/api/posts`)
- `GET /` — paginated list (`?skip=&limit=`)
- `GET /{id}` — single post
- `POST /` — create *(auth)*
- `PUT /{id}` · `PATCH /{id}` — update *(owner)*
- `DELETE /{id}` — delete *(owner)*

**Users** (`/api/users`)
- `POST /` — register
- `POST /token` — log in (OAuth2 password flow), returns a JWT
- `GET /me` — current user *(auth)*
- `POST /forgot-password` · `POST /reset-password` — password reset flow
- `PATCH /me/password` — change password *(auth)*
- `GET /{id}` · `GET /{id}/posts` — public profile & posts
- `PATCH /{id}/picture` · `DELETE /{id}/picture` — profile picture *(owner)*

`GET /health` returns `200` with a DB connectivity check.

## Deployment notes

Deployed on **Render**. A couple of gotchas worth knowing:

- **SMTP is blocked** on Render's outbound ports, so email uses Brevo's **HTTP API** (port 443), not SMTP.
- **Deliverability** requires sending from an address on a **domain authenticated in Brevo** (DKIM). Sending from a free `@gmail.com` address falls back to Brevo's shared domain, which mail providers rate-limit.
- Set all environment variables (`DATABASE_URL`, `SECRET_KEY`, `S3_*`, `BREVO_API_KEY`, `MAIL_FROM`, `FRONTEND_URL`) in the Render dashboard — the `.env` file is not deployed.

## Notes

- The `media/` directory holds legacy local uploads from before the S3 migration and is no longer written to.
- There is no automated test suite yet (`pytest` and `moto` are in the dev group, but no `tests/` directory exists).
