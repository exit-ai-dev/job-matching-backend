"""
Add LINE fields to users table
Migration script to add line_display_name, line_picture_url, and line_email columns
"""
import sys
import os

# Add parent directory to path to import app modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import text
from app.db.session import SessionLocal
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def run_migration():
    """Run the migration to add LINE fields to users table"""
    db = SessionLocal()

    try:
        logger.info("Starting migration: add_line_fields_to_users")

        # Check if columns already exist
        check_sql = text("""
            SELECT column_name
            FROM information_schema.columns
            WHERE table_name = 'users'
            AND column_name IN ('line_display_name', 'line_picture_url', 'line_email')
        """)

        existing_columns = db.execute(check_sql).fetchall()
        existing_column_names = [row[0] for row in existing_columns]

        logger.info(f"Existing LINE columns: {existing_column_names}")

        # Add line_display_name if it doesn't exist
        if 'line_display_name' not in existing_column_names:
            logger.info("Adding line_display_name column...")
            db.execute(text("ALTER TABLE users ADD COLUMN line_display_name VARCHAR(100) NULL"))
            logger.info("✓ line_display_name column added")
        else:
            logger.info("✓ line_display_name column already exists")

        # Add line_picture_url if it doesn't exist
        if 'line_picture_url' not in existing_column_names:
            logger.info("Adding line_picture_url column...")
            db.execute(text("ALTER TABLE users ADD COLUMN line_picture_url VARCHAR(500) NULL"))
            logger.info("✓ line_picture_url column added")
        else:
            logger.info("✓ line_picture_url column already exists")

        # Add line_email if it doesn't exist
        if 'line_email' not in existing_column_names:
            logger.info("Adding line_email column...")
            db.execute(text("ALTER TABLE users ADD COLUMN line_email VARCHAR(255) NULL"))
            logger.info("✓ line_email column added")
        else:
            logger.info("✓ line_email column already exists")

        db.commit()
        logger.info("Migration completed successfully!")

    except Exception as e:
        logger.error(f"Migration failed: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    run_migration()
