# BlunderLab Database Migrations

This directory contains database migration scripts for the BlunderLab application.

## Migration System

BlunderLab now uses Alembic via Flask-Migrate. Manual one-off scripts are retired in favour of versioned revisions tracked in this directory.

### Current revisions

- `0993f449f98a_initial_schema.py` — Baseline schema defining `users`, `games`, and `moves` with the constraints used by the Flask models.

### Running migrations

```bash
# Ensure the application dependencies are installed
export FLASK_APP=backend.app:create_app
python3 -m flask db upgrade
```

`flask db upgrade` is idempotent and should be executed during every deployment.

> **First-time adoption:** if the target database already contains the tables from a pre-Alembic deploy, stamp it before the first upgrade so Alembic records the baseline without recreating tables:
> ```bash
> export FLASK_APP=backend.app:create_app
> python3 -m flask db stamp 0993f449f98a
> ```

### Creating new migrations

1. Make model changes in `backend/models.py`.
2. Generate a revision: `python3 -m flask db migrate -m "short description"`
3. Review / edit the auto-generated file under `migrations/versions/`.
4. Apply locally with `python3 -m flask db upgrade` before deploying.

### Legacy scripts

The ad-hoc scripts (`deploy_user_games.py`, `deploy_user_games_phase2.py`, `add_user_color.py`) are kept only as historical references and should not be run in production. They will be removed once any live environments depending on them have been migrated to the Alembic baseline.
