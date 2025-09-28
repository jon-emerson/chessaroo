#!/usr/bin/env python3
"""
Database migration script to add username column to users table
"""
import os
import sys
import secrets
import logging
from models import db, User
from app import create_app
from sqlalchemy import text

def add_username_column():
    """Add username column to users table if it doesn't exist"""
    app = create_app()

    with app.app_context():
        try:
            # Check if username column exists
            result = db.session.execute(text("""
                SELECT COUNT(*) FROM information_schema.columns
                WHERE table_name = 'users' AND column_name = 'username'
            """))

            column_exists = result.scalar() > 0

            if column_exists:
                app.logger.info("Username column already exists, skipping migration")
                return True

            app.logger.info("Adding username column to users table...")

            # Add the username column
            db.session.execute(text("""
                ALTER TABLE users
                ADD COLUMN username VARCHAR(50) UNIQUE
            """))

            # Get all existing users
            existing_users = db.session.execute(text("SELECT id, email FROM users")).fetchall()

            app.logger.info(f"Found {len(existing_users)} existing users to update")

            # Generate usernames for existing users
            for user_row in existing_users:
                user_id, email = user_row

                # Generate a unique username based on email prefix
                email_prefix = email.split('@')[0]
                # Clean and limit the username
                base_username = ''.join(c for c in email_prefix if c.isalnum())[:20]

                # Ensure uniqueness by adding random suffix if needed
                username = base_username
                counter = 1
                while True:
                    # Check if username is taken
                    check_result = db.session.execute(text(
                        "SELECT COUNT(*) FROM users WHERE username = :username"
                    ), {"username": username}).scalar()

                    if check_result == 0:
                        break

                    # Try with a counter
                    username = f"{base_username}{counter}"
                    counter += 1

                    # Fallback to random if too many conflicts
                    if counter > 100:
                        username = f"{base_username}_{secrets.token_hex(3)}"
                        break

                # Update the user with the username
                db.session.execute(text("""
                    UPDATE users SET username = :username WHERE id = :user_id
                """), {"username": username, "user_id": user_id})

                app.logger.info(f"Set username '{username}' for user {email}")

            # Make username column NOT NULL after populating it
            db.session.execute(text("""
                ALTER TABLE users
                ALTER COLUMN username SET NOT NULL
            """))

            db.session.commit()
            app.logger.info("Username column migration completed successfully")
            return True

        except Exception as e:
            db.session.rollback()
            app.logger.error(f"Migration failed: {str(e)}", exc_info=True)
            return False

if __name__ == "__main__":
    success = add_username_column()
    sys.exit(0 if success else 1)