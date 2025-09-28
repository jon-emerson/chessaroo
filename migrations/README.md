# Chessaroo Database Migrations

This directory contains database migration scripts for the Chessaroo application.

## Migration System

We've transitioned from manual migrations in `app.py` to a proper migration system for better deployment practices.

### Available Migrations

#### `refactor_player_names.py`
**Purpose**: Rebuilds the entire schema to match the latest Flask models (users, games, moves) including the `email` and `last_login` fields.

**Changes**:
- Drops `moves`, `games`, and `users`
- Recreates all tables with current constraints and indexes
- Enforces unique email addresses and move ordering uniqueness

**Destructive**: Yes. All data is removed. Only use this when a clean slate is acceptable.

Run with:
```bash
python3 migrations/refactor_player_names.py $DATABASE_URL
```

#### Legacy incremental migrations
These scripts remain in the repo for reference but are no longer part of the production deployment flow once the baseline reset has been applied.

- `deploy_user_games.py`
- `deploy_user_games_phase2.py`
- `add_user_color.py`

### Usage

1. Run `refactor_player_names.py` against the target database to align the schema with the latest application code.
2. Deploy the application image (no additional ad-hoc SQL is required at container start-up).
3. For future changes, create new migration scripts that build on this baseline.

### Future Migrations

For new migrations, follow this pattern:
1. Create a new script in `migrations/`
2. Make it idempotent when practical (or clearly mark destructive scripts)
3. Use transactions for safety
4. Test locally first
5. Document the new script in this README
