#!/usr/bin/env python3
"""
Database migration script to add email column to users table
Run this script BEFORE deploying the new code with email support
"""

import os
import sys
import psycopg2
from urllib.parse import urlparse

def get_database_url():
    """Get database URL from environment or use default"""
    # Check for production DATABASE_URL first
    database_url = os.environ.get('DATABASE_URL')
    if database_url:
        return database_url

    # Fallback to local development database
    return 'postgresql://chessaroo_user:chessaroo_pass@localhost:5432/chessaroo'

def run_migration():
    """Add email column to users table"""
    database_url = get_database_url()

    try:
        # Parse the database URL
        parsed = urlparse(database_url)

        # Connect to database
        conn = psycopg2.connect(
            host=parsed.hostname,
            port=parsed.port or 5432,
            database=parsed.path[1:],  # Remove leading /
            user=parsed.username,
            password=parsed.password
        )

        cur = conn.cursor()

        print("Checking if email column exists...")

        # Check if email column already exists
        cur.execute("""
            SELECT column_name
            FROM information_schema.columns
            WHERE table_name = 'users' AND column_name = 'email'
        """)

        if cur.fetchone():
            print("Email column already exists. No migration needed.")
            return

        print("Adding email column to users table...")

        # Add email column (nullable for now to handle existing users)
        cur.execute("""
            ALTER TABLE users
            ADD COLUMN email VARCHAR(255)
        """)

        # Add unique constraint on email (will be enforced for new users)
        # Note: We can't make it NOT NULL yet because existing users don't have emails
        cur.execute("""
            CREATE UNIQUE INDEX idx_users_email_unique
            ON users (email)
            WHERE email IS NOT NULL
        """)

        # Commit the changes
        conn.commit()

        print("✅ Migration completed successfully!")
        print("📧 Email column added to users table")
        print("🔒 Unique constraint added for email addresses")
        print("\nNote: Existing users will need to add their email through the profile settings.")

    except psycopg2.Error as e:
        print(f"❌ Database error: {e}")
        if conn:
            conn.rollback()
        sys.exit(1)
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        sys.exit(1)
    finally:
        if 'cur' in locals():
            cur.close()
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    print("🔄 Running database migration to add email support...")
    run_migration()