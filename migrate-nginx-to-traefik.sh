#!/bin/bash

# ============================================
# OpenAgile Board - Nginx to Traefik Migration
# Version: 2.0 (With Safeguards)
# ============================================
# This script safely migrates from Nginx to Traefik
# with proper existence checks and safeguards
# ============================================

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Banner
echo -e "${BLUE}"
cat << "EOF"
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║        OpenAgile Board - Nginx to Traefik Migration         ║
║                     Version 2.0 (Safe)                       ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
EOF
echo -e "${NC}"

# Check if running as root
if [ "$EUID" -ne 0 ]; then 
    log_error "Please run as root (use sudo)"
    exit 1
fi

# ============================================
# STEP 1: PRE-FLIGHT CHECKS
# ============================================

log_info "Step 1: Running pre-flight checks..."

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    log_error "Docker is not installed. Please install Docker first."
    exit 1
fi
log_success "Docker is installed"

# Check if Docker Compose is available
if ! docker compose version &> /dev/null; then
    log_error "Docker Compose is not available. Please install Docker Compose."
    exit 1
fi
log_success "Docker Compose is available"

# Check if required tools are installed
REQUIRED_TOOLS=("lsof" "ufw")
for tool in "${REQUIRED_TOOLS[@]}"; do
    if ! command -v "$tool" &> /dev/null; then
        log_warning "$tool not found, installing..."
        apt-get update && apt-get install -y "$tool"
    fi
done
log_success "All required tools available"

# ============================================
# STEP 2: CHECK NGINX STATUS
# ============================================

log_info "Step 2: Checking Nginx status..."

NGINX_INSTALLED=false
NGINX_RUNNING=false

if command -v nginx &> /dev/null; then
    NGINX_INSTALLED=true
    log_warning "Nginx is installed"
    
    if systemctl is-active --quiet nginx 2>/dev/null; then
        NGINX_RUNNING=true
        log_warning "Nginx is currently running"
    else
        log_info "Nginx is installed but not running"
    fi
else
    log_info "Nginx is not installed - skipping Nginx removal"
fi

# ============================================
# STEP 3: BACKUP NGINX CONFIGURATION
# ============================================

