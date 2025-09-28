# Chessaroo Database Migrations

This directory contains database migration scripts for the Chessaroo application.

## Migration System

We've transitioned from manual migrations in `app.py` to a proper migration system for better deployment practices.

### Available Migrations

#### `deploy_user_games.py` (Phase 1)
**Purpose**: Adds nullable user_id column for user-specific game ownership

**Changes**:
- Adds `user_id` column to `games` table (NULLABLE)
- Creates foreign key constraint to `users.user_id`
- Creates index on `user_id` for query performance
- Assigns existing games to the first user (by creation date)

**Idempotent**: Safe to run multiple times - detects if already applied

#### `deploy_user_games_phase2.py` (Phase 2)
**Purpose**: Makes user_id column NOT NULL after Phase 1 is stable

**Changes**:
- Adds NOT NULL constraint to `user_id` column
- Validates no games have NULL user_id before proceeding

**Prerequisites**: Phase 1 must be completed first
**Idempotent**: Safe to run multiple times - detects if already applied

#### `add_user_color.py`
**Purpose**: Adds user_color column to track which color the user played

**Changes**:
- Adds `user_color` column to `games` table (nullable)
- Stores 'w' for white or 'b' for black
- Existing games will have NULL user_color until manually set

**Idempotent**: Safe to run multiple times - detects if already applied

### Usage

#### Local Development
```bash
# Test Phase 1 migration (will show "already applied" if run locally)
python3 migrations/deploy_user_games.py postgresql://chessaroo_user:chessaroo_pass@localhost:5432/chessaroo

# Test Phase 2 migration (after Phase 1 is stable)
python3 migrations/deploy_user_games_phase2.py postgresql://chessaroo_user:chessaroo_pass@localhost:5432/chessaroo

# Test user_color migration
python3 migrations/add_user_color.py postgresql://chessaroo_user:chessaroo_pass@localhost:5432/chessaroo
```

#### AWS Deployment
```bash
# Run Phase 1 migration during first deployment
python3 migrations/deploy_user_games.py $DATABASE_URL

# Run Phase 2 migration during second deployment (after Phase 1 is stable)
python3 migrations/deploy_user_games_phase2.py $DATABASE_URL

# Run user_color migration (can be done anytime after user-specific games are deployed)
python3 migrations/add_user_color.py $DATABASE_URL
```

### Deployment Process

#### Two-Phase Deployment Strategy

**PHASE 1 Deployment** (Safe Zero-Downtime):

1. **Deploy Phase 1 application code** with nullable user_id models
2. **Run Phase 1 migration** to add nullable column and backfill data
3. **Start/restart application** with Phase 1 code
4. **Verify everything works** - users can see their games, new games work

**PHASE 2 Deployment** (After Phase 1 is stable):

5. **Deploy Phase 2 application code** with NOT NULL user_id models
6. **Run Phase 2 migration** to add NOT NULL constraint
7. **Start/restart application** with Phase 2 code

#### Example Deployment Sequence

**Phase 1:**
```bash
# 1. Build and push Phase 1 Docker image (nullable user_id)
docker build -t chessaroo:phase1 .
docker tag chessaroo:phase1 $ECR_URI:phase1
docker push $ECR_URI:phase1

# 2. Run Phase 1 migration
python3 migrations/deploy_user_games.py $RDS_DATABASE_URL

# 3. Update ECS service to use Phase 1 image
aws ecs update-service --cluster chessaroo --service chessaroo-service --force-new-deployment
```

**Phase 2 (after Phase 1 is verified stable):**
```bash
# 4. Build and push Phase 2 Docker image (NOT NULL user_id)
docker build -t chessaroo:phase2 .
docker tag chessaroo:phase2 $ECR_URI:phase2
docker push $ECR_URI:phase2

# 5. Run Phase 2 migration
python3 migrations/deploy_user_games_phase2.py $RDS_DATABASE_URL

# 6. Update ECS service to use Phase 2 image
aws ecs update-service --cluster chessaroo --service chessaroo-service --force-new-deployment
```

### Migration Safety

The `deploy_user_games.py` migration:
- ✅ **Checks if already applied** - won't run twice
- ✅ **Uses transactions** - rolls back on failure
- ✅ **Assigns existing data** - doesn't lose games
- ✅ **Detailed logging** - shows exactly what's happening
- ✅ **Error handling** - fails safely

### Future Migrations

For new migrations, follow this pattern:
1. Create a new script in `migrations/`
2. Make it idempotent (check if already applied)
3. Use transactions for safety
4. Test locally first
5. Document in this README