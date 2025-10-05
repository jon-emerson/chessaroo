# Claude Development Guidelines for BlunderLab

## Port Configuration

**ALWAYS use these specific ports for local development:**

- **Frontend (Next.js)**: Port **3000** ONLY
  - Command: `cd frontend && npm run dev`
  - URL: http://localhost:3000

- **Backend (Flask)**: Port **8000** ONLY
  - Command: `export LDFLAGS="-L/opt/homebrew/opt/postgresql@15/lib" && export CPPFLAGS="-I/opt/homebrew/opt/postgresql@15/include" && flask --app backend.app run --port 8000`
  - URL: http://localhost:8000

**NEVER use different ports (3001, 8001, etc.)**

If ports 3000 or 8000 are busy:
1. Kill the existing processes: `lsof -ti:3000 | xargs kill -9` and `lsof -ti:8000 | xargs kill -9`
2. Start new processes on the correct ports

## Database Migration

- Use Alembic migrations managed via Flask-Migrate.
- Apply migrations with `export FLASK_APP=backend.app:create_app && python3 -m flask db upgrade`.
- Never run ad-hoc scripts that drop and recreate tables in production.
- Configure admin access via environment variables set outside the repo:
  - `APP_ENV` (e.g., `development`, `staging`, `production`)
  - `ADMIN_MASTER_PASSWORD_DEV` (development/staging master password)
  - `ADMIN_MASTER_PASSWORD` (production master password)
- Use `.env.local` (ignored by git) for local secrets if needed.

## Development Commands

### Start Local Development
All local work should run inside Docker:

```bash
docker compose up --build
docker compose exec backend flask db upgrade
```

> The backend aborts if it detects a non-container runtime. To bypass (not recommended), set `ALLOW_NON_CONTAINER=1` for that invocation only.
> Put required secrets (e.g., `ADMIN_MASTER_PASSWORD_DEV`) in a local `.env` file or export them before starting Compose; Docker will pass them into the container.

### Deploy to Production
```bash
./scripts/deploy.sh
```

## Project Structure

- **Backend**: Flask API with PostgreSQL
- **Frontend**: Next.js React application
- **Database**: PostgreSQL with SQLAlchemy ORM
- **Deployment**: AWS ECS with Docker containers

## Key Implementation Notes

- Last login tracking is implemented in the User model (`backend/models.py:23`) and login endpoint (`backend/app.py:156-159`)
- Frontend properly handles last login display in Account Settings (`frontend/src/app/settings/page.tsx:102`)
- Database migrations are versioned under `migrations/versions/`

## Claude Development Guidelines for BlunderLab

- You may stage files, but **do not run `git commit` or `git push` unless the user explicitly asks for it.**

## BlunderLab Repo Rules

⚠️  Absolute rule: never run `git commit`, `git commit --amend`, `git push`, or `git push --force` unless the user explicitly asks for it.

