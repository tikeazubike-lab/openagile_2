#!/bin/bash
# Estate Portfolio Management System - Quick Setup Script
# Run this script to automatically set up the entire application

set -e  # Exit on any error

echo "🚀 Estate Portfolio Management System - Setup"
echo "=============================================="
echo ""

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo -e "${RED}❌ Docker is not installed. Please install Docker first.${NC}"
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo -e "${RED}❌ Docker Compose is not installed. Please install Docker Compose first.${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Docker and Docker Compose are installed${NC}"
echo ""

# Create project directory
PROJECT_DIR="$HOME/estate-portfolio"
echo "📁 Creating project directory: $PROJECT_DIR"

mkdir -p "$PROJECT_DIR"/{scripts,backups}
cd "$PROJECT_DIR"

# Generate secure password
DB_PASSWORD=$(openssl rand -base64 32 | tr -d "=+/" | cut -c1-25)

# Create .env file
echo "🔐 Creating environment configuration..."
cat > .env << EOF
DB_PASSWORD=$DB_PASSWORD
DB_HOST=postgres
DB_NAME=estate_portfolio
DB_USER=portfolio_user
EOF

echo -e "${GREEN}✅ Environment file created${NC}"

# Ask for domain configuration
echo ""
echo "🌐 Domain Configuration"
read -p "Enter your domain (e.g., estate.zubbystudio.shop) or press Enter to skip: " DOMAIN

if [ -z "$DOMAIN" ]; then
    echo -e "${YELLOW}⚠️  No domain specified. Application will run on port 8501${NC}"
    USE_TRAEFIK=false
else
    echo -e "${GREEN}✅ Will configure for domain: $DOMAIN${NC}"
    USE_TRAEFIK=true
    
    read -p "Do you have Traefik already running? (y/n): " HAS_TRAEFIK
    if [[ $HAS_TRAEFIK != "y" ]]; then
        echo -e "${YELLOW}⚠️  You'll need to set up Traefik first or use port-based access${NC}"
    fi
fi

# Create docker-compose.yml
echo ""
echo "📝 Creating Docker Compose configuration..."

if [ "$USE_TRAEFIK" = true ]; then
    # With Traefik
    cat > docker-compose.yml << 'EOF'
version: '3.8'

