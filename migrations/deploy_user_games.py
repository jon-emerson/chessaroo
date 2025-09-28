#!/usr/bin/env python3
"""
PHASE 1 Deployment migration: Add nullable user_id to games table

This migration adds the user_id column as NULLABLE to the games table and assigns
existing games to the first user. Phase 2 will make it NOT NULL.
It's idempotent and safe to run multiple times.
"""
import os
import sys
import logging
from sqlalchemy import create_engine, text, MetaData

def run_migration(database_url):
    """Run the user_id migration"""
    engine = create_engine(database_url)

    with engine.connect() as conn:
        # Start transaction
        trans = conn.begin()

        try:
            print("🔍 Checking if user_id column exists in games table...")

            # Check if user_id column exists
            result = conn.execute(text("""
                SELECT COUNT(*) FROM information_schema.columns
                WHERE table_name = 'games' AND column_name = 'user_id'
            """))

            column_exists = result.scalar() > 0

            if column_exists:
                print("✅ user_id column already exists - migration already applied")
                trans.commit()
                return True

            print("➕ Adding user_id column to games table...")

            # Add the user_id column
            conn.execute(text("""
                ALTER TABLE games
                ADD COLUMN user_id VARCHAR(20)
            """))

            # Get the first user to assign existing games to
            print("👤 Finding first user for existing games...")
            first_user = conn.execute(text(
                "SELECT user_id FROM users ORDER BY created_at LIMIT 1"
            )).fetchone()

            if first_user:
                default_user_id = first_user[0]
                print(f"📋 Assigning existing games to user {default_user_id}")

                # Assign all existing games to the first user
                result = conn.execute(text("""
                    UPDATE games SET user_id = :user_id WHERE user_id IS NULL
                """), {"user_id": default_user_id})

                print(f"✏️  Updated {result.rowcount} games")
            else:
                print("⚠️  No users found - will need to handle manually")

            # Add foreign key constraint (but keep nullable for Phase 1)
            print("🔗 Adding foreign key constraint...")
            conn.execute(text("""
                ALTER TABLE games
                ADD CONSTRAINT fk_games_user_id
                FOREIGN KEY (user_id) REFERENCES users(user_id)
            """))

            # Add index for performance
            print("🔍 Creating index on user_id...")
            conn.execute(text("""
                CREATE INDEX ix_games_user_id ON games(user_id)
            """))

            # Commit transaction
            trans.commit()
            print("✅ Migration completed successfully!")
            return True

        except Exception as e:
            trans.rollback()
            print(f"❌ Migration failed: {str(e)}")
            return False

if __name__ == "__main__":
    # Get database URL from environment or command line
    database_url = os.environ.get('DATABASE_URL')

    if len(sys.argv) > 1:
        database_url = sys.argv[1]

    if not database_url:
        print("❌ Please provide DATABASE_URL environment variable or as argument")
        sys.exit(1)

    print(f"🚀 Running user-games migration...")
    print(f"📊 Database: {database_url.split('@')[1] if '@' in database_url else 'localhost'}")

    success = run_migration(database_url)
    sys.exit(0 if success else 1)