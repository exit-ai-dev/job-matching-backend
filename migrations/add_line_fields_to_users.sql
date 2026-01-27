-- Add LINE fields to users table
-- Migration: add_line_fields_to_users
-- Date: 2026-01-19

-- Add line_display_name column
ALTER TABLE users
ADD COLUMN line_display_name VARCHAR(100) NULL;

-- Add line_picture_url column
ALTER TABLE users
ADD COLUMN line_picture_url VARCHAR(500) NULL;

-- Add line_email column
ALTER TABLE users
ADD COLUMN line_email VARCHAR(255) NULL;

-- Add comments for documentation
COMMENT ON COLUMN users.line_display_name IS 'LINE display name from LINE profile';
COMMENT ON COLUMN users.line_picture_url IS 'LINE profile picture URL';
COMMENT ON COLUMN users.line_email IS 'Email address from LINE profile';
