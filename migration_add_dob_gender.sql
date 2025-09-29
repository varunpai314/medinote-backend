-- Migration script: Add date_of_birth and gender columns to patient table
-- Run this script on your database to add the missing columns

\c medinote_db;

-- Add date_of_birth column (nullable, since it's optional in frontend)
ALTER TABLE patient ADD COLUMN dob DATE;

-- Add gender column (not null, since it's required in frontend, but allow existing records to be null initially)
ALTER TABLE patient ADD COLUMN gender VARCHAR(20);

-- Add constraint for existing records - we'll allow null for now but new records should have gender
-- Note: In production, you might want to update existing records with default values first

-- Add unique constraint for doctor_id + email combination if it doesn't exist
-- (This should already exist based on the SQLAlchemy model)
CREATE UNIQUE INDEX IF NOT EXISTS uix_doctor_email ON patient(doctor_id, email);

-- Grant permissions to the user
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO medinote_user;

-- Verification queries (uncomment to run):
-- SELECT column_name, data_type, is_nullable FROM information_schema.columns 
-- WHERE table_name = 'patient' ORDER BY column_name;