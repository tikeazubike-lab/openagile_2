#!/bin/bash
# scripts/backup-openagile.sh
# Comprehensive backup script for OpenAgile Board

set -e

# Configuration
BACKUP_ROOT=~/openagile/backups
RETENTION_DAYS=${BACKUP_RETENTION_DAYS:-30}
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="$BACKUP_ROOT/$TIMESTAMP"

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${YELLOW}=========================================${NC}"
echo -e "${YELLOW}OpenAgile Backup - $(date)${NC}"
echo -e "${YELLOW}=========================================${NC}"

# Create backup directory
mkdir -p "$BACKUP_DIR"/{volumes,configs,database}

# Function to backup Docker volume
backup_volume() {
    local volume_name=$1
    local backup_file=$2
    
    echo -e "${YELLOW}Backing up volume: $volume_name${NC}"
    docker run --rm \
        -v ${volume_name}:/data \
        -v ${BACKUP_DIR}/volumes:/backup \
        alpine tar czf /backup/${backup_file} -C /data .
    
    echo -e "${GREEN}✓ $volume_name backed up${NC}"
}

# Function to backup database
backup_database() {
    local db_name=$1
    
    echo -e "${YELLOW}Backing up database: $db_name${NC}"
    docker compose exec -T postgres pg_dump -U openagile $db_name | gzip > "$BACKUP_DIR/database/${db_name}.sql.gz"
    echo -e "${GREEN}✓ Database $db_name backed up${NC}"
}

# Backup all Docker volumes
echo -e "${YELLOW}Step 1: Backing up Docker volumes...${NC}"
backup_volume "openagile_postgres_data" "postgres_data.tar.gz"
backup_volume "openagile_n8n_data" "n8n_data.tar.gz"
backup_volume "openagile_wikijs_data" "wikijs_data.tar.gz"
backup_volume "openagile_openproject_pgdata" "openproject_pgdata.tar.gz"
backup_volume "openagile_openproject_assets" "openproject_assets.tar.gz"
backup_volume "openagile_prometheus_data" "prometheus_data.tar.gz"
backup_volume "openagile_grafana_data" "grafana_data.tar.gz"
backup_volume "openagile_traefik_certs" "traefik_certs.tar.gz"

# Backup databases individually
echo -e "${YELLOW}Step 2: Backing up databases...${NC}"
backup_database "openagile"
backup_database "n8n"
backup_database "wikijs"
backup_database "openproject"

# Backup configuration files
echo -e "${YELLOW}Step 3: Backing up configurations...${NC}"
cd ~/openagile
tar czf "$BACKUP_DIR/configs/openagile_configs.tar.gz" \
    configs/ \
    docker-compose.yml \
    .env 2>/dev/null || true

echo -e "${GREEN}✓ Configurations backed up${NC}"

# Backup scripts
echo -e "${YELLOW}Step 4: Backing up scripts...${NC}"
tar czf "$BACKUP_DIR/configs/scripts.tar.gz" scripts/
echo -e "${GREEN}✓ Scripts backed up${NC}"

# Create backup manifest
echo -e "${YELLOW}Step 5: Creating backup manifest...${NC}"
cat > "$BACKUP_DIR/manifest.txt" << EOF
OpenAgile Backup Manifest
========================
Backup Date: $(date)
Backup Location: $BACKUP_DIR

Volumes:
$(ls -lh $BACKUP_DIR/volumes/)

Databases:
$(ls -lh $BACKUP_DIR/database/)

Configs:
$(ls -lh $BACKUP_DIR/configs/)

Total Size: $(du -sh $BACKUP_DIR | cut -f1)
EOF

echo -e "${GREEN}✓ Manifest created${NC}"

# Cleanup old backups
echo -e "${YELLOW}Step 6: Cleaning up old backups (older than $RETENTION_DAYS days)...${NC}"
find "$BACKUP_ROOT" -maxdepth 1 -type d -mtime +$RETENTION_DAYS -exec rm -rf {} \; 2>/dev/null || true
echo -e "${GREEN}✓ Old backups cleaned${NC}"

# Calculate backup size
BACKUP_SIZE=$(du -sh "$BACKUP_DIR" | cut -f1)

# Summary
echo -e "${GREEN}=========================================${NC}"
echo -e "${GREEN}Backup Complete!${NC}"
echo -e "${GREEN}=========================================${NC}"
echo "Location: $BACKUP_DIR"
echo "Size: $BACKUP_SIZE"
echo "Retention: $RETENTION_DAYS days"
echo
echo "Backup contents:"
cat "$BACKUP_DIR/manifest.txt"
echo
echo -e "${YELLOW}To restore from this backup, run:${NC}"
echo "  ~/openagile/scripts/restore-openagile.sh $TIMESTAMP"
