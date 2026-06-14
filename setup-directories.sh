#!/bin/bash

# ============================================
# OpenAgile Board - Directory Setup Script
# ============================================
# This standalone script creates all required
# directories for OpenAgile Board
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
echo ""
echo "═══════════════════════════════════════════════════════════"
echo "   OpenAgile Board - Directory Structure Setup"
echo "═══════════════════════════════════════════════════════════"
echo ""

# Configuration
OPENAGILE_DIR="${HOME}/openagile"

# Check if directory exists
if [ ! -d "$OPENAGILE_DIR" ]; then
    log_warning "OpenAgile directory does not exist"
    read -p "Create $OPENAGILE_DIR? (yes/no) [default: yes]: " create_dir
    create_dir=${create_dir:-yes}
    
    if [ "$create_dir" = "yes" ]; then
        mkdir -p "$OPENAGILE_DIR"
        log_success "Created: $OPENAGILE_DIR"
    else
        log_error "Cannot continue without base directory"
        exit 1
    fi
fi

# Change to openagile directory
cd "$OPENAGILE_DIR" || {
    log_error "Failed to change to $OPENAGILE_DIR"
    exit 1
}

log_info "Working in: $(pwd)"
echo ""

# Define all subdirectories
log_info "Setting up directory structure..."
echo ""

# Main directories
declare -A DIRECTORY_STRUCTURE=(
    # Configs
    ["configs"]="Main configuration directory"
    ["configs/traefik"]="Traefik reverse proxy configuration"
    ["configs/prometheus"]="Prometheus monitoring configuration"
    ["configs/grafana"]="Grafana dashboards and settings"
    ["configs/grafana/provisioning"]="Grafana auto-provisioning"
    ["configs/grafana/provisioning/datasources"]="Grafana datasource configs"
    ["configs/grafana/provisioning/dashboards"]="Grafana dashboard providers"
    ["configs/grafana/dashboards"]="Dashboard JSON files"
    ["configs/n8n"]="n8n automation configuration"
    ["configs/gitea"]="Gitea version control configuration"
    ["configs/woodpecker"]="Woodpecker CI/CD configuration"
    
    # Scripts
    ["scripts"]="Automation and maintenance scripts"
    
    # Backups
    ["backups"]="Automated backup storage"
    
    # Monitoring
    ["monitoring"]="Custom monitoring scripts and configs"
    
    # ERPNext
    ["erpnext"]="ERPNext business management"
    ["erpnext/sites"]="ERPNext site data"
    
    # CI/CD Pipelines
    ["pipelines"]="CI/CD pipeline definitions"
    ["pipelines/examples"]="Example pipeline configurations"
)

# Sort directories by depth to create parent before child
SORTED_DIRS=($(for dir in "${!DIRECTORY_STRUCTURE[@]}"; do echo "$dir"; done | sort))

CREATED=0
EXISTS=0
FAILED=0

for dir in "${SORTED_DIRS[@]}"; do
    description="${DIRECTORY_STRUCTURE[$dir]}"
    
    if [ -d "$dir" ]; then
        echo -e "${GREEN}✓${NC} ${dir} (exists)"
        ((EXISTS++))
    else
        echo -e "${BLUE}→${NC} Creating: ${dir}"
        if mkdir -p "$dir" 2>/dev/null; then
            if [ -d "$dir" ]; then
                echo -e "${GREEN}✓${NC} ${dir} (created) - ${description}"
                ((CREATED++))
            else
                echo -e "${RED}✗${NC} ${dir} (failed to verify)"
                ((FAILED++))
            fi
        else
            echo -e "${RED}✗${NC} ${dir} (mkdir failed)"
            ((FAILED++))
        fi
    fi
done

echo ""
echo "═══════════════════════════════════════════════════════════"
echo "                    Summary"
echo "═══════════════════════════════════════════════════════════"
echo ""
echo "Total directories: ${#SORTED_DIRS[@]}"
echo "  Created: $CREATED"
echo "  Already existed: $EXISTS"
echo "  Failed: $FAILED"
echo ""

# Create .gitignore if it doesn't exist
if [ ! -f .gitignore ]; then
    log_info "Creating .gitignore..."
    cat > .gitignore << 'EOF'
# Secrets and sensitive files
*.env
.env.*
*.key
*.pem
.secrets/

# Logs and temporary files
*.log
deployment.log
*.tmp
*.swp
*~

# Backups
backups/

# OS files
.DS_Store
Thumbs.db

# IDE files
.vscode/
.idea/
*.iml

# Docker override files
docker-compose.override.yml
EOF
    log_success "Created .gitignore"
else
    log_success ".gitignore already exists"
fi

# Initialize git if not already done
if [ ! -d .git ]; then
    log_info "Initializing Git repository..."
    git init
    git config user.name "zubbyik"
    git config user.email "zubbyik@gmail.com"
    log_success "Git repository initialized"
else
    log_success "Git repository already exists"
fi

# Verify structure
echo ""
log_info "Verifying directory structure..."
echo ""

# Display tree-like structure
if command -v tree &> /dev/null; then
    tree -L 3 -d --dirsfirst
else
    log_info "Directory listing (install 'tree' command for better visualization):"
    find . -type d -not -path '*/\.*' | sort | sed 's|^./||' | sed 's|[^/]*/|  |g'
fi

echo ""
echo "═══════════════════════════════════════════════════════════"

if [ $FAILED -eq 0 ]; then
    log_success "✓ Directory structure setup complete!"
    echo ""
    echo "Next steps:"
    echo "  1. Create configuration files in configs/"
    echo "  2. Place scripts in scripts/"
    echo "  3. Create docker-compose.yml in root"
    echo "  4. Create .env file with credentials"
    echo ""
    echo "Location: $OPENAGILE_DIR"
else
    log_error "✗ Some directories failed to create"
    log_warning "Please check permissions and try again"
    exit 1
fi

echo "═══════════════════════════════════════════════════════════"
echo ""

# Check for required files
echo ""
log_info "Checking for required files..."
echo ""

REQUIRED_FILES=(
    "docker-compose.yml"
    ".env"
    "configs/traefik/traefik.yml"
    "configs/traefik/dynamic.yml"
    "configs/prometheus/prometheus.yml"
)

MISSING_FILES=()

for file in "${REQUIRED_FILES[@]}"; do
    if [ -f "$file" ]; then
        echo -e "${GREEN}✓${NC} $file"
    else
        echo -e "${YELLOW}✗${NC} $file (missing)"
        MISSING_FILES+=("$file")
    fi
done

if [ ${#MISSING_FILES[@]} -gt 0 ]; then
    echo ""
    log_warning "Missing ${#MISSING_FILES[@]} configuration files"
    echo "Create these files before running deployment"
else
    echo ""
    log_success "All required files present!"
fi

echo ""
log_success "Setup script completed!"
echo ""
