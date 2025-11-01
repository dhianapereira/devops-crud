-- Create database
CREATE DATABASE appdb;

-- Create non-root user for the application
CREATE USER appuser WITH ENCRYPTED PASSWORD 'appsecret';

-- Allow the user to connect to the database
GRANT ALL PRIVILEGES ON DATABASE appdb TO appuser;

-- Switch to the new database
\connect appdb;

-- Give privileges on the public schema
GRANT ALL ON SCHEMA public TO appuser;

-- Make sure future tables can be used by this user
ALTER DEFAULT PRIVILEGES IN SCHEMA public
GRANT ALL ON TABLES TO appuser;