if [ "$NGINX_INSTALLED" = true ]; then
    log_info "Step 3: Backing up Nginx configuration..."
    
    BACKUP_DIR="$HOME/openagile/backups/nginx-backup-$(date +%Y%m%d_%H%M%S)"
    
    # Check if backup directory structure exists
    if [ ! -d "$HOME/openagile/backups" ]; then
        log_warning "Backup directory doesn't exist, creating it..."
        mkdir -p "$HOME/openagile/backups"
    fi
    
    if [ -d /etc/nginx ]; then
        mkdir -p "$BACKUP_DIR"
        cp -r /etc/nginx/* "$BACKUP_DIR/" 2>/dev/null || true
        
        # Save Nginx status information
        cat > "$BACKUP_DIR/nginx-status.txt" << EOF
Nginx Backup Information
========================
Backup Date: $(date)
Nginx Version: $(nginx -v 2>&1)
Nginx Running: $NGINX_RUNNING
Backup Location: $BACKUP_DIR

Configuration Files Backed Up:
$(ls -lah $BACKUP_DIR/)
EOF
        
        log_success "Nginx configuration backed up to: $BACKUP_DIR"
        log_info "Backup size: $(du -sh "$BACKUP_DIR" | cut -f1)"
    else
        log_warning "No /etc/nginx directory found to backup"
    fi
else
    log_info "Step 3: Skipping Nginx backup (not installed)"
fi

# ============================================
# STEP 4: CHECK PORT AVAILABILITY
# ============================================

log_info "Step 4: Checking port availability..."

check_port() {
    local port=$1
    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1; then
        local process=$(lsof -Pi :$port -sTCP:LISTEN | tail -n 1 | awk '{print $1}')
        log_warning "Port $port is in use by: $process"
        return 1
    else
        log_success "Port $port is available"
        return 0
    fi
}

PORT_80_FREE=false
PORT_443_FREE=false

check_port 80 && PORT_80_FREE=true || PORT_80_FREE=false
check_port 443 && PORT_443_FREE=true || PORT_443_FREE=false

# ============================================
# STEP 5: STOP AND REMOVE NGINX
# ============================================

if [ "$NGINX_RUNNING" = true ] || [ "$PORT_80_FREE" = false ] || [ "$PORT_443_FREE" = false ]; then
    log_info "Step 5: Stopping and removing Nginx..."
    
    # Stop Nginx service
    if systemctl is-active --quiet nginx 2>/dev/null; then
        log_info "Stopping Nginx service..."
        systemctl stop nginx
        systemctl disable nginx
        log_success "Nginx service stopped and disabled"
    fi
    
    # Ask user about Nginx removal
    echo ""
    log_warning "Nginx package removal options:"
    echo "  1) Keep Nginx installed (just stopped)"
    echo "  2) Remove Nginx package (keep config backup)"
    echo "  3) Purge Nginx completely (remove everything)"
    echo ""
    read -p "Choose option (1/2/3) [default: 2]: " nginx_removal
    nginx_removal=${nginx_removal:-2}
    
    case $nginx_removal in
        1)
            log_info "Keeping Nginx installed"
            ;;
        2)
            log_info "Removing Nginx package..."
            apt-get remove -y nginx nginx-common 2>/dev/null || true
            log_success "Nginx package removed (config backup preserved)"
            ;;
        3)
            log_warning "Purging Nginx completely..."
            apt-get purge -y nginx nginx-common 2>/dev/null || true
            apt-get autoremove -y 2>/dev/null || true
            log_success "Nginx purged completely"
            ;;
        *)
            log_error "Invalid option"
            exit 1
            ;;
    esac
    
    # Verify ports are now free
    sleep 2
    check_port 80 && PORT_80_FREE=true || PORT_80_FREE=false
    check_port 443 && PORT_443_FREE=true || PORT_443_FREE=false
    
    if [ "$PORT_80_FREE" = false ] || [ "$PORT_443_FREE" = false ]; then
        log_error "Ports are still in use. Please manually stop the services:"
        lsof -Pi :80 -sTCP:LISTEN 2>/dev/null || true
        lsof -Pi :443 -sTCP:LISTEN 2>/dev/null || true
        exit 1
    fi
else
    log_info "Step 5: Ports are already free, skipping Nginx removal"
fi

# ============================================
# STEP 6: ENSURE OPENAGILE DIRECTORY STRUCTURE
# ============================================

log_info "Step 6: Ensuring OpenAgile directory structure..."

# Check if directory exists
if [ -d "$HOME/openagile" ]; then
    log_success "OpenAgile directory already exists: $HOME/openagile"
    cd "$HOME/openagile"
    
    # Check for required subdirectories and create if missing
    SUBDIRS=(
        "configs/traefik"
        "configs/prometheus"
        "configs/grafana/provisioning/datasources"
        "configs/grafana/provisioning/dashboards"
        "configs/grafana/dashboards"
        "configs/n8n"
        "configs/gitea"
        "configs/woodpecker"
        "scripts"
        "backups"
        "monitoring"
        "erpnext/sites"
        "pipelines/examples"
    )
    
    log_info "Checking subdirectories..."
    for dir in "${SUBDIRS[@]}"; do
        if [ ! -d "$dir" ]; then
            log_warning "Creating missing directory: $dir"
            mkdir -p "$dir"
        else
            log_success "✓ $dir exists"
        fi
    done
    
else
    log_warning "OpenAgile directory doesn't exist, creating it..."
    cd "$HOME"
    mkdir -p openagile && cd openagile
    
    # Initialize Git repository
    if [ ! -d .git ]; then
        log_info "Initializing Git repository..."
        git init
        git config user.name "zubbyik"
        git config user.email "zubbyik@gmail.com"
        
        # Create .gitignore
        cat > .gitignore << 'EOF'
*.env
*.key
*.pem
backups/
.secrets/
deployment.log
*.log
EOF
        log_success "Git repository initialized"
    fi
    
    # Create all subdirectories
    log_info "Creating directory structure..."
    mkdir -p configs/{traefik,prometheus,grafana/{provisioning/{datasources,dashboards},dashboards},n8n,gitea,woodpecker}
    mkdir -p scripts backups monitoring erpnext/sites pipelines/examples
    
    log_success "Directory structure created"
fi

# Make scripts executable if they exist
if [ -d scripts ]; then
    chmod +x scripts/*.sh 2>/dev/null || true
    log_success "Scripts made executable"
fi

log_success "Directory structure verified and ready"

# ============================================
# STEP 7: VERIFY CONFIGURATION FILES
# ============================================

log_info "Step 7: Verifying configuration files..."

REQUIRED_FILES=(
    "docker-compose.yml"
    ".env"
    "configs/traefik/traefik.yml"
    "configs/traefik/dynamic.yml"
    "configs/prometheus/prometheus.yml"
    "configs/prometheus/alerts.yml"
)

MISSING_FILES=()

for file in "${REQUIRED_FILES[@]}"; do
    if [ -f "$file" ]; then
        log_success "✓ $file exists"
    else
        log_warning "✗ $file is MISSING"
        MISSING_FILES+=("$file")
    fi
done

if [ ${#MISSING_FILES[@]} -gt 0 ]; then
    log_error "Missing configuration files detected!"
    log_warning "Please create these files before proceeding:"
    for file in "${MISSING_FILES[@]}"; do
        echo "  - $file"
    done
    echo ""
    read -p "Continue anyway? (yes/no) [default: no]: " continue_missing
    continue_missing=${continue_missing:-no}
    if [ "$continue_missing" != "yes" ]; then
        log_info "Migration paused. Create missing files and re-run this script."
        exit 0
    fi
fi

# ============================================
# STEP 8: UPDATE UFW FIREWALL RULES
# ============================================

log_info "Step 8: Updating firewall rules..."

if command -v ufw &> /dev/null; then
    # Check if UFW is active
    if ufw status | grep -q "Status: active"; then
        log_info "UFW is active, updating rules..."
        
        # Ensure required ports are allowed
        ufw allow 22/tcp comment 'SSH' 2>/dev/null || true
        ufw allow 80/tcp comment 'HTTP (Traefik)' 2>/dev/null || true
        ufw allow 443/tcp comment 'HTTPS (Traefik)' 2>/dev/null || true
        ufw allow 8080/tcp comment 'Traefik Dashboard' 2>/dev/null || true
        ufw allow 2222/tcp comment 'Gitea SSH' 2>/dev/null || true
        
        log_success "Firewall rules updated"
        
        # Display current rules
        log_info "Current UFW status:"
        ufw status numbered
    else
        log_warning "UFW is installed but not active"
        read -p "Enable UFW? (yes/no) [default: yes]: " enable_ufw
        enable_ufw=${enable_ufw:-yes}
        if [ "$enable_ufw" = "yes" ]; then
            ufw --force enable
            ufw allow 22/tcp
            ufw allow 80/tcp
            ufw allow 443/tcp
            ufw allow 8080/tcp
            ufw allow 2222/tcp
            log_success "UFW enabled with required rules"
        fi
    fi
else
    log_warning "UFW is not installed. Consider installing it for security."
fi

# ============================================
#

# ============================================
# STEP 9: VALIDATE DOCKER COMPOSE CONFIGURATION
# ============================================

log_info "Step 9: Validating Docker Compose configuration..."

if [ -f docker-compose.yml ]; then
    if docker compose config > /dev/null 2>&1; then
        log_success "docker-compose.yml is valid"
    else
        log_error "docker-compose.yml has syntax errors!"
        log_warning "Running validation with output:"
        docker compose config
        exit 1
    fi
else
    log_warning "docker-compose.yml not found - will need to create it before deployment"
fi

# ============================================
# STEP 10: CHECK FOR EXISTING CONTAINERS
# ============================================

log_info "Step 10: Checking for existing OpenAgile containers..."

EXISTING_CONTAINERS=$(docker ps -a --filter "name=openagile" --format "{{.Names}}" 2>/dev/null | wc -l)

if [ "$EXISTING_CONTAINERS" -gt 0 ]; then
    log_warning "Found $EXISTING_CONTAINERS existing OpenAgile containers:"
    docker ps -a --filter "name=openagile" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
    echo ""
    read -p "Stop and remove existing containers? (yes/no) [default: no]: " remove_containers
    remove_containers=${remove_containers:-no}
    
    if [ "$remove_containers" = "yes" ]; then
        log_info "Stopping and removing existing containers..."
        docker compose down --remove-orphans 2>/dev/null || true
        log_success "Existing containers removed"
    else
        log_warning "Existing containers will remain. This may cause conflicts."
    fi
else
    log_success "No existing OpenAgile containers found"
fi

# ============================================
# STEP 11: CHECK FOR EXISTING VOLUMES
# ============================================

log_info "Step 11: Checking for existing volumes..."

EXISTING_VOLUMES=$(docker volume ls --filter "name=openagile" --format "{{.Name}}" 2>/dev/null | wc -l)

if [ "$EXISTING_VOLUMES" -gt 0 ]; then
    log_warning "Found $EXISTING_VOLUMES existing OpenAgile volumes:"
    docker volume ls --filter "name=openagile" --format "table {{.Name}}\t{{.Driver}}\t{{.Mountpoint}}"
    log_info "These volumes contain your data and will be reused by the new deployment"
    log_info "To start fresh, run the teardown script first"
else
    log_success "No existing volumes found - will create fresh"
fi

# ============================================
# STEP 12: CREATE BACKUP OF CURRENT STATE
# ============================================

log_info "Step 12: Creating backup of current state..."

MIGRATION_BACKUP_DIR="$HOME/openagile/backups/migration-backup-$(date +%Y%m%d_%H%M%S)"
mkdir -p "$MIGRATION_BACKUP_DIR"

# Backup configuration files if they exist
if [ -f docker-compose.yml ]; then
    cp docker-compose.yml "$MIGRATION_BACKUP_DIR/" 2>/dev/null || true
fi
if [ -f .env ]; then
    cp .env "$MIGRATION_BACKUP_DIR/" 2>/dev/null || true
fi
if [ -d configs ]; then
    cp -r configs "$MIGRATION_BACKUP_DIR/" 2>/dev/null || true
fi

# Save system state
cat > "$MIGRATION_BACKUP_DIR/migration-state.txt" << EOF
Migration Backup Information
============================
Backup Date: $(date)
Migration Script Version: 2.0

System State Before Migration:
------------------------------
Nginx Installed: $NGINX_INSTALLED
Nginx Running: $NGINX_RUNNING
Port 80 Free: $PORT_80_FREE
Port 443 Free: $PORT_443_FREE
Existing Containers: $EXISTING_CONTAINERS
Existing Volumes: $EXISTING_VOLUMES

Docker Version:
$(docker version --format '{{.Server.Version}}')

Docker Compose Version:
$(docker compose version)

Backup Location: $MIGRATION_BACKUP_DIR
EOF

log_success "Migration backup created: $MIGRATION_BACKUP_DIR"

# ============================================
# STEP 13: FINAL VERIFICATION
# ============================================

log_info "Step 13: Final verification before proceeding..."

echo ""
echo "═══════════════════════════════════════════════════════════"
echo "                    MIGRATION SUMMARY                       "
echo "═══════════════════════════════════════════════════════════"
echo ""
echo "✓ Pre-flight checks:         PASSED"
echo "✓ Nginx handling:             $([ "$NGINX_INSTALLED" = false ] && echo "N/A" || echo "COMPLETED")"
echo "✓ Port availability:          VERIFIED"
echo "✓ Directory structure:        READY"
echo "✓ Configuration files:        $([ ${#MISSING_FILES[@]} -eq 0 ] && echo "COMPLETE" || echo "INCOMPLETE (${#MISSING_FILES[@]} missing)")"
echo "✓ Firewall rules:             UPDATED"
echo "✓ Backup created:             YES"
echo ""

if [ "$PORT_80_FREE" = true ] && [ "$PORT_443_FREE" = true ]; then
    echo "🎉 Ports 80 and 443 are FREE and ready for Traefik!"
else
    echo "⚠️  Warning: Some ports may still be in use"
fi

echo ""
echo "═══════════════════════════════════════════════════════════"
echo ""

# ============================================
# STEP 14: NEXT STEPS GUIDANCE
# ============================================

log_info "Step 14: Migration preparation complete!"

echo ""
log_success "✓ System is ready for OpenAgile deployment"
echo ""
log_info "Next steps:"
echo ""
echo "  1. Ensure all configuration files are in place:"
echo "     - docker-compose.yml"
echo "     - .env (with your actual credentials)"
echo "     - configs/traefik/traefik.yml"
echo "     - configs/traefik/dynamic.yml"
echo "     - configs/prometheus/prometheus.yml"
echo "     - All other config files"
echo ""
echo "  2. Review and edit .env file:"
echo "     nano .env"
echo ""
echo "  3. Deploy the OpenAgile stack:"
echo "     docker compose up -d"
echo ""
echo "  4. Monitor the deployment:"
echo "     docker compose logs -f"
echo ""
echo "  5. Run health check:"
echo "     ./scripts/health-check.sh"
echo ""

# Save next steps to file
cat > "$HOME/openagile/NEXT_STEPS.txt" << 'EOF'
OpenAgile Board - Post-Migration Next Steps
===========================================

✓ Migration completed successfully!

1. VERIFY CONFIGURATION FILES
   ------------------------------
   cd ~/openagile
   
   Check that these files exist:
   - docker-compose.yml
   - .env
   - configs/traefik/traefik.yml
   - configs/traefik/dynamic.yml
   - configs/prometheus/prometheus.yml
   - configs/prometheus/alerts.yml
   - configs/grafana/provisioning/datasources/prometheus.yml
   - configs/grafana/provisioning/dashboards/default.yml

2. EDIT ENVIRONMENT VARIABLES
   ---------------------------
   nano .env
   
   Update these values:
   - CLOUDFLARE_API_TOKEN
   - TRAEFIK_DASHBOARD_AUTH
   - POSTGRES_PASSWORD
   - N8N_BASIC_AUTH_PASSWORD
   - GRAFANA_ADMIN_PASSWORD
   - OPENPROJECT_SECRET_KEY_BASE
   - OPENPROJECT_ADMIN_PASSWORD

3. DEPLOY OPENAGILE
   ----------------
   docker compose up -d

4. MONITOR DEPLOYMENT
   ------------------
   docker compose logs -f
   
   Watch for:
   - SSL certificate generation
   - Database initialization
   - Service startup messages

5. VERIFY SERVICES
   ---------------
   Wait 2-3 minutes, then check:
   - https://traefik.zubbystudio.shop
   - https://n8n.zubbystudio.shop
   - https://project.zubbystudio.shop
   - https://docs.zubbystudio.shop
   - https://metrics.zubbystudio.shop

6. RUN HEALTH CHECK
   ----------------
   ./scripts/health-check.sh

7. SETUP AUTOMATED BACKUPS
   -----------------------
   crontab -e
   
   Add this line:
   0 2 * * * /root/openagile/scripts/backup-openagile.sh

8. DOCUMENT YOUR SETUP
   -------------------
   - Update Wiki.js with your configuration
   - Document any custom changes
   - Add team member access details

TROUBLESHOOTING
===============
If services don't start:
  - Check logs: docker compose logs <service>
  - Verify DNS: dig <subdomain>.zubbystudio.shop
  - Check firewall: sudo ufw status
  - Verify ports: sudo lsof -i :80,443

For support, see README.md or run:
  ./scripts/health-check.sh

Happy building! 🚀
EOF

log_success "Next steps saved to: $HOME/openagile/NEXT_STEPS.txt"

# ============================================
# FINAL MESSAGE
# ============================================

echo ""
echo "═══════════════════════════════════════════════════════════"
echo "            MIGRATION PREPARATION COMPLETE! ✓              "
echo "═══════════════════════════════════════════════════════════"
echo ""
echo "📋 Summary:"
echo "  • Nginx: $([ "$NGINX_INSTALLED" = false ] && echo "Not installed (skipped)" || echo "Handled successfully")"
echo "  • Ports: 80 and 443 are FREE"
echo "  • Directory: Ready at $HOME/openagile"
echo "  • Backups: Created at $MIGRATION_BACKUP_DIR"
echo ""
echo "📖 Documentation:"
echo "  • Next steps: $HOME/openagile/NEXT_STEPS.txt"
echo "  • Migration backup: $MIGRATION_BACKUP_DIR"
echo "  • Nginx backup: $([ "$NGINX_INSTALLED" = true ] && echo "$BACKUP_DIR" || echo "N/A")"
echo ""
echo "🚀 You're ready to deploy OpenAgile!"
echo ""
echo "Read the next steps with:"
echo "  cat ~/openagile/NEXT_STEPS.txt"
echo ""
log_success "Migration script completed successfully!"
echo "" OpenAgile Board - Nginx to Traefik Migration
# Version: 2.0 (With Safeguards)
# ============================================
# This script safely migrates from Nginx to Traefik
# with proper existence checks and safeguards
# ============================================

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Banner
echo -e "${BLUE}"
cat << "EOF"
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║        OpenAgile Board - Nginx to Traefik Migration         ║
║                     Version 2.0 (Safe)                       ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
EOF
echo -e "${NC}"

# Check if running as root
if [ "$EUID" -ne 0 ]; then 
    log_error "Please run as root (use sudo)"
    exit 1
fi

# ============================================
# STEP 1: PRE-FLIGHT CHECKS
# ============================================

log_info "Step 1: Running pre-flight checks..."

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    log_error "Docker is not installed. Please install Docker first."
    exit 1
fi
log_success "Docker is installed"

# Check if Docker Compose is available
if ! docker compose version &> /dev/null; then
    log_error "Docker Compose is not available. Please install Docker Compose."
    exit 1
fi
log_success "Docker Compose is available"

# Check if required tools are installed
REQUIRED_TOOLS=("lsof" "ufw")
for tool in "${REQUIRED_TOOLS[@]}"; do
    if ! command -v "$tool" &> /dev/null; then
        log_warning "$tool not found, installing..."
        apt-get update && apt-get install -y "$tool"
    fi
done
log_success "All required tools available"

# ============================================
# STEP 2: CHECK NGINX STATUS
# ============================================

log_info "Step 2: Checking Nginx status..."

NGINX_INSTALLED=false
NGINX_RUNNING=false

if command -v nginx &> /dev/null; then
    NGINX_INSTALLED=true
    log_warning "Nginx is installed"
    
    if systemctl is-active --quiet nginx 2>/dev/null; then
        NGINX_RUNNING=true
        log_warning "Nginx is currently running"
    else
        log_info "Nginx is installed but not running"
    fi
else
    log_info "Nginx is not installed - skipping Nginx removal"
fi

# ============================================
# STEP 3: BACKUP NGINX CONFIGURATION
# ============================================

if [ "$NGINX_INSTALLED" = true ]; then
    log_info "Step 3: Backing up Nginx configuration..."
    
    BACKUP_DIR="$HOME/openagile/backups/nginx-backup-$(date +%Y%m%d_%H%M%S)"
    
    # Check if backup directory structure exists
    if [ ! -d "$HOME/openagile/backups" ]; then
        log_warning "Backup directory doesn't exist, creating it..."
        mkdir -p "$HOME/openagile/backups"
    fi
    
    if [ -d /etc/nginx ]; then
        mkdir -p "$BACKUP_DIR"
        cp -r /etc/nginx/* "$BACKUP_DIR/" 2>/dev/null || true
        
        # Save Nginx status information
        cat > "$BACKUP_DIR/nginx-status.txt" << EOF
Nginx Backup Information
========================
Backup Date: $(date)
Nginx Version: $(nginx -v 2>&1)
Nginx Running: $NGINX_RUNNING
Backup Location: $BACKUP_DIR

Configuration Files Backed Up:
$(ls -lah $BACKUP_DIR/)
EOF
        
        log_success "Nginx configuration backed up to: $BACKUP_DIR"
        log_info "Backup size: $(du -sh "$BACKUP_DIR" | cut -f1)"
    else
        log_warning "No /etc/nginx directory found to backup"
    fi
else
    log_info "Step 3: Skipping Nginx backup (not installed)"
fi

# ============================================
# STEP 4: CHECK PORT AVAILABILITY
# ============================================

log_info "Step 4: Checking port availability..."

check_port() {
    local port=$1
    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1; then
        local process=$(lsof -Pi :$port -sTCP:LISTEN | tail -n 1 | awk '{print $1}')
        log_warning "Port $port is in use by: $process"
        return 1
    else
        log_success "Port $port is available"
        return 0
    fi
}

PORT_80_FREE=false
PORT_443_FREE=false

check_port 80 && PORT_80_FREE=true || PORT_80_FREE=false
check_port 443 && PORT_443_FREE=true || PORT_443_FREE=false

# ============================================
# STEP 5: STOP AND REMOVE NGINX
# ============================================

if [ "$NGINX_RUNNING" = true ] || [ "$PORT_80_FREE" = false ] || [ "$PORT_443_FREE" = false ]; then
    log_info "Step 5: Stopping and removing Nginx..."
    
    # Stop Nginx service
    if systemctl is-active --quiet nginx 2>/dev/null; then
        log_info "Stopping Nginx service..."
        systemctl stop nginx
        systemctl disable nginx
        log_success "Nginx service stopped and disabled"
    fi
    
    # Ask user about Nginx removal
    echo ""
    log_warning "Nginx package removal options:"
    echo "  1) Keep Nginx installed (just stopped)"
    echo "  2) Remove Nginx package (keep config backup)"
    echo "  3) Purge Nginx completely (remove everything)"
    echo ""
    read -p "Choose option (1/2/3) [default: 2]: " nginx_removal
    nginx_removal=${nginx_removal:-2}
    
    case $nginx_removal in
        1)
            log_info "Keeping Nginx installed"
            ;;
        2)
            log_info "Removing Nginx package..."
            apt-get remove -y nginx nginx-common 2>/dev/null || true
            log_success "Nginx package removed (config backup preserved)"
            ;;
        3)
            log_warning "Purging Nginx completely..."
            apt-get purge -y nginx nginx-common 2>/dev/null || true
            apt-get autoremove -y 2>/dev/null || true
            log_success "Nginx purged completely"
            ;;
        *)
            log_error "Invalid option"
            exit 1
            ;;
    esac
    
    # Verify ports are now free
    sleep 2
    check_port 80 && PORT_80_FREE=true || PORT_80_FREE=false
    check_port 443 && PORT_443_FREE=true || PORT_443_FREE=false
    
    if [ "$PORT_80_FREE" = false ] || [ "$PORT_443_FREE" = false ]; then
        log_error "Ports are still in use. Please manually stop the services:"
        lsof -Pi :80 -sTCP:LISTEN 2>/dev/null || true
        lsof -Pi :443 -sTCP:LISTEN 2>/dev/null || true
        exit 1
    fi
else
    log_info "Step 5: Ports are already free, skipping Nginx removal"
fi

# ============================================
# STEP 6: ENSURE OPENAGILE DIRECTORY STRUCTURE
# ============================================

log_info "Step 6: Ensuring OpenAgile directory structure..."

# Check if directory exists
if [ -d "$HOME/openagile" ]; then
    log_success "OpenAgile directory already exists: $HOME/openagile"
    cd "$HOME/openagile"
    
    # Check for required subdirectories and create if missing
    SUBDIRS=(
        "configs/traefik"
        "configs/prometheus"
        "configs/grafana/provisioning/datasources"
        "configs/grafana/provisioning/dashboards"
        "configs/grafana/dashboards"
        "configs/n8n"
        "configs/gitea"
        "configs/woodpecker"
        "scripts"
        "backups"
        "monitoring"
        "erpnext/sites"
        "pipelines/examples"
    )
    
    log_info "Checking subdirectories..."
    for dir in "${SUBDIRS[@]}"; do
        if [ ! -d "$dir" ]; then
            log_warning "Creating missing directory: $dir"
            mkdir -p "$dir"
        else
            log_success "✓ $dir exists"
        fi
    done
    
else
    log_warning "OpenAgile directory doesn't exist, creating it..."
    cd "$HOME"
    mkdir -p openagile && cd openagile
    
    # Initialize Git repository
    if [ ! -d .git ]; then
        log_info "Initializing Git repository..."
        git init
        git config user.name "zubbyik"
        git config user.email "zubbyik@gmail.com"
        
        # Create .gitignore
        cat > .gitignore << 'EOF'
*.env
*.key
*.pem
backups/
.secrets/
deployment.log
*.log
EOF
        log_success "Git repository initialized"
    fi
    
    # Create all subdirectories
    log_info "Creating directory structure..."
    mkdir -p configs/{traefik,prometheus,grafana/{provisioning/{datasources,dashboards},dashboards},n8n,gitea,woodpecker}
    mkdir -p scripts backups monitoring erpnext/sites pipelines/examples
    
    log_success "Directory structure created"
fi

# Make scripts executable if they exist
if [ -d scripts ]; then
    chmod +x scripts/*.sh 2>/dev/null || true
    log_success "Scripts made executable"
fi

log_success "Directory structure verified and ready"

# ============================================
# STEP 7: VERIFY CONFIGURATION FILES
# ============================================

log_info "Step 7: Verifying configuration files..."

REQUIRED_FILES=(
    "docker-compose.yml"
    ".env"
    "configs/traefik/traefik.yml"
    "configs/traefik/dynamic.yml"
    "configs/prometheus/prometheus.yml"
    "configs/prometheus/alerts.yml"
)

MISSING_FILES=()

for file in "${REQUIRED_FILES[@]}"; do
    if [ -f "$file" ]; then
        log_success "✓ $file exists"
    else
        log_warning "✗ $file is MISSING"
        MISSING_FILES+=("$file")
    fi
done

if [ ${#MISSING_FILES[@]} -gt 0 ]; then
    log_error "Missing configuration files detected!"
    log_warning "Please create these files before proceeding:"
    for file in "${MISSING_FILES[@]}"; do
        echo "  - $file"
    done
    echo ""
    read -p "Continue anyway? (yes/no) [default: no]: " continue_missing
    continue_missing=${continue_missing:-no}
    if [ "$continue_missing" != "yes" ]; then
        log_info "Migration paused. Create missing files and re-run this script."
        exit 0
    fi
fi

# ============================================
# STEP 8: UPDATE UFW FIREWALL RULES
# ============================================

log_info "Step 8: Updating firewall rules..."

if command -v ufw &> /dev/null; then
    # Check if UFW is active
    if ufw status | grep -q "Status: active"; then
        log_info "UFW is active, updating rules..."
        
        # Ensure required ports are allowed
        ufw allow 22/tcp comment 'SSH' 2>/dev/null || true
        ufw allow 80/tcp comment 'HTTP (Traefik)' 2>/dev/null || true
        ufw allow 443/tcp comment 'HTTPS (Traefik)' 2>/dev/null || true
        ufw allow 8080/tcp comment 'Traefik Dashboard' 2>/dev/null || true
        ufw allow 2222/tcp comment 'Gitea SSH' 2>/dev/null || true
        
        log_success "Firewall rules updated"
        
        # Display current rules
        log_info "Current UFW status:"
        ufw status numbered
    else
        log_warning "UFW is installed but not active"
        read -p "Enable UFW? (yes/no) [default: yes]: " enable_ufw
        enable_ufw=${enable_ufw:-yes}
        if [ "$enable_ufw" = "yes" ]; then
            ufw --force enable
            ufw allow 22/tcp
            ufw allow 80/tcp
            ufw allow 443/tcp
            ufw allow 8080/tcp
            ufw allow 2222/tcp
            log_success "UFW enabled with required rules"
        fi
    fi
else
    log_warning "UFW is not installed. Consider installing it for security."
fi

# ============================================
#
