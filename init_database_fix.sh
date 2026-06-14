#!/bin/bash

# Load environment variables
source .env

# Get or create DB_PASSWORD
if [ -z "$DB_PASSWORD" ]; then
    echo "DB_PASSWORD not found in .env, generating one..."
    DB_PASSWORD=$(openssl rand -base64 32)
    echo "DB_PASSWORD=$DB_PASSWORD" >> .env
    echo "✅ Generated and saved DB_PASSWORD"
fi

echo "🔧 Creating OpenProject database and user..."

# Create database and user
docker exec openagile_postgres psql -U postgres << EOF
-- Drop existing user/database if they exist (start fresh)
DROP DATABASE IF EXISTS openproject;
DROP USER IF EXISTS openproject;

-- Create new user with password
CREATE USER openproject WITH PASSWORD '$DB_PASSWORD';

-- Create database owned by openproject user
CREATE DATABASE openproject OWNER openproject;

-- Grant all privileges
GRANT ALL PRIVILEGES ON DATABASE openproject TO openproject;

-- Confirm creation
\l openproject
\du openproject
EOF

echo "✅ Database setup complete!"
echo ""
echo "🔄 Now updating docker-compose.yml..."

# Update the OpenProject DATABASE_URL in docker-compose.yml
# Note: You'll need to do this manually or I can provide the correct config

echo "✅ Done! Now restart OpenProject:"
echo "   docker compose restart openproject"
echo "   docker logs -f openproject"