services:
  postgres:
    image: postgres:15-alpine
    container_name: estate_portfolio_db
    environment:
      POSTGRES_DB: ${DB_NAME}
      POSTGRES_USER: ${DB_USER}
      POSTGRES_PASSWORD: ${DB_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./init_db.sql:/docker-entrypoint-initdb.d/01_init.sql
    networks:
      - estate_network
    restart: unless-stopped
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${DB_USER}"]
      interval: 10s
      timeout: 5s
      retries: 5

  streamlit:
    build: .
    container_name: estate_portfolio_app
    environment:
      DB_HOST: ${DB_HOST}
      DB_NAME: ${DB_NAME}
      DB_USER: ${DB_USER}
      DB_PASSWORD: ${DB_PASSWORD}
    volumes:
      - ./app.py:/app/app.py
      - ./scripts:/app/scripts
      - ./backups:/app/backups
    depends_on:
      postgres:
        condition: service_healthy
    networks:
      - estate_network
    labels:
      - "traefik.enable=true"
      - "traefik.http.routers.estate-portfolio.rule=Host(`DOMAIN_PLACEHOLDER`)"
      - "traefik.http.routers.estate-portfolio.entrypoints=websecure"
      - "traefik.http.routers.estate-portfolio.tls.certresolver=letsencrypt"
      - "traefik.http.services.estate-portfolio.loadbalancer.server.port=8501"
    restart: unless-stopped

volumes:
  postgres_data:

networks:
  estate_network:
    external: true
    name: openagile_default
EOF
    # Replace domain placeholder
    sed -i "s/DOMAIN_PLACEHOLDER/$DOMAIN/g" docker-compose.yml
else
    # Without Traefik (port-based)
    cat > docker-compose.yml << 'EOF'
version: '3.8'

services:
  postgres:
    image: postgres:15-alpine
    container_name: estate_portfolio_db
    environment:
      POSTGRES_DB: ${DB_NAME}
      POSTGRES_USER: ${DB_USER}
      POSTGRES_PASSWORD: ${DB_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./init_db.sql:/docker-entrypoint-initdb.d/01_init.sql
    networks:
      - estate_network
    restart: unless-stopped
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${DB_USER}"]
      interval: 10s
      timeout: 5s
      retries: 5

  streamlit:
    build: .
    container_name: estate_portfolio_app
    environment:
      DB_HOST: ${DB_HOST}
      DB_NAME: ${DB_NAME}
      DB_USER: ${DB_USER}
      DB_PASSWORD: ${DB_PASSWORD}
    volumes:
      - ./app.py:/app/app.py
      - ./scripts:/app/scripts
      - ./backups:/app/backups
    ports:
      - "8501:8501"
    depends_on:
      postgres:
        condition: service_healthy
    networks:
      - estate_network
    restart: unless-stopped

volumes:
  postgres_data:

networks:
  estate_network:
    driver: bridge
EOF
fi

echo -e "${GREEN}✅ Docker Compose configuration created${NC}"

# Create Dockerfile
echo "📝 Creating Dockerfile..."
cat > Dockerfile << 'EOF'
FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    postgresql-client \
    cron \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app.py .
COPY scripts/ ./scripts/

# Setup cron for weekly price scraper (Fridays at 6 PM)
RUN echo "0 18 * * 5 cd /app && python scripts/ngx_scraper.py >> /var/log/cron.log 2>&1" > /etc/cron.d/price-scraper
RUN chmod 0644 /etc/cron.d/price-scraper
RUN crontab /etc/cron.d/price-scraper
RUN touch /var/log/cron.log

EXPOSE 8501

CMD service cron start && streamlit run app.py --server.port=8501 --server.address=0.0.0.0 --server.headless=true
EOF

# Create requirements.txt
echo "📝 Creating requirements.txt..."
cat > requirements.txt << 'EOF'
streamlit==1.29.0
pandas==2.1.4
psycopg2-binary==2.9.9
plotly==5.18.0
python-frontmatter==1.0.1
beautifulsoup4==4.12.2
requests==2.31.0
EOF

# Check if app.py exists
if [ ! -f "app.py" ]; then
    echo ""
    echo -e "${YELLOW}⚠️  app.py not found!${NC}"
    echo "Please copy the complete app.py file from the Claude artifact to:"
    echo "  $PROJECT_DIR/app.py"
    echo ""
    read -p "Press Enter once you've copied app.py..."
fi

# Check if init_db.sql exists
if [ ! -f "init_db.sql" ]; then
    echo ""
    echo -e "${YELLOW}⚠️  init_db.sql not found!${NC}"
    echo "Please copy the init_db.sql file from the Claude artifact to:"
    echo "  $PROJECT_DIR/init_db.sql"
    echo ""
    read -p "Press Enter once you've copied init_db.sql..."
fi

# Check if scripts exist
if [ ! -f "scripts/ngx_scraper.py" ]; then
    echo ""
    echo -e "${YELLOW}⚠️  scripts/ngx_scraper.py not found!${NC}"
    echo "Please copy the ngx_scraper.py file from the Claude artifact to:"
    echo "  $PROJECT_DIR/scripts/ngx_scraper.py"
    echo ""
    read -p "Press Enter once you've copied the scraper script..."
fi

# Make scripts executable
chmod +x scripts/*.py 2>/dev/null || true

echo ""
echo "🔨 Building Docker images..."
docker-compose build

echo ""
echo "🚀 Starting services..."
docker-compose up -d

echo ""
echo "⏳ Waiting for database to be ready..."
sleep 10

# Check if services are running
if docker-compose ps | grep -q "Up"; then
    echo -e "${GREEN}✅ Services are running!${NC}"
    echo ""
    echo "=============================================="
    echo "🎉 Estate Portfolio Manager is ready!"
    echo "=============================================="
    echo ""
    
    if [ "$USE_TRAEFIK" = true ]; then
        echo "🌐 Access your application at:"
        echo "   https://$DOMAIN"
    else
        echo "🌐 Access your application at:"
        echo "   http://localhost:8501"
        echo "   or"
        echo "   http://$(hostname -I | awk '{print $1}'):8501"
    fi
    
    echo ""
    echo "📊 Database credentials:"
    echo "   Database: estate_portfolio"
    echo "   User: portfolio_user"
    echo "   Password: $DB_PASSWORD"
    echo "   (Saved in .env file)"
    echo ""
    echo "📝 Useful commands:"
    echo "   View logs:        docker-compose logs -f"
    echo "   Stop services:    docker-compose down"
    echo "   Restart:          docker-compose restart"
    echo "   Database backup:  docker-compose exec postgres pg_dump -U portfolio_user estate_portfolio > backup.sql"
    echo ""
    echo "📖 Next steps:"
    echo "   1. Open the application in your browser"
    echo "   2. Go to Settings → Import Data to import your Obsidian vault"
    echo "   3. Add companies and holdings"
    echo "   4. Set up weekly price scraper"
    echo ""
else
    echo -e "${RED}❌ Services failed to start. Check logs:${NC}"
    echo "   docker-compose logs"
fi

echo ""
echo "Setup complete! 🎉"
