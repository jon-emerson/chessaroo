# Claude Development Guidelines for Chessaroo

## Port Configuration

**ALWAYS use these specific ports for local development:**

- **Frontend (Next.js)**: Port **3000** ONLY
  - Command: `cd frontend && npm run dev`
  - URL: http://localhost:3000

- **Backend (Flask)**: Port **8000** ONLY
  - Command: `export LDFLAGS="-L/opt/homebrew/opt/postgresql@15/lib" && export CPPFLAGS="-I/opt/homebrew/opt/postgresql@15/include" && python3 app.py`
  - URL: http://localhost:8000

**NEVER use different ports (3001, 8001, etc.)**

If ports 3000 or 8000 are busy:
1. Kill the existing processes: `lsof -ti:3000 | xargs kill -9` and `lsof -ti:8000 | xargs kill -9`
2. Start new processes on the correct ports

## Database Migration

- Use Alembic migrations managed via Flask-Migrate.
- Apply migrations with `export FLASK_APP=app:create_app && python3 -m flask db upgrade`.
- Never run ad-hoc scripts that drop and recreate tables in production.

## Development Commands

### Start Local Development
```bash
# Terminal 1 - Backend
export LDFLAGS="-L/opt/homebrew/opt/postgresql@15/lib" && export CPPFLAGS="-I/opt/homebrew/opt/postgresql@15/include" && python3 app.py

# Terminal 2 - Frontend
cd frontend && npm run dev
```

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

- Last login tracking is implemented in the User model (`models.py:23`) and login endpoint (`app.py:156-159`)
- Frontend properly handles last login display in Account Settings (`frontend/src/app/settings/page.tsx:102`)
- Database migrations are versioned under `migrations/versions/`
