---
type: OB
id: OPENAGILE-SETUP-GUIDE
title: OpenAgile Board Complete Setup Guide
status: ARCHIVAL_REFERENCE
version: 1.0
updated: 2026-05-23
---

# 🚀 OpenAgile Board - Complete Setup Guide

> A comprehensive, step-by-step guide to deploy the OpenAgile self-hosted DevOps platform from scratch.

---

## 📚 Table of Contents

1. [Prerequisites](#prerequisites)
2. [Server Preparation](#server-preparation)
3. [Project Structure Setup](#project-structure-setup)
4. [Environment Configuration](#environment-configuration)
5. [Cloudflare DNS Setup](#cloudflare-dns-setup)
6. [Main Stack Deployment](#main-stack-deployment)
7. [Frappe/ERPNext Stack Deployment](#frappeerrnext-stack-deployment)
8. [Service Configuration](#service-configuration)
9. [Post-Deployment Verification](#post-deployment-verification)
10. [Maintenance & Operations](#maintenance--operations)
11. [Troubleshooting](#troubleshooting)

---

## Prerequisites

### Hardware Requirements

| Resource | Minimum | Recommended |
|----------|---------|-------------|
| **CPU** | 4 vCPU | 8 vCPU |
| **RAM** | 8 GB | 16 GB |
| **Storage** | 100 GB SSD | 500 GB SSD |
| **Network** | 100 Mbps | 1 Gbps |

### Software Requirements

- **Operating System**: Ubuntu 22.04 LTS (or compatible Linux distribution)
- **Docker**: v24.0+ with Docker Compose v2.20+
- **Git**: v2.30+
- **Domain**: A registered domain with DNS management access
- **Cloudflare Account**: For DNS and SSL certificate management

### Required Accounts & API Keys

| Service | Purpose | How to Obtain |
|---------|---------|---------------|
| **Cloudflare** | DNS management & SSL certificates | https://cloudflare.com |
| **Docker Hub** | Container image pulls | https://hub.docker.com (optional) |

---

## Server Preparation

### Step 1: Update System

```bash
sudo apt update && sudo apt upgrade -y
sudo apt install -y curl wget git vim ufw fail2ban
```

### Step 2: Install Docker

```bash
# Install Docker using official script
curl -fsSL https://get.docker.com | sh

# Add current user to docker group
sudo usermod -aG docker $USER

# Apply group changes (or log out and back in)
newgrp docker

# Verify installation
docker --version
docker compose version
```

### Step 3: Configure Firewall

```bash
# Enable UFW
sudo ufw --force enable

# Allow SSH
sudo ufw allow 22/tcp

# Allow HTTP/HTTPS
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp

# Allow Traefik Dashboard (optional, for debugging)
sudo ufw allow 8080/tcp

# Allow Git SSH (for Gitea)
sudo ufw allow 2222/tcp

# Verify rules
sudo ufw status
```

### Step 4: Configure Fail2ban

```bash
# Enable fail2ban
sudo systemctl enable fail2ban
sudo systemctl start fail2ban
```

### Step 5: Set System Timezone

```bash
sudo timedatectl set-timezone Africa/Lagos  # Adjust to your timezone
```

---

## Project Structure Setup

### Step 1: Create Project Directory

```bash
# Create project root
mkdir -p ~/openagile
cd ~/openagile

# Create directory structure
mkdir -p configs/{traefik/dynamic,prometheus,grafana/provisioning/datasources,grafana/provisioning/dashboards,grafana/dashboards,n8n,openproject}
mkdir -p scripts
mkdir -p backups
```

### Step 2: Create Main docker-compose.yml

Create the file `~/openagile/docker-compose.yml`:

```yaml
networks:
  openagile_network:
    driver: bridge
  traefik_public:
    external: false

volumes:
  traefik_letsencrypt:
  postgres_data:
  n8n_data:
  wikijs_data:
  openproject_pgdata:
  openproject_assets:
  prometheus_data:
  grafana_data:
  portainer_data:
  gitea_data:
  woodpecker_server_data:

services:
  # ============================================
  # TRAEFIK - Reverse Proxy & SSL Management
  # ============================================
  traefik:
    image: traefik:v2.10
    container_name: traefik
    restart: unless-stopped
    security_opt:
      - no-new-privileges:true
    networks:
      - openagile_network
    ports:
      - "80:80"
      - "443:443"
      - "8080:8080"  # Dashboard
      - "8082:8082"  # Metrics
    environment:
      - CF_API_EMAIL=${CLOUDFLARE_EMAIL}
      - CF_DNS_API_TOKEN=${CLOUDFLARE_API_TOKEN}
      - TZ=Africa/Lagos
    volumes:
      - /etc/localtime:/etc/localtime:ro
      - /var/run/docker.sock:/var/run/docker.sock:ro
      - traefik_letsencrypt:/letsencrypt
      - ./configs/traefik/traefik.yml:/etc/traefik/traefik.yml:ro
      - ./configs/traefik/dynamic:/etc/traefik/dynamic:ro
    labels:
      - "traefik.enable=true"
      - "traefik.http.routers.traefik.rule=Host(`traefik.${DOMAIN}`)"
      - "traefik.http.routers.traefik.entrypoints=websecure"
      - "traefik.http.routers.traefik.tls=true"
      - "traefik.http.routers.traefik.tls.certresolver=cloudflare"
      - "traefik.http.routers.traefik.service=api@internal"
      - "traefik.http.routers.traefik.middlewares=traefik-auth@file"

  # ============================================
  # PORTAINER - Container Management
  # ============================================
  portainer:
    image: portainer/portainer-ce:latest
    container_name: portainer
    restart: unless-stopped
    networks:
      - openagile_network
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock
      - portainer_data:/data
    labels:
      - "traefik.enable=true"
      - "traefik.http.routers.portainer.rule=Host(`portainer.${DOMAIN}`)"
      - "traefik.http.routers.portainer.entrypoints=websecure"
      - "traefik.http.routers.portainer.tls=true"
      - "traefik.http.routers.portainer.tls.certresolver=cloudflare"
      - "traefik.http.services.portainer.loadbalancer.server.port=9000"
      - "traefik.http.routers.portainer.middlewares=security-headers@file"
    deploy:
      resources:
        limits:
          cpus: '0.5'
          memory: 512M

  # ============================================
  # POSTGRESQL - Shared Database
  # ============================================
  postgres:
    image: postgres:15-alpine
    container_name: openagile_postgres
    restart: unless-stopped
    networks:
      - openagile_network
    environment:
      POSTGRES_USER: ${POSTGRES_USER:-openagile}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
      POSTGRES_MULTIPLE_DATABASES: n8n,wikijs,openproject,gitea
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./scripts/init-databases.sh:/docker-entrypoint-initdb.d/init-databases.sh:ro
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${POSTGRES_USER:-openagile}"]
      interval: 10s
      timeout: 5s
      retries: 5
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 2G
        reservations:
          cpus: '1'
          memory: 1G

  # ============================================
  # GITEA - Git Version Control
  # ============================================
  gitea:
    image: gitea/gitea:1.21
    container_name: gitea
    restart: unless-stopped
    networks:
      - openagile_network
    environment:
      - USER_UID=1000
      - USER_GID=1000
      - GITEA__database__DB_TYPE=postgres
      - GITEA__database__HOST=postgres:5432
      - GITEA__database__NAME=gitea
      - GITEA__database__USER=${POSTGRES_USER:-openagile}
      - GITEA__database__PASSWD=${POSTGRES_PASSWORD}
      - GITEA__server__DOMAIN=git.${DOMAIN}
      - GITEA__server__SSH_DOMAIN=git.${DOMAIN}
      - GITEA__server__ROOT_URL=https://git.${DOMAIN}/
      - GITEA__server__HTTP_PORT=3000
      - GITEA__server__SSH_PORT=2222
      - GITEA__service__DISABLE_REGISTRATION=false
      - GITEA__service__REQUIRE_SIGNIN_VIEW=false
      - GITEA__webhook__ALLOWED_HOST_LIST=*
    volumes:
      - gitea_data:/data
      - /etc/timezone:/etc/timezone:ro
      - /etc/localtime:/etc/localtime:ro
    ports:
      - "2222:22"
    depends_on:
      postgres:
        condition: service_healthy
    labels:
      - "traefik.enable=true"
      - "traefik.http.routers.gitea.rule=Host(`git.${DOMAIN}`)"
      - "traefik.http.routers.gitea.entrypoints=websecure"
      - "traefik.http.routers.gitea.tls=true"
      - "traefik.http.routers.gitea.tls.certresolver=cloudflare"
      - "traefik.http.services.gitea.loadbalancer.server.port=3000"
      - "traefik.http.routers.gitea.middlewares=security-headers@file"
    deploy:
      resources:
        limits:
          cpus: '1'
          memory: 1G

  # ============================================
  # WOODPECKER SERVER - CI/CD Server
  # ============================================
  woodpecker_server:
    image: woodpeckerci/woodpecker-server:latest
    container_name: woodpecker_server
    restart: unless-stopped
    networks:
      - openagile_network
    environment:
      - WOODPECKER_OPEN=true
      - WOODPECKER_HOST=https://ci.${DOMAIN}
      - WOODPECKER_GITEA=true
      - WOODPECKER_GITEA_URL=https://git.${DOMAIN}
      - WOODPECKER_GITEA_CLIENT=${WOODPECKER_GITEA_CLIENT}
      - WOODPECKER_GITEA_SECRET=${WOODPECKER_GITEA_SECRET}
      - WOODPECKER_AGENT_SECRET=${WOODPECKER_AGENT_SECRET}
      - WOODPECKER_ADMIN=${WOODPECKER_ADMIN:-admin}
    volumes:
      - woodpecker_server_data:/var/lib/woodpecker
    depends_on:
      - gitea
    labels:
      - "traefik.enable=true"
      - "traefik.http.routers.woodpecker.rule=Host(`ci.${DOMAIN}`)"
      - "traefik.http.routers.woodpecker.entrypoints=websecure"
      - "traefik.http.routers.woodpecker.tls=true"
      - "traefik.http.routers.woodpecker.tls.certresolver=cloudflare"
      - "traefik.http.services.woodpecker.loadbalancer.server.port=8000"
      - "traefik.http.routers.woodpecker.middlewares=security-headers@file"
    deploy:
      resources:
        limits:
          cpus: '0.5'
          memory: 512M

  # ============================================
  # WOODPECKER AGENT - CI/CD Runner
  # ============================================
  woodpecker_agent:
    image: woodpeckerci/woodpecker-agent:latest
    container_name: woodpecker_agent
    restart: unless-stopped
    networks:
      - openagile_network
    environment:
      - WOODPECKER_SERVER=woodpecker_server:9000
      - WOODPECKER_AGENT_SECRET=${WOODPECKER_AGENT_SECRET}
      - WOODPECKER_MAX_WORKFLOWS=4
      - WOODPECKER_BACKEND=docker
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock
    depends_on:
      - woodpecker_server
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 1G

  # ============================================
  # CADVISOR - Container Metrics
  # ============================================
  cadvisor:
    container_name: cadvisor
    image: gcr.io/cadvisor/cadvisor:latest
    restart: unless-stopped
    volumes:
      - /:/rootfs:ro
      - /var/run:/var/run:ro
      - /sys:/sys:ro
      - /var/lib/docker/:/var/lib/docker:ro
      - /dev/disk/:/dev/disk:ro
    networks:
      - traefik_public
    privileged: true
    devices:
      - /dev/kmsg
    labels:
      - "traefik.enable=false"

  # ============================================
  # NODE EXPORTER - Host Metrics
  # ============================================
  node-exporter:
    container_name: node_exporter
    image: prom/node-exporter:latest
    restart: unless-stopped
    command:
      - '--path.rootfs=/host'
      - '--path.procfs=/host/proc'
      - '--path.sysfs=/host/sys'
      - '--collector.filesystem.mount-points-exclude=^/(sys|proc|dev|host|etc)($$|/)'
    volumes:
      - /:/host:ro,rslave
      - /proc:/host/proc:ro
      - /sys:/host/sys:ro
    networks:
      - traefik_public
    pid: host
    labels:
      - "traefik.enable=false"

  # ============================================
  # N8N - Automation Platform
  # ============================================
  n8n:
    image: n8nio/n8n:latest
    container_name: n8n
    restart: unless-stopped
    networks:
      - openagile_network
    environment:
      - N8N_HOST=n8n.${DOMAIN}
      - N8N_PORT=5678
      - N8N_PROTOCOL=https
      - NODE_ENV=production
      - WEBHOOK_URL=https://n8n.${DOMAIN}/
      - GENERIC_TIMEZONE=${TIMEZONE:-Africa/Lagos}
      - DB_TYPE=postgresdb
      - DB_POSTGRESDB_HOST=postgres
      - DB_POSTGRESDB_PORT=5432
      - DB_POSTGRESDB_DATABASE=n8n
      - DB_POSTGRESDB_USER=${POSTGRES_USER:-openagile}
      - DB_POSTGRESDB_PASSWORD=${POSTGRES_PASSWORD}
      - N8N_BASIC_AUTH_ACTIVE=true
      - N8N_BASIC_AUTH_USER=${N8N_BASIC_AUTH_USER}
      - N8N_BASIC_AUTH_PASSWORD=${N8N_BASIC_AUTH_PASSWORD}
    volumes:
      - n8n_data:/home/node/.n8n
      - ./configs/n8n:/etc/n8n
    depends_on:
      postgres:
        condition: service_healthy
    labels:
      - "traefik.enable=true"
      - "traefik.http.routers.n8n.rule=Host(`n8n.${DOMAIN}`)"
      - "traefik.http.routers.n8n.entrypoints=websecure"
      - "traefik.http.routers.n8n.tls=true"
      - "traefik.http.routers.n8n.tls.certresolver=cloudflare"
      - "traefik.http.services.n8n.loadbalancer.server.port=5678"
      - "traefik.http.routers.n8n.middlewares=security-headers@file"
    deploy:
      resources:
        limits:
          cpus: '1'
          memory: 1G

  # ============================================
  # OPENPROJECT - Project Management
  # ============================================
  openproject:
    image: openproject/openproject:14
    container_name: openproject
    restart: unless-stopped
    networks:
      - openagile_network
    environment:
      - OPENPROJECT_HOST__NAME=project.${DOMAIN}
      - OPENPROJECT_HTTPS=true
      - OPENPROJECT_DEFAULT__LANGUAGE=en
      - RAILS_CACHE_STORE=memcache
      - OPENPROJECT_CACHE__MEMCACHE__SERVER=cache:11211
      - IMAP_ENABLED=false
    volumes:
      - openproject_pgdata:/var/openproject/pgdata
      - openproject_assets:/var/openproject/assets
    depends_on:
      postgres:
        condition: service_healthy
    labels:
      - "traefik.enable=true"
      - "traefik.http.routers.openproject.rule=Host(`project.${DOMAIN}`)"
      - "traefik.http.routers.openproject.entrypoints=websecure"
      - "traefik.http.routers.openproject.tls=true"
      - "traefik.http.routers.openproject.tls.certresolver=cloudflare"
      - "traefik.http.services.openproject.loadbalancer.server.port=80"
      - "traefik.http.routers.openproject.middlewares=security-headers@file"
    deploy:
      resources:
        limits:
          cpus: '2.5'
          memory: 3G
        reservations:
          cpus: '1.5'
          memory: 2G

  # ============================================
  # WIKI.JS - Documentation Hub
  # ============================================
  wikijs:
    image: ghcr.io/requarks/wiki:2
    container_name: wikijs
    restart: unless-stopped
    networks:
      - openagile_network
    environment:
      DB_TYPE: postgres
      DB_HOST: postgres
      DB_PORT: 5432
      DB_USER: ${POSTGRES_USER:-openagile}
      DB_PASS: ${POSTGRES_PASSWORD}
      DB_NAME: wikijs
    volumes:
      - wikijs_data:/wiki/data
    depends_on:
      postgres:
        condition: service_healthy
    labels:
      - "traefik.enable=true"
      - "traefik.http.routers.wikijs.rule=Host(`docs.${DOMAIN}`)"
      - "traefik.http.routers.wikijs.entrypoints=websecure"
      - "traefik.http.routers.wikijs.tls=true"
      - "traefik.http.routers.wikijs.tls.certresolver=cloudflare"
      - "traefik.http.services.wikijs.loadbalancer.server.port=3000"
      - "traefik.http.routers.wikijs.middlewares=security-headers@file"
    deploy:
      resources:
        limits:
          cpus: '1'
          memory: 1G

  # ============================================
  # PROMETHEUS - Metrics Collection
  # ============================================
  prometheus:
    image: prom/prometheus:latest
    container_name: prometheus
    restart: unless-stopped
    networks:
      - openagile_network
      - traefik_public
    ports:
      - "9090:9090"
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--storage.tsdb.path=/prometheus'
      - '--storage.tsdb.retention.time=15d'
      - '--web.console.libraries=/usr/share/prometheus/console_libraries'
      - '--web.console.templates=/usr/share/prometheus/consoles'
    volumes:
      - prometheus_data:/prometheus
      - ./configs/prometheus/prometheus.yml:/etc/prometheus/prometheus.yml:ro
      - ./configs/prometheus/alerts.yml:/etc/prometheus/alerts.yml:ro
    deploy:
      resources:
        limits:
          cpus: '0.5'
          memory: 512M

  # ============================================
  # GRAFANA - Metrics Visualization
  # ============================================
  grafana:
    image: grafana/grafana:latest
    container_name: grafana
    restart: unless-stopped
    networks:
      - openagile_network
    environment:
      - GF_SERVER_ROOT_URL=https://metrics.${DOMAIN}
      - GF_SECURITY_ADMIN_USER=${GRAFANA_ADMIN_USER:-admin}
      - GF_SECURITY_ADMIN_PASSWORD=${GRAFANA_ADMIN_PASSWORD}
      - GF_INSTALL_PLUGINS=grafana-clock-panel,grafana-simple-json-datasource
    volumes:
      - grafana_data:/var/lib/grafana
      - ./configs/grafana/provisioning:/etc/grafana/provisioning:ro
      - ./configs/grafana/dashboards:/var/lib/grafana/dashboards:ro
    depends_on:
      - prometheus
    labels:
      - "traefik.enable=true"
      - "traefik.http.routers.grafana.rule=Host(`metrics.${DOMAIN}`)"
      - "traefik.http.routers.grafana.entrypoints=websecure"
      - "traefik.http.routers.grafana.tls=true"
      - "traefik.http.routers.grafana.tls.certresolver=cloudflare"
      - "traefik.http.services.grafana.loadbalancer.server.port=3000"
      - "traefik.http.routers.grafana.middlewares=security-headers@file"
    deploy:
      resources:
        limits:
          cpus: '0.5'
          memory: 512M

  # ============================================
  # CACHE - Memcached for OpenProject
  # ============================================
  cache:
    image: memcached:alpine
    container_name: openproject_cache
    restart: unless-stopped
    networks:
      - openagile_network
    deploy:
      resources:
        limits:
          cpus: '0.25'
          memory: 256M
```

---

## Configuration Files

### Traefik Static Configuration

Create `configs/traefik/traefik.yml`:

```yaml
# Static Configuration for Traefik

global:
  checkNewVersion: false
  sendAnonymousUsage: false

api:
  dashboard: true
  insecure: true

log:
  level: INFO
  format: common

accessLog:
  format: common
  bufferingSize: 100

# Entry Points
entryPoints:
  web:
    address: ":80"
    http:
      redirections:
        entryPoint:
          to: websecure
          scheme: https
          permanent: true

  websecure:
    address: ":443"
    http:
      tls:
        certResolver: cloudflare
        domains:
          - main: yourdomain.com  # Replace with your domain
            sans:
              - "*.yourdomain.com"
    http2:
      maxConcurrentStreams: 250

  metrics:
    address: ":8082"

# Providers
providers:
  docker:
    endpoint: "unix:///var/run/docker.sock"
    exposedByDefault: false
    network: openagile_network
    watch: true
  
  file:
    directory: /etc/traefik/dynamic
    watch: true

# Certificate Resolvers
certificatesResolvers:
  cloudflare:
    acme:
      email: your-email@example.com  # Replace with your email
      storage: /letsencrypt/acme.json
      dnsChallenge:
        provider: cloudflare
        delayBeforeCheck: 30
        resolvers:
          - "1.1.1.1:53"
          - "1.0.0.1:53"

# Metrics for Prometheus
metrics:
  prometheus:
    addEntryPointsLabels: true
    addServicesLabels: true
    addRoutersLabels: true
    entryPoint: metrics
    manualRouting: false
```

### Traefik Dynamic Configuration

Create `configs/traefik/dynamic/dynamic.yml`:

```yaml
# Dynamic Configuration for Traefik

http:
  middlewares:
    # Security headers
    security-headers:
      headers:
        frameDeny: true
        sslRedirect: true
        browserXssFilter: true
        contentTypeNosniff: true
        forceSTSHeader: true
        stsIncludeSubdomains: true
        stsPreload: true
        stsSeconds: 31536000
        customFrameOptionsValue: "SAMEORIGIN"
        customResponseHeaders:
          X-Powered-By: ""
          Server: ""

    # Traefik dashboard authentication
    traefik-auth:
      basicAuth:
        users:
          - "admin:$apr1$YOUR_HASH_HERE"  # Generate with: htpasswd -n admin

    # Rate limiting
    rate-limit:
      rateLimit:
        average: 100
        burst: 50
        period: 1m

    # Compression
    compression:
      compress: true

tls:
  options:
    default:
      minVersion: VersionTLS12
      cipherSuites:
        - TLS_ECDHE_RSA_WITH_AES_128_GCM_SHA256
        - TLS_ECDHE_RSA_WITH_AES_256_GCM_SHA384
        - TLS_ECDHE_RSA_WITH_CHACHA20_POLY1305
        - TLS_AES_128_GCM_SHA256
        - TLS_AES_256_GCM_SHA384
        - TLS_CHACHA20_POLY1305_SHA256
      sniStrict: true
```

### Prometheus Configuration

Create `configs/prometheus/prometheus.yml`:

```yaml
global:
  scrape_interval: 15s
  evaluation_interval: 15s
  external_labels:
    cluster: 'openagile-production'
    environment: 'production'

rule_files:
  - 'alerts.yml'

scrape_configs:
  - job_name: 'prometheus'
    static_configs:
      - targets: ['localhost:9090']
      
  - job_name: 'cadvisor'
    static_configs:
      - targets: ['cadvisor:8080']
    metric_relabel_configs:
      - source_labels: [__name__]
        regex: 'container_(cpu|memory|network|fs).*'
        action: keep
  
  - job_name: 'node-exporter'
    static_configs:
      - targets: ['node-exporter:9100']
  
  - job_name: 'traefik'
    static_configs:
      - targets: ['traefik:8082']
  
  - job_name: 'gitea'
    static_configs:
      - targets: ['gitea:3000']
    metrics_path: '/metrics'
  
  - job_name: 'n8n'
    static_configs:
      - targets: ['n8n:5678']
    metrics_path: '/metrics'
```

### Prometheus Alerts

Create `configs/prometheus/alerts.yml`:

```yaml
groups:
  - name: openagile-alerts
    rules:
      - alert: ServiceDown
        expr: up == 0
        for: 1m
        labels:
          severity: critical
        annotations:
          summary: "Service {{ $labels.job }} is down"
          description: "{{ $labels.instance }} has been down for more than 1 minute."

      - alert: HighCPUUsage
        expr: 100 - (avg by(instance) (rate(node_cpu_seconds_total{mode="idle"}[5m])) * 100) > 80
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "High CPU usage detected"
          description: "CPU usage is above 80% for more than 5 minutes."

      - alert: HighMemoryUsage
        expr: (1 - (node_memory_MemAvailable_bytes / node_memory_MemTotal_bytes)) * 100 > 80
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "High memory usage detected"
          description: "Memory usage is above 80% for more than 5 minutes."

      - alert: DiskSpaceLow
        expr: (1 - (node_filesystem_avail_bytes{fstype!="tmpfs"} / node_filesystem_size_bytes{fstype!="tmpfs"})) * 100 > 85
        for: 10m
        labels:
          severity: warning
        annotations:
          summary: "Low disk space"
          description: "Disk usage is above 85%."
```

### Grafana Datasource Provisioning

Create `configs/grafana/provisioning/datasources/datasource.yml`:

```yaml
apiVersion: 1

datasources:
  - name: Prometheus
    type: prometheus
    access: proxy
    url: http://prometheus:9090
    isDefault: true
    editable: false
```

### Database Init Script

Create `scripts/init-databases.sh`:

```bash
#!/bin/bash
# Initialize multiple databases for OpenAgile services

set -e
set -u

function create_database() {
    local database=$1
    echo "Creating database '$database'"
    psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" <<-EOSQL
        CREATE DATABASE $database;
        GRANT ALL PRIVILEGES ON DATABASE $database TO $POSTGRES_USER;
EOSQL
}

if [ -n "$POSTGRES_MULTIPLE_DATABASES" ]; then
    echo "Multiple database creation requested: $POSTGRES_MULTIPLE_DATABASES"
    for db in $(echo $POSTGRES_MULTIPLE_DATABASES | tr ',' ' '); do
        create_database $db
    done
    echo "Multiple databases created"
fi
```

Make the script executable:

```bash
chmod +x scripts/init-databases.sh
```

---

## Environment Configuration

### Create .env File

Create `~/openagile/.env`:

```bash
# Domain Configuration
DOMAIN=yourdomain.com

# Timezone
TIMEZONE=Africa/Lagos

# Cloudflare Configuration
CLOUDFLARE_EMAIL=your-email@example.com
CLOUDFLARE_API_TOKEN=your-cloudflare-api-token

# PostgreSQL Configuration
POSTGRES_USER=openagile
POSTGRES_PASSWORD=your-secure-password-here

# n8n Configuration
N8N_BASIC_AUTH_USER=admin
N8N_BASIC_AUTH_PASSWORD=your-n8n-password

# Grafana Configuration
GRAFANA_ADMIN_USER=admin
GRAFANA_ADMIN_PASSWORD=your-grafana-password

# Woodpecker CI/CD Configuration
WOODPECKER_AGENT_SECRET=your-random-32-char-secret
WOODPECKER_ADMIN=admin
# These will be set after Gitea OAuth app creation
WOODPECKER_GITEA_CLIENT=
WOODPECKER_GITEA_SECRET=
```

> [!IMPORTANT]
> Generate secure passwords using:
> ```bash
> openssl rand -base64 32
> ```

---

## Cloudflare DNS Setup

### Step 1: Log into Cloudflare Dashboard

1. Go to [Cloudflare Dashboard](https://dash.cloudflare.com)
2. Select your domain

### Step 2: Create DNS Records

Create the following A records pointing to your server IP:

| Type | Name | Content | Proxy Status |
|------|------|---------|--------------|
| A | @ | YOUR_SERVER_IP | DNS only (gray cloud) |
| A | traefik | YOUR_SERVER_IP | DNS only |
| A | portainer | YOUR_SERVER_IP | DNS only |
| A | git | YOUR_SERVER_IP | DNS only |
| A | ci | YOUR_SERVER_IP | DNS only |
| A | project | YOUR_SERVER_IP | DNS only |
| A | n8n | YOUR_SERVER_IP | DNS only |
| A | docs | YOUR_SERVER_IP | DNS only |
| A | metrics | YOUR_SERVER_IP | DNS only |
| A | erpnext | YOUR_SERVER_IP | DNS only |
| A | *.erpnext | YOUR_SERVER_IP | DNS only |

> [!NOTE]
> Keep the proxy status as **DNS only** (gray cloud) since Traefik handles SSL.

### Step 3: Create API Token

1. Go to **My Profile** → **API Tokens**
2. Click **Create Token**
3. Use **Edit zone DNS** template
4. Configure:
   - **Zone Resources**: Include your domain
   - **Permissions**: Zone → DNS → Edit
5. Copy the token and add to `.env` as `CLOUDFLARE_API_TOKEN`

---

## Main Stack Deployment

### Step 1: Generate Authentication Hash

```bash
# Generate htpasswd hash for Traefik dashboard
htpasswd -n admin
# Enter password when prompted
# Copy the output and update configs/traefik/dynamic/dynamic.yml
```

### Step 2: Start the Main Stack

```bash
cd ~/openagile

# Pull latest images
docker compose pull

# Start all services
docker compose up -d

# View logs
docker compose logs -f
```

### Step 3: Verify Services

```bash
# Check container status
docker compose ps

# Verify all containers are "Up"
docker compose ps --format "table {{.Name}}\t{{.Status}}"
```

---

## Frappe/ERPNext Stack Deployment

The Frappe/ERPNext stack runs as a separate sub-stack that connects to the main Traefik proxy.

### Step 1: Clone Frappe Docker Repository

```bash
cd ~/openagile
git clone https://github.com/frappe/frappe_docker.git
cd frappe_docker
```

### Step 2: Create Override Files

Create `overrides/compose.external-traefik.yaml`:

```yaml
# Connect Frappe to external Traefik network
networks:
  openagile_openagile_network:
    external: true

services:
  frontend:
    networks:
      - default
      - openagile_openagile_network
    labels:
      - "traefik.enable=true"
      - "traefik.docker.network=openagile_openagile_network"
      
      # Main ERPNext site
      - "traefik.http.routers.erpnext.rule=Host(`erpnext.${DOMAIN:-yourdomain.com}`)"
      - "traefik.http.routers.erpnext.entrypoints=websecure"
      - "traefik.http.routers.erpnext.tls=true"
      - "traefik.http.routers.erpnext.tls.certresolver=cloudflare"
      - "traefik.http.services.erpnext.loadbalancer.server.port=8080"
      
      # Wildcard for sub-sites
      - "traefik.http.routers.erpnext-sites.rule=HostRegexp(`{subdomain:[a-z]+}.erpnext.${DOMAIN:-yourdomain.com}`)"
      - "traefik.http.routers.erpnext-sites.entrypoints=websecure"
      - "traefik.http.routers.erpnext-sites.tls=true"
      - "traefik.http.routers.erpnext-sites.tls.certresolver=cloudflare"
      - "traefik.http.routers.erpnext-sites.service=erpnext"
```

Create `overrides/compose.databases.yaml`:

```yaml
services:
  db:
    image: mariadb:10.6
    restart: unless-stopped
    command:
      - --character-set-server=utf8mb4
      - --collation-server=utf8mb4_unicode_ci
      - --skip-character-set-client-handshake
      - --skip-innodb-read-only-compressed
    environment:
      MYSQL_ROOT_PASSWORD: ${DB_PASSWORD:-admin}
    volumes:
      - db-data:/var/lib/mysql
    healthcheck:
      test: mysqladmin ping -h localhost -p${DB_PASSWORD:-admin}
      interval: 1s
      retries: 20

volumes:
  db-data:
```

### Step 3: Deploy Frappe Stack

```bash
cd ~/openagile/frappe_docker

# Deploy using the deploy script (if available)
./deploy-compose.sh

# Or manually:
docker compose \
  -f compose.yaml \
  -f overrides/compose.databases.yaml \
  -f overrides/compose.external-traefik.yaml \
  up -d
```

### Step 4: Create ERPNext Site

```bash
# Wait for containers to be ready (about 60 seconds)
sleep 60

# Create the main site
docker compose exec backend bench new-site erpnext.yourdomain.com \
  --mariadb-root-password admin \
  --admin-password your-admin-password

# Install ERPNext
docker compose exec backend bench --site erpnext.yourdomain.com install-app erpnext
```

---

## Post-Deployment Verification

### Service Verification Checklist

| Service | URL | Expected Result |
|---------|-----|-----------------|
| Traefik | `https://traefik.yourdomain.com` | Dashboard login |
| Portainer | `https://portainer.yourdomain.com` | Setup wizard |
| Gitea | `https://git.yourdomain.com` | Git welcome page |
| Woodpecker | `https://ci.yourdomain.com` | Login via Gitea |
| OpenProject | `https://project.yourdomain.com` | Login page |
| n8n | `https://n8n.yourdomain.com` | Workflow editor |
| Wiki.js | `https://docs.yourdomain.com` | Setup wizard |
| Grafana | `https://metrics.yourdomain.com` | Dashboard login |
| ERPNext | `https://erpnext.yourdomain.com` | ERP login |

### Run Health Check

```bash
#!/bin/bash
# Quick health check script

echo "=== OpenAgile Health Check ==="

# Check running containers
echo -e "\n📦 Container Status:"
docker compose ps --format "table {{.Name}}\t{{.Status}}\t{{.Ports}}"

# Check disk usage
echo -e "\n💾 Disk Usage:"
df -h / | tail -1

# Check memory
echo -e "\n🧠 Memory Usage:"
free -h | grep Mem

# Check Docker resource usage
echo -e "\n🐳 Docker Resource Usage:"
docker stats --no-stream --format "table {{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}"
```

---

## Maintenance & Operations

### Backup Script

Create `scripts/backup-openagile.sh`:

```bash
#!/bin/bash
# Comprehensive backup script for OpenAgile Board

set -e

# Configuration
BACKUP_ROOT=~/openagile/backups
RETENTION_DAYS=${BACKUP_RETENTION_DAYS:-30}
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="$BACKUP_ROOT/$TIMESTAMP"

echo "========================================="
echo "OpenAgile Backup - $(date)"
echo "========================================="

# Create backup directory
mkdir -p "$BACKUP_DIR"/{volumes,configs,database}

# Backup Docker volumes
backup_volume() {
    local volume_name=$1
    local backup_file=$2
    
    echo "Backing up volume: $volume_name"
    docker run --rm \
        -v ${volume_name}:/data \
        -v ${BACKUP_DIR}/volumes:/backup \
        alpine tar czf /backup/${backup_file} -C /data .
}

# Backup databases
backup_database() {
    local db_name=$1
    
    echo "Backing up database: $db_name"
    docker compose exec -T postgres pg_dump -U openagile $db_name | gzip > "$BACKUP_DIR/database/${db_name}.sql.gz"
}

# Execute backups
backup_volume "openagile_postgres_data" "postgres_data.tar.gz"
backup_volume "openagile_n8n_data" "n8n_data.tar.gz"
backup_volume "openagile_wikijs_data" "wikijs_data.tar.gz"
backup_volume "openagile_grafana_data" "grafana_data.tar.gz"

backup_database "n8n"
backup_database "wikijs"
backup_database "openproject"
backup_database "gitea"

# Backup configs
tar czf "$BACKUP_DIR/configs/openagile_configs.tar.gz" configs/ docker-compose.yml .env

# Cleanup old backups
find "$BACKUP_ROOT" -maxdepth 1 -type d -mtime +$RETENTION_DAYS -exec rm -rf {} \;

# Summary
BACKUP_SIZE=$(du -sh "$BACKUP_DIR" | cut -f1)
echo "========================================="
echo "Backup Complete!"
echo "Location: $BACKUP_DIR"
echo "Size: $BACKUP_SIZE"
echo "========================================="
```

### Daily Operations Commands

```bash
# View logs for a specific service
docker compose logs -f traefik

# Restart a service
docker compose restart openproject

# Update all services
docker compose pull && docker compose up -d

# Check resource usage
docker stats

# Enter a container shell
docker compose exec postgres psql -U openagile

# View container health
docker compose ps
```

---

## Troubleshooting

### Common Issues

#### 1. SSL Certificate Issues

**Symptoms**: Browser shows certificate errors

**Solution**:
```bash
# Check Traefik logs
docker compose logs traefik | grep -i acme

# Verify Cloudflare API token
curl -X GET "https://api.cloudflare.com/client/v4/user/tokens/verify" \
  -H "Authorization: Bearer ${CLOUDFLARE_API_TOKEN}"

# Delete old certificates and restart
docker compose exec traefik rm -rf /letsencrypt/acme.json
docker compose restart traefik
```

#### 2. Database Connection Issues

**Symptoms**: Services can't connect to PostgreSQL

**Solution**:
```bash
# Check PostgreSQL status
docker compose logs postgres

# Verify database creation
docker compose exec postgres psql -U openagile -c "\l"

# Recreate databases if needed
docker compose exec postgres psql -U openagile -c "CREATE DATABASE n8n;"
```

#### 3. Container Won't Start

**Symptoms**: Container keeps restarting

**Solution**:
```bash
# Check container logs
docker compose logs <service_name>

# Check resource limits
docker stats --no-stream

# Increase memory if needed in docker-compose.yml
```

#### 4. Gitea-Woodpecker Integration

**Symptoms**: Woodpecker can't authenticate with Gitea

**Solution**:
1. Go to Gitea → Settings → Applications → OAuth2 Applications
2. Create new OAuth2 application:
   - Name: Woodpecker CI
   - Redirect URI: `https://ci.yourdomain.com/authorize`
3. Copy Client ID and Secret to `.env`
4. Restart Woodpecker: `docker compose restart woodpecker_server`

---

## 📊 Architecture Diagram

```
                          INTERNET
                             │
                        [Cloudflare DNS]
                             │
                         [Traefik]
                   (Reverse Proxy + SSL)
                             │
        ┌────────────────────┼────────────────────┐
        │                    │                    │
    [Gitea] ────────────► [Woodpecker] ───────► [Registry]
      VCS                    CI/CD              Images
        │                    │                    │
        ├────────────────────┼────────────────────┤
        │                    │                    │
        │              [PostgreSQL]               │
        │          (Shared Database)              │
        │                    │                    │
        ├────────────┬───────┼───────┬────────────┤
        │            │       │       │            │
   [OpenProject] [n8n] [Wiki.js] [Grafana]  [ERPNext]
    PM System    Auto   Docs    Monitoring  Business
        │            │       │       │            │
        └────────────┴───────┴───────┴────────────┘
                   │
             [Prometheus]
           (Metrics Collection)
```

---

## 💰 Cost Summary

| Component | Cost |
|-----------|------|
| **Software** | $0 (100% Open Source) |
| **VPS Hosting** | ~€20/month (~$260/year) |
| **Domain** | ~$12/year |
| **Total Annual Cost** | ~$272/year |
| **Equivalent SaaS Cost** | ~$25,000/year |
| **Annual Savings** | ~$24,700 |

---

## � Woodpecker CI/CD Pipeline Examples

Woodpecker CI uses `.woodpecker.yml` files in your repository root to define pipelines.

### Basic Pipeline Structure

Create `.woodpecker.yml` in your repository:

```yaml
# .woodpecker.yml - Basic pipeline structure
when:
  - event: [push, pull_request, tag]
    branch: [main, develop]

steps:
  - name: test
    image: node:18-alpine
    commands:
      - npm install
      - npm test

  - name: build
    image: node:18-alpine
    commands:
      - npm run build
    when:
      - branch: main
```

### Pipeline Example 1: Node.js Application

```yaml
# .woodpecker.yml - Full Node.js CI/CD Pipeline
when:
  - event: push
    branch: [main, develop, feature/*]
  - event: pull_request

variables:
  - &node_image 'node:18-alpine'
  - &docker_image 'docker:24-dind'

steps:
  # Install dependencies and cache
  - name: install
    image: *node_image
    commands:
      - npm ci --prefer-offline

  # Run linting
  - name: lint
    image: *node_image
    commands:
      - npm run lint
    depends_on:
      - install

  # Run tests with coverage
  - name: test
    image: *node_image
    commands:
      - npm run test:coverage
    depends_on:
      - install

  # Build application
  - name: build
    image: *node_image
    commands:
      - npm run build
    depends_on:
      - lint
      - test
    when:
      - branch: main

  # Build Docker image
  - name: docker-build
    image: *docker_image
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock
    commands:
      - docker build -t myapp:${CI_COMMIT_SHA:0:8} .
      - docker tag myapp:${CI_COMMIT_SHA:0:8} registry.yourdomain.com/myapp:latest
    depends_on:
      - build
    when:
      - branch: main

  # Push to registry
  - name: docker-push
    image: *docker_image
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock
    environment:
      REGISTRY_USER:
        from_secret: registry_user
      REGISTRY_PASS:
        from_secret: registry_password
    commands:
      - echo "$REGISTRY_PASS" | docker login registry.yourdomain.com -u "$REGISTRY_USER" --password-stdin
      - docker push registry.yourdomain.com/myapp:latest
    depends_on:
      - docker-build
    when:
      - branch: main

  # Deploy to production
  - name: deploy
    image: alpine:latest
    environment:
      SSH_KEY:
        from_secret: deploy_ssh_key
      DEPLOY_HOST:
        from_secret: deploy_host
    commands:
      - apk add --no-cache openssh-client
      - mkdir -p ~/.ssh
      - echo "$SSH_KEY" > ~/.ssh/id_rsa
      - chmod 600 ~/.ssh/id_rsa
      - ssh -o StrictHostKeyChecking=no $DEPLOY_HOST "cd /app && docker compose pull && docker compose up -d"
    depends_on:
      - docker-push
    when:
      - branch: main
      - event: push
```

### Pipeline Example 2: Python/Django Application

```yaml
# .woodpecker.yml - Python/Django CI/CD Pipeline
when:
  - event: [push, pull_request]
    branch: [main, develop]

steps:
  # Run tests
  - name: test
    image: python:3.11-slim
    environment:
      DATABASE_URL: postgres://postgres:postgres@postgres:5432/test_db
      DJANGO_SETTINGS_MODULE: myapp.settings.test
    commands:
      - pip install -r requirements.txt
      - python manage.py migrate --noinput
      - python manage.py test --verbosity=2
      - coverage run manage.py test
      - coverage report

  # Security scan
  - name: security-scan
    image: python:3.11-slim
    commands:
      - pip install safety bandit
      - safety check -r requirements.txt
      - bandit -r myapp/ -ll
    depends_on:
      - test

  # Build and push
  - name: build-push
    image: docker:24-dind
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock
    environment:
      REGISTRY_USER:
        from_secret: registry_user
      REGISTRY_PASS:
        from_secret: registry_password
    commands:
      - docker build -t registry.yourdomain.com/django-app:${CI_COMMIT_SHA:0:8} .
      - echo "$REGISTRY_PASS" | docker login registry.yourdomain.com -u "$REGISTRY_USER" --password-stdin
      - docker push registry.yourdomain.com/django-app:${CI_COMMIT_SHA:0:8}
    when:
      - branch: main
    depends_on:
      - security-scan

services:
  postgres:
    image: postgres:15-alpine
    environment:
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres
      POSTGRES_DB: test_db
```

### Pipeline Example 3: Static Site Deployment

```yaml
# .woodpecker.yml - Static Site (Hugo/Jekyll) Pipeline
when:
  - event: push
    branch: main

steps:
  - name: build
    image: klakegg/hugo:0.111.3-ext-alpine
    commands:
      - hugo --minify

  - name: deploy
    image: alpine:latest
    environment:
      SSH_KEY:
        from_secret: deploy_ssh_key
    commands:
      - apk add --no-cache openssh-client rsync
      - mkdir -p ~/.ssh
      - echo "$SSH_KEY" > ~/.ssh/id_rsa
      - chmod 600 ~/.ssh/id_rsa
      - rsync -avz --delete public/ user@server:/var/www/mysite/
    depends_on:
      - build
```

### Pipeline Example 4: Multi-Environment Deployment

```yaml
# .woodpecker.yml - Multi-Environment Pipeline
when:
  - event: push
    branch: [main, staging, develop]

steps:
  - name: test
    image: node:18-alpine
    commands:
      - npm ci
      - npm test

  - name: build
    image: node:18-alpine
    commands:
      - npm run build
    depends_on:
      - test

  # Deploy to Development
  - name: deploy-dev
    image: alpine:latest
    environment:
      DEPLOY_URL:
        from_secret: dev_deploy_url
    commands:
      - echo "Deploying to Development..."
      - 'curl -X POST "$DEPLOY_URL" -H "Content-Type: application/json" -d "{\"ref\": \"$CI_COMMIT_SHA\"}"'
    when:
      - branch: develop
    depends_on:
      - build

  # Deploy to Staging
  - name: deploy-staging
    image: alpine:latest
    environment:
      DEPLOY_URL:
        from_secret: staging_deploy_url
    commands:
      - echo "Deploying to Staging..."
      - 'curl -X POST "$DEPLOY_URL" -H "Content-Type: application/json" -d "{\"ref\": \"$CI_COMMIT_SHA\"}"'
    when:
      - branch: staging
    depends_on:
      - build

  # Deploy to Production
  - name: deploy-production
    image: alpine:latest
    environment:
      DEPLOY_URL:
        from_secret: prod_deploy_url
    commands:
      - echo "Deploying to Production..."
      - 'curl -X POST "$DEPLOY_URL" -H "Content-Type: application/json" -d "{\"ref\": \"$CI_COMMIT_SHA\"}"'
    when:
      - branch: main
    depends_on:
      - build
```

### Setting Up Secrets in Woodpecker

1. Go to your repository in Woodpecker CI
2. Click **Settings** → **Secrets**
3. Add secrets:

| Secret Name | Description | Example |
|-------------|-------------|---------|
| `registry_user` | Docker registry username | `admin` |
| `registry_password` | Docker registry password | `secure-password` |
| `deploy_ssh_key` | SSH private key for deployment | `-----BEGIN RSA PRIVATE KEY-----...` |
| `deploy_host` | Target deployment server | `user@server.example.com` |

---

## 📊 Grafana Dashboard Configuration

### Dashboard Provisioning Setup

Create `configs/grafana/provisioning/dashboards/dashboard.yml`:

```yaml
apiVersion: 1

providers:
  - name: 'OpenAgile Dashboards'
    orgId: 1
    folder: 'OpenAgile'
    folderUid: ''
    type: file
    disableDeletion: false
    updateIntervalSeconds: 30
    allowUiUpdates: true
    options:
      path: /var/lib/grafana/dashboards
```

### Dashboard 1: System Overview

Create `configs/grafana/dashboards/system-overview.json`:

```json
{
  "annotations": {
    "list": []
  },
  "editable": true,
  "fiscalYearStartMonth": 0,
  "graphTooltip": 0,
  "id": null,
  "links": [],
  "liveNow": false,
  "panels": [
    {
      "datasource": {
        "type": "prometheus",
        "uid": "prometheus"
      },
      "fieldConfig": {
        "defaults": {
          "color": {
            "mode": "palette-classic"
          },
          "mappings": [],
          "thresholds": {
            "mode": "absolute",
            "steps": [
              { "color": "green", "value": null },
              { "color": "yellow", "value": 60 },
              { "color": "red", "value": 80 }
            ]
          },
          "unit": "percent"
        },
        "overrides": []
      },
      "gridPos": { "h": 6, "w": 6, "x": 0, "y": 0 },
      "id": 1,
      "options": {
        "orientation": "auto",
        "reduceOptions": {
          "calcs": ["lastNotNull"],
          "fields": "",
          "values": false
        },
        "showThresholdLabels": false,
        "showThresholdMarkers": true
      },
      "pluginVersion": "10.0.0",
      "targets": [
        {
          "datasource": { "type": "prometheus", "uid": "prometheus" },
          "expr": "100 - (avg(rate(node_cpu_seconds_total{mode=\"idle\"}[5m])) * 100)",
          "refId": "A"
        }
      ],
      "title": "CPU Usage",
      "type": "gauge"
    },
    {
      "datasource": {
        "type": "prometheus",
        "uid": "prometheus"
      },
      "fieldConfig": {
        "defaults": {
          "color": {
            "mode": "palette-classic"
          },
          "mappings": [],
          "thresholds": {
            "mode": "absolute",
            "steps": [
              { "color": "green", "value": null },
              { "color": "yellow", "value": 70 },
              { "color": "red", "value": 85 }
            ]
          },
          "unit": "percent"
        },
        "overrides": []
      },
      "gridPos": { "h": 6, "w": 6, "x": 6, "y": 0 },
      "id": 2,
      "options": {
        "orientation": "auto",
        "reduceOptions": {
          "calcs": ["lastNotNull"],
          "fields": "",
          "values": false
        },
        "showThresholdLabels": false,
        "showThresholdMarkers": true
      },
      "pluginVersion": "10.0.0",
      "targets": [
        {
          "datasource": { "type": "prometheus", "uid": "prometheus" },
          "expr": "(1 - (node_memory_MemAvailable_bytes / node_memory_MemTotal_bytes)) * 100",
          "refId": "A"
        }
      ],
      "title": "Memory Usage",
      "type": "gauge"
    },
    {
      "datasource": {
        "type": "prometheus",
        "uid": "prometheus"
      },
      "fieldConfig": {
        "defaults": {
          "color": {
            "mode": "palette-classic"
          },
          "mappings": [],
          "thresholds": {
            "mode": "absolute",
            "steps": [
              { "color": "green", "value": null },
              { "color": "yellow", "value": 70 },
              { "color": "red", "value": 85 }
            ]
          },
          "unit": "percent"
        },
        "overrides": []
      },
      "gridPos": { "h": 6, "w": 6, "x": 12, "y": 0 },
      "id": 3,
      "options": {
        "orientation": "auto",
        "reduceOptions": {
          "calcs": ["lastNotNull"],
          "fields": "",
          "values": false
        },
        "showThresholdLabels": false,
        "showThresholdMarkers": true
      },
      "pluginVersion": "10.0.0",
      "targets": [
        {
          "datasource": { "type": "prometheus", "uid": "prometheus" },
          "expr": "(1 - (node_filesystem_avail_bytes{mountpoint=\"/\"} / node_filesystem_size_bytes{mountpoint=\"/\"})) * 100",
          "refId": "A"
        }
      ],
      "title": "Disk Usage",
      "type": "gauge"
    },
    {
      "datasource": {
        "type": "prometheus",
        "uid": "prometheus"
      },
      "fieldConfig": {
        "defaults": {
          "color": { "mode": "thresholds" },
          "mappings": [
            { "options": { "0": { "color": "red", "text": "Down" }, "1": { "color": "green", "text": "Up" } }, "type": "value" }
          ],
          "thresholds": {
            "mode": "absolute",
            "steps": [
              { "color": "red", "value": null },
              { "color": "green", "value": 1 }
            ]
          }
        },
        "overrides": []
      },
      "gridPos": { "h": 6, "w": 6, "x": 18, "y": 0 },
      "id": 4,
      "options": {
        "colorMode": "background",
        "graphMode": "none",
        "justifyMode": "auto",
        "orientation": "horizontal",
        "reduceOptions": {
          "calcs": ["lastNotNull"],
          "fields": "",
          "values": false
        },
        "textMode": "auto"
      },
      "pluginVersion": "10.0.0",
      "targets": [
        {
          "datasource": { "type": "prometheus", "uid": "prometheus" },
          "expr": "up{job=\"traefik\"}",
          "legendFormat": "Traefik",
          "refId": "A"
        },
        {
          "datasource": { "type": "prometheus", "uid": "prometheus" },
          "expr": "up{job=\"gitea\"}",
          "legendFormat": "Gitea",
          "refId": "B"
        },
        {
          "datasource": { "type": "prometheus", "uid": "prometheus" },
          "expr": "up{job=\"n8n\"}",
          "legendFormat": "n8n",
          "refId": "C"
        }
      ],
      "title": "Service Status",
      "type": "stat"
    },
    {
      "datasource": {
        "type": "prometheus",
        "uid": "prometheus"
      },
      "fieldConfig": {
        "defaults": {
          "color": { "mode": "palette-classic" },
          "custom": {
            "axisCenteredZero": false,
            "axisColorMode": "text",
            "axisLabel": "",
            "axisPlacement": "auto",
            "barAlignment": 0,
            "drawStyle": "line",
            "fillOpacity": 10,
            "gradientMode": "none",
            "hideFrom": { "legend": false, "tooltip": false, "viz": false },
            "lineInterpolation": "linear",
            "lineWidth": 1,
            "pointSize": 5,
            "scaleDistribution": { "type": "linear" },
            "showPoints": "never",
            "spanNulls": false,
            "stacking": { "group": "A", "mode": "none" },
            "thresholdsStyle": { "mode": "off" }
          },
          "mappings": [],
          "thresholds": {
            "mode": "absolute",
            "steps": [{ "color": "green", "value": null }]
          },
          "unit": "short"
        },
        "overrides": []
      },
      "gridPos": { "h": 8, "w": 12, "x": 0, "y": 6 },
      "id": 5,
      "options": {
        "legend": { "calcs": [], "displayMode": "list", "placement": "bottom", "showLegend": true },
        "tooltip": { "mode": "multi", "sort": "none" }
      },
      "pluginVersion": "10.0.0",
      "targets": [
        {
          "datasource": { "type": "prometheus", "uid": "prometheus" },
          "expr": "sum(rate(traefik_entrypoint_requests_total[5m])) by (entrypoint)",
          "legendFormat": "{{entrypoint}}",
          "refId": "A"
        }
      ],
      "title": "Request Rate by Entrypoint",
      "type": "timeseries"
    },
    {
      "datasource": {
        "type": "prometheus",
        "uid": "prometheus"
      },
      "fieldConfig": {
        "defaults": {
          "color": { "mode": "palette-classic" },
          "custom": {
            "axisCenteredZero": false,
            "axisColorMode": "text",
            "axisLabel": "",
            "axisPlacement": "auto",
            "barAlignment": 0,
            "drawStyle": "line",
            "fillOpacity": 10,
            "gradientMode": "none",
            "hideFrom": { "legend": false, "tooltip": false, "viz": false },
            "lineInterpolation": "linear",
            "lineWidth": 1,
            "pointSize": 5,
            "scaleDistribution": { "type": "linear" },
            "showPoints": "never",
            "spanNulls": false,
            "stacking": { "group": "A", "mode": "none" },
            "thresholdsStyle": { "mode": "off" }
          },
          "mappings": [],
          "thresholds": {
            "mode": "absolute",
            "steps": [{ "color": "green", "value": null }]
          },
          "unit": "bytes"
        },
        "overrides": []
      },
      "gridPos": { "h": 8, "w": 12, "x": 12, "y": 6 },
      "id": 6,
      "options": {
        "legend": { "calcs": [], "displayMode": "list", "placement": "bottom", "showLegend": true },
        "tooltip": { "mode": "multi", "sort": "none" }
      },
      "pluginVersion": "10.0.0",
      "targets": [
        {
          "datasource": { "type": "prometheus", "uid": "prometheus" },
          "expr": "sum(container_memory_usage_bytes{name=~\".+\"}) by (name)",
          "legendFormat": "{{name}}",
          "refId": "A"
        }
      ],
      "title": "Container Memory Usage",
      "type": "timeseries"
    }
  ],
  "refresh": "30s",
  "schemaVersion": 38,
  "style": "dark",
  "tags": ["openagile", "system"],
  "templating": { "list": [] },
  "time": { "from": "now-1h", "to": "now" },
  "timepicker": {},
  "timezone": "",
  "title": "OpenAgile System Overview",
  "uid": "openagile-system",
  "version": 1,
  "weekStart": ""
}
```

### Dashboard 2: Traefik Metrics

Create `configs/grafana/dashboards/traefik-dashboard.json`:

```json
{
  "annotations": { "list": [] },
  "editable": true,
  "fiscalYearStartMonth": 0,
  "graphTooltip": 0,
  "id": null,
  "links": [],
  "liveNow": false,
  "panels": [
    {
      "datasource": { "type": "prometheus", "uid": "prometheus" },
      "fieldConfig": {
        "defaults": {
          "mappings": [],
          "thresholds": { "mode": "absolute", "steps": [{ "color": "green", "value": null }] },
          "unit": "reqps"
        },
        "overrides": []
      },
      "gridPos": { "h": 4, "w": 6, "x": 0, "y": 0 },
      "id": 1,
      "options": {
        "colorMode": "value",
        "graphMode": "area",
        "justifyMode": "auto",
        "orientation": "auto",
        "reduceOptions": { "calcs": ["lastNotNull"], "fields": "", "values": false },
        "textMode": "auto"
      },
      "pluginVersion": "10.0.0",
      "targets": [
        {
          "datasource": { "type": "prometheus", "uid": "prometheus" },
          "expr": "sum(rate(traefik_entrypoint_requests_total[5m]))",
          "refId": "A"
        }
      ],
      "title": "Total Request Rate",
      "type": "stat"
    },
    {
      "datasource": { "type": "prometheus", "uid": "prometheus" },
      "fieldConfig": {
        "defaults": {
          "mappings": [],
          "thresholds": { "mode": "absolute", "steps": [{ "color": "green", "value": null }] },
          "unit": "none"
        },
        "overrides": []
      },
      "gridPos": { "h": 4, "w": 6, "x": 6, "y": 0 },
      "id": 2,
      "options": {
        "colorMode": "value",
        "graphMode": "none",
        "justifyMode": "auto",
        "orientation": "auto",
        "reduceOptions": { "calcs": ["lastNotNull"], "fields": "", "values": false },
        "textMode": "auto"
      },
      "pluginVersion": "10.0.0",
      "targets": [
        {
          "datasource": { "type": "prometheus", "uid": "prometheus" },
          "expr": "traefik_service_open_connections",
          "legendFormat": "{{service}}",
          "refId": "A"
        }
      ],
      "title": "Open Connections",
      "type": "stat"
    },
    {
      "datasource": { "type": "prometheus", "uid": "prometheus" },
      "fieldConfig": {
        "defaults": {
          "color": { "mode": "palette-classic" },
          "custom": {
            "axisCenteredZero": false,
            "axisColorMode": "text",
            "axisLabel": "",
            "axisPlacement": "auto",
            "barAlignment": 0,
            "drawStyle": "line",
            "fillOpacity": 10,
            "gradientMode": "none",
            "hideFrom": { "legend": false, "tooltip": false, "viz": false },
            "lineInterpolation": "linear",
            "lineWidth": 1,
            "pointSize": 5,
            "scaleDistribution": { "type": "linear" },
            "showPoints": "never",
            "spanNulls": false,
            "stacking": { "group": "A", "mode": "none" },
            "thresholdsStyle": { "mode": "off" }
          },
          "mappings": [],
          "thresholds": { "mode": "absolute", "steps": [{ "color": "green", "value": null }] },
          "unit": "short"
        },
        "overrides": []
      },
      "gridPos": { "h": 8, "w": 12, "x": 0, "y": 4 },
      "id": 3,
      "options": {
        "legend": { "calcs": [], "displayMode": "list", "placement": "bottom", "showLegend": true },
        "tooltip": { "mode": "multi", "sort": "none" }
      },
      "pluginVersion": "10.0.0",
      "targets": [
        {
          "datasource": { "type": "prometheus", "uid": "prometheus" },
          "expr": "sum(rate(traefik_service_requests_total[5m])) by (service, code)",
          "legendFormat": "{{service}} - {{code}}",
          "refId": "A"
        }
      ],
      "title": "Requests by Service & Status Code",
      "type": "timeseries"
    },
    {
      "datasource": { "type": "prometheus", "uid": "prometheus" },
      "fieldConfig": {
        "defaults": {
          "color": { "mode": "palette-classic" },
          "custom": {
            "axisCenteredZero": false,
            "axisColorMode": "text",
            "axisLabel": "",
            "axisPlacement": "auto",
            "barAlignment": 0,
            "drawStyle": "line",
            "fillOpacity": 10,
            "gradientMode": "none",
            "hideFrom": { "legend": false, "tooltip": false, "viz": false },
            "lineInterpolation": "linear",
            "lineWidth": 1,
            "pointSize": 5,
            "scaleDistribution": { "type": "linear" },
            "showPoints": "never",
            "spanNulls": false,
            "stacking": { "group": "A", "mode": "none" },
            "thresholdsStyle": { "mode": "off" }
          },
          "mappings": [],
          "thresholds": { "mode": "absolute", "steps": [{ "color": "green", "value": null }] },
          "unit": "s"
        },
        "overrides": []
      },
      "gridPos": { "h": 8, "w": 12, "x": 12, "y": 4 },
      "id": 4,
      "options": {
        "legend": { "calcs": [], "displayMode": "list", "placement": "bottom", "showLegend": true },
        "tooltip": { "mode": "multi", "sort": "none" }
      },
      "pluginVersion": "10.0.0",
      "targets": [
        {
          "datasource": { "type": "prometheus", "uid": "prometheus" },
          "expr": "histogram_quantile(0.95, sum(rate(traefik_service_request_duration_seconds_bucket[5m])) by (le, service))",
          "legendFormat": "p95 {{service}}",
          "refId": "A"
        },
        {
          "datasource": { "type": "prometheus", "uid": "prometheus" },
          "expr": "histogram_quantile(0.50, sum(rate(traefik_service_request_duration_seconds_bucket[5m])) by (le, service))",
          "legendFormat": "p50 {{service}}",
          "refId": "B"
        }
      ],
      "title": "Response Time (p50/p95)",
      "type": "timeseries"
    }
  ],
  "refresh": "30s",
  "schemaVersion": 38,
  "style": "dark",
  "tags": ["openagile", "traefik"],
  "templating": { "list": [] },
  "time": { "from": "now-1h", "to": "now" },
  "timepicker": {},
  "timezone": "",
  "title": "Traefik Dashboard",
  "uid": "traefik-metrics",
  "version": 1,
  "weekStart": ""
}
```

### Dashboard 3: Container Overview

Create `configs/grafana/dashboards/container-overview.json`:

```json
{
  "annotations": { "list": [] },
  "editable": true,
  "fiscalYearStartMonth": 0,
  "graphTooltip": 0,
  "id": null,
  "links": [],
  "liveNow": false,
  "panels": [
    {
      "datasource": { "type": "prometheus", "uid": "prometheus" },
      "fieldConfig": {
        "defaults": {
          "color": { "mode": "palette-classic" },
          "custom": {
            "axisCenteredZero": false,
            "axisColorMode": "text",
            "axisLabel": "",
            "axisPlacement": "auto",
            "barAlignment": 0,
            "drawStyle": "line",
            "fillOpacity": 10,
            "gradientMode": "none",
            "hideFrom": { "legend": false, "tooltip": false, "viz": false },
            "lineInterpolation": "linear",
            "lineWidth": 1,
            "pointSize": 5,
            "scaleDistribution": { "type": "linear" },
            "showPoints": "never",
            "spanNulls": false,
            "stacking": { "group": "A", "mode": "none" },
            "thresholdsStyle": { "mode": "off" }
          },
          "mappings": [],
          "thresholds": { "mode": "absolute", "steps": [{ "color": "green", "value": null }] },
          "unit": "percent"
        },
        "overrides": []
      },
      "gridPos": { "h": 8, "w": 12, "x": 0, "y": 0 },
      "id": 1,
      "options": {
        "legend": { "calcs": ["mean", "max"], "displayMode": "table", "placement": "right", "showLegend": true },
        "tooltip": { "mode": "multi", "sort": "desc" }
      },
      "pluginVersion": "10.0.0",
      "targets": [
        {
          "datasource": { "type": "prometheus", "uid": "prometheus" },
          "expr": "sum(rate(container_cpu_usage_seconds_total{name=~\".+\"}[5m])) by (name) * 100",
          "legendFormat": "{{name}}",
          "refId": "A"
        }
      ],
      "title": "Container CPU Usage",
      "type": "timeseries"
    },
    {
      "datasource": { "type": "prometheus", "uid": "prometheus" },
      "fieldConfig": {
        "defaults": {
          "color": { "mode": "palette-classic" },
          "custom": {
            "axisCenteredZero": false,
            "axisColorMode": "text",
            "axisLabel": "",
            "axisPlacement": "auto",
            "barAlignment": 0,
            "drawStyle": "line",
            "fillOpacity": 10,
            "gradientMode": "none",
            "hideFrom": { "legend": false, "tooltip": false, "viz": false },
            "lineInterpolation": "linear",
            "lineWidth": 1,
            "pointSize": 5,
            "scaleDistribution": { "type": "linear" },
            "showPoints": "never",
            "spanNulls": false,
            "stacking": { "group": "A", "mode": "none" },
            "thresholdsStyle": { "mode": "off" }
          },
          "mappings": [],
          "thresholds": { "mode": "absolute", "steps": [{ "color": "green", "value": null }] },
          "unit": "bytes"
        },
        "overrides": []
      },
      "gridPos": { "h": 8, "w": 12, "x": 12, "y": 0 },
      "id": 2,
      "options": {
        "legend": { "calcs": ["mean", "max"], "displayMode": "table", "placement": "right", "showLegend": true },
        "tooltip": { "mode": "multi", "sort": "desc" }
      },
      "pluginVersion": "10.0.0",
      "targets": [
        {
          "datasource": { "type": "prometheus", "uid": "prometheus" },
          "expr": "container_memory_usage_bytes{name=~\".+\"}",
          "legendFormat": "{{name}}",
          "refId": "A"
        }
      ],
      "title": "Container Memory Usage",
      "type": "timeseries"
    },
    {
      "datasource": { "type": "prometheus", "uid": "prometheus" },
      "fieldConfig": {
        "defaults": {
          "color": { "mode": "palette-classic" },
          "custom": {
            "axisCenteredZero": false,
            "axisColorMode": "text",
            "axisLabel": "",
            "axisPlacement": "auto",
            "barAlignment": 0,
            "drawStyle": "line",
            "fillOpacity": 10,
            "gradientMode": "none",
            "hideFrom": { "legend": false, "tooltip": false, "viz": false },
            "lineInterpolation": "linear",
            "lineWidth": 1,
            "pointSize": 5,
            "scaleDistribution": { "type": "linear" },
            "showPoints": "never",
            "spanNulls": false,
            "stacking": { "group": "A", "mode": "none" },
            "thresholdsStyle": { "mode": "off" }
          },
          "mappings": [],
          "thresholds": { "mode": "absolute", "steps": [{ "color": "green", "value": null }] },
          "unit": "Bps"
        },
        "overrides": []
      },
      "gridPos": { "h": 8, "w": 24, "x": 0, "y": 8 },
      "id": 3,
      "options": {
        "legend": { "calcs": ["mean"], "displayMode": "table", "placement": "right", "showLegend": true },
        "tooltip": { "mode": "multi", "sort": "desc" }
      },
      "pluginVersion": "10.0.0",
      "targets": [
        {
          "datasource": { "type": "prometheus", "uid": "prometheus" },
          "expr": "sum(rate(container_network_receive_bytes_total{name=~\".+\"}[5m])) by (name)",
          "legendFormat": "{{name}} RX",
          "refId": "A"
        },
        {
          "datasource": { "type": "prometheus", "uid": "prometheus" },
          "expr": "sum(rate(container_network_transmit_bytes_total{name=~\".+\"}[5m])) by (name)",
          "legendFormat": "{{name}} TX",
          "refId": "B"
        }
      ],
      "title": "Container Network I/O",
      "type": "timeseries"
    }
  ],
  "refresh": "30s",
  "schemaVersion": 38,
  "style": "dark",
  "tags": ["openagile", "containers"],
  "templating": { "list": [] },
  "time": { "from": "now-1h", "to": "now" },
  "timepicker": {},
  "timezone": "",
  "title": "Container Overview",
  "uid": "container-overview",
  "version": 1,
  "weekStart": ""
}
```

### Importing Pre-built Dashboards

You can also import community dashboards from Grafana.com:

| Dashboard | ID | Description |
|-----------|-----|-------------|
| Node Exporter Full | 1860 | Complete server metrics |
| Docker Container Metrics | 893 | Container monitoring |
| Traefik 2 | 12250 | Traefik proxy metrics |
| PostgreSQL Database | 9628 | Database metrics |

**To import:**
1. Go to Grafana → Dashboards → Import
2. Enter the dashboard ID
3. Select Prometheus as data source
4. Click Import

---

## ⚡ n8n Workflow Examples

### Workflow 1: Deployment Notification

This workflow sends notifications to email/Slack when deployments occur.

**Trigger:** Woodpecker webhook
**Actions:** Parse deployment data, send notification

```json
{
  "name": "Deployment Notifier",
  "nodes": [
    {
      "parameters": {
        "httpMethod": "POST",
        "path": "woodpecker-deploy",
        "responseMode": "lastNode"
      },
      "name": "Webhook",
      "type": "n8n-nodes-base.webhook",
      "position": [250, 300]
    },
    {
      "parameters": {
        "conditions": {
          "string": [
            {
              "value1": "={{$json[\"event\"]}}",
              "operation": "equals",
              "value2": "deployment"
            }
          ]
        }
      },
      "name": "Is Deployment?",
      "type": "n8n-nodes-base.if",
      "position": [450, 300]
    },
    {
      "parameters": {
        "channel": "#deployments",
        "text": "🚀 *Deployment Complete*\n\n*Repo:* {{$json[\"repo\"][\"full_name\"]}}\n*Branch:* {{$json[\"commit\"][\"branch\"]}}\n*Commit:* {{$json[\"commit\"][\"sha\"].substring(0,7)}}\n*Author:* {{$json[\"commit\"][\"author\"]}}\n*Message:* {{$json[\"commit\"][\"message\"]}}\n*Status:* ✅ Success",
        "attachments": []
      },
      "name": "Slack Notification",
      "type": "n8n-nodes-base.slack",
      "position": [650, 200]
    },
    {
      "parameters": {
        "fromEmail": "deployments@yourdomain.com",
        "toEmail": "team@yourdomain.com",
        "subject": "Deployment: {{$json[\"repo\"][\"name\"]}} - {{$json[\"commit\"][\"branch\"]}}",
        "text": "Deployment completed successfully.\n\nRepository: {{$json[\"repo\"][\"full_name\"]}}\nBranch: {{$json[\"commit\"][\"branch\"]}}\nCommit: {{$json[\"commit\"][\"sha\"]}}\nAuthor: {{$json[\"commit\"][\"author\"]}}\nMessage: {{$json[\"commit\"][\"message\"]}}"
      },
      "name": "Email Notification",
      "type": "n8n-nodes-base.emailSend",
      "position": [650, 400]
    }
  ],
  "connections": {
    "Webhook": { "main": [[{ "node": "Is Deployment?", "type": "main", "index": 0 }]] },
    "Is Deployment?": {
      "main": [
        [{ "node": "Slack Notification", "type": "main", "index": 0 }, { "node": "Email Notification", "type": "main", "index": 0 }],
        []
      ]
    }
  }
}
```

**Setup Instructions:**
1. Import workflow in n8n
2. Configure Slack credentials
3. Configure SMTP email credentials
4. Copy webhook URL and add to Woodpecker repository settings

### Workflow 2: Daily Backup Report

This workflow runs daily backups and sends a status report.

```json
{
  "name": "Daily Backup Report",
  "nodes": [
    {
      "parameters": {
        "rule": {
          "interval": [{ "field": "hours", "hoursInterval": 24 }]
        }
      },
      "name": "Daily Trigger",
      "type": "n8n-nodes-base.scheduleTrigger",
      "position": [250, 300]
    },
    {
      "parameters": {
        "command": "cd ~/openagile && ./scripts/backup-openagile.sh 2>&1"
      },
      "name": "Run Backup Script",
      "type": "n8n-nodes-base.executeCommand",
      "position": [450, 300]
    },
    {
      "parameters": {
        "conditions": {
          "number": [
            {
              "value1": "={{$json[\"exitCode\"]}}",
              "operation": "equal",
              "value2": 0
            }
          ]
        }
      },
      "name": "Check Exit Code",
      "type": "n8n-nodes-base.if",
      "position": [650, 300]
    },
    {
      "parameters": {
        "fromEmail": "backups@yourdomain.com",
        "toEmail": "admin@yourdomain.com",
        "subject": "✅ OpenAgile Backup Complete - {{$now.format('YYYY-MM-DD')}}",
        "text": "Daily backup completed successfully.\n\n{{$json[\"stdout\"]}}"
      },
      "name": "Success Email",
      "type": "n8n-nodes-base.emailSend",
      "position": [850, 200]
    },
    {
      "parameters": {
        "fromEmail": "backups@yourdomain.com",
        "toEmail": "admin@yourdomain.com",
        "subject": "❌ OpenAgile Backup FAILED - {{$now.format('YYYY-MM-DD')}}",
        "text": "Daily backup failed!\n\nError Output:\n{{$json[\"stderr\"]}}\n\nPlease investigate immediately."
      },
      "name": "Failure Email",
      "type": "n8n-nodes-base.emailSend",
      "position": [850, 400]
    }
  ],
  "connections": {
    "Daily Trigger": { "main": [[{ "node": "Run Backup Script", "type": "main", "index": 0 }]] },
    "Run Backup Script": { "main": [[{ "node": "Check Exit Code", "type": "main", "index": 0 }]] },
    "Check Exit Code": {
      "main": [
        [{ "node": "Success Email", "type": "main", "index": 0 }],
        [{ "node": "Failure Email", "type": "main", "index": 0 }]
      ]
    }
  }
}
```

### Workflow 3: OpenProject Issue Sync

This workflow syncs Gitea issues to OpenProject when they're created.

```json
{
  "name": "Gitea to OpenProject Sync",
  "nodes": [
    {
      "parameters": {
        "httpMethod": "POST",
        "path": "gitea-issue",
        "responseMode": "lastNode"
      },
      "name": "Gitea Webhook",
      "type": "n8n-nodes-base.webhook",
      "position": [250, 300]
    },
    {
      "parameters": {
        "conditions": {
          "string": [
            {
              "value1": "={{$json[\"action\"]}}",
              "operation": "equals",
              "value2": "opened"
            }
          ]
        }
      },
      "name": "Is New Issue?",
      "type": "n8n-nodes-base.if",
      "position": [450, 300]
    },
    {
      "parameters": {
        "url": "https://project.yourdomain.com/api/v3/projects/1/work_packages",
        "authentication": "genericCredentialType",
        "genericAuthType": "httpBasicAuth",
        "sendBody": true,
        "specifyBody": "json",
        "jsonBody": "={\n  \"subject\": \"[Gitea #{{$json[\"issue\"][\"number\"]}}] {{$json[\"issue\"][\"title\"]}}\",\n  \"description\": {\n    \"raw\": \"{{$json[\"issue\"][\"body\"]}}\\n\\n---\\nSynced from: {{$json[\"issue\"][\"html_url\"]}}\"\n  },\n  \"_links\": {\n    \"type\": { \"href\": \"/api/v3/types/1\" },\n    \"status\": { \"href\": \"/api/v3/statuses/1\" },\n    \"priority\": { \"href\": \"/api/v3/priorities/2\" }\n  }\n}"
      },
      "name": "Create OpenProject Work Package",
      "type": "n8n-nodes-base.httpRequest",
      "position": [650, 200]
    },
    {
      "parameters": {
        "url": "={{$node[\"Gitea Webhook\"].json[\"issue\"][\"comments_url\"]}}",
        "authentication": "genericCredentialType",
        "genericAuthType": "httpBasicAuth",
        "sendBody": true,
        "bodyParameters": {
          "parameters": [
            {
              "name": "body",
              "value": "📌 This issue has been synced to OpenProject: https://project.yourdomain.com/work_packages/{{$json[\"id\"]}}"
            }
          ]
        }
      },
      "name": "Comment on Gitea Issue",
      "type": "n8n-nodes-base.httpRequest",
      "position": [850, 200]
    }
  ],
  "connections": {
    "Gitea Webhook": { "main": [[{ "node": "Is New Issue?", "type": "main", "index": 0 }]] },
    "Is New Issue?": { "main": [[{ "node": "Create OpenProject Work Package", "type": "main", "index": 0 }], []] },
    "Create OpenProject Work Package": { "main": [[{ "node": "Comment on Gitea Issue", "type": "main", "index": 0 }]] }
  }
}
```

### Workflow 4: System Health Monitor

This workflow monitors system health and alerts on issues.

```json
{
  "name": "System Health Monitor",
  "nodes": [
    {
      "parameters": {
        "rule": {
          "interval": [{ "field": "minutes", "minutesInterval": 5 }]
        }
      },
      "name": "Every 5 Minutes",
      "type": "n8n-nodes-base.scheduleTrigger",
      "position": [250, 300]
    },
    {
      "parameters": {
        "url": "http://prometheus:9090/api/v1/query",
        "sendQuery": true,
        "queryParameters": {
          "parameters": [
            { "name": "query", "value": "100 - (avg(rate(node_cpu_seconds_total{mode=\"idle\"}[5m])) * 100)" }
          ]
        }
      },
      "name": "Get CPU Usage",
      "type": "n8n-nodes-base.httpRequest",
      "position": [450, 200]
    },
    {
      "parameters": {
        "url": "http://prometheus:9090/api/v1/query",
        "sendQuery": true,
        "queryParameters": {
          "parameters": [
            { "name": "query", "value": "(1 - (node_memory_MemAvailable_bytes / node_memory_MemTotal_bytes)) * 100" }
          ]
        }
      },
      "name": "Get Memory Usage",
      "type": "n8n-nodes-base.httpRequest",
      "position": [450, 400]
    },
    {
      "parameters": {
        "mode": "combine",
        "combineBy": "combineAll",
        "options": {}
      },
      "name": "Merge Results",
      "type": "n8n-nodes-base.merge",
      "position": [650, 300]
    },
    {
      "parameters": {
        "jsCode": "const cpu = parseFloat(items[0].json.data.result[0]?.value[1] || 0);\nconst memory = parseFloat(items[0].json.data.result[1]?.value[1] || 0);\n\nreturn [{\n  json: {\n    cpu: cpu.toFixed(2),\n    memory: memory.toFixed(2),\n    cpuAlert: cpu > 80,\n    memoryAlert: memory > 85,\n    timestamp: new Date().toISOString()\n  }\n}];"
      },
      "name": "Process Metrics",
      "type": "n8n-nodes-base.code",
      "position": [850, 300]
    },
    {
      "parameters": {
        "conditions": {
          "boolean": [
            { "value1": "={{$json[\"cpuAlert\"]}}", "value2": true },
            { "value1": "={{$json[\"memoryAlert\"]}}", "value2": true }
          ]
        },
        "combineOperation": "any"
      },
      "name": "Alert Needed?",
      "type": "n8n-nodes-base.if",
      "position": [1050, 300]
    },
    {
      "parameters": {
        "channel": "#alerts",
        "text": "⚠️ *System Alert*\n\n🖥️ CPU: {{$json[\"cpu\"]}}%\n💾 Memory: {{$json[\"memory\"]}}%\n⏰ Time: {{$json[\"timestamp\"]}}\n\nPlease investigate!"
      },
      "name": "Send Alert",
      "type": "n8n-nodes-base.slack",
      "position": [1250, 200]
    }
  ],
  "connections": {
    "Every 5 Minutes": { "main": [[{ "node": "Get CPU Usage", "type": "main", "index": 0 }, { "node": "Get Memory Usage", "type": "main", "index": 0 }]] },
    "Get CPU Usage": { "main": [[{ "node": "Merge Results", "type": "main", "index": 0 }]] },
    "Get Memory Usage": { "main": [[{ "node": "Merge Results", "type": "main", "index": 1 }]] },
    "Merge Results": { "main": [[{ "node": "Process Metrics", "type": "main", "index": 0 }]] },
    "Process Metrics": { "main": [[{ "node": "Alert Needed?", "type": "main", "index": 0 }]] },
    "Alert Needed?": { "main": [[{ "node": "Send Alert", "type": "main", "index": 0 }], []] }
  }
}
```

### Workflow 5: Wiki.js Auto-Documentation

This workflow automatically creates Wiki.js documentation from README files in repositories.

```json
{
  "name": "Auto-Document from README",
  "nodes": [
    {
      "parameters": {
        "httpMethod": "POST",
        "path": "gitea-push",
        "responseMode": "lastNode"
      },
      "name": "Gitea Push Webhook",
      "type": "n8n-nodes-base.webhook",
      "position": [250, 300]
    },
    {
      "parameters": {
        "jsCode": "const commits = items[0].json.commits || [];\nconst readmeChanged = commits.some(c => \n  c.modified?.includes('README.md') || \n  c.added?.includes('README.md')\n);\n\nreturn [{ json: { ...items[0].json, readmeChanged } }];"
      },
      "name": "Check README Changed",
      "type": "n8n-nodes-base.code",
      "position": [450, 300]
    },
    {
      "parameters": {
        "conditions": {
          "boolean": [{ "value1": "={{$json[\"readmeChanged\"]}}", "value2": true }]
        }
      },
      "name": "README Changed?",
      "type": "n8n-nodes-base.if",
      "position": [650, 300]
    },
    {
      "parameters": {
        "url": "=https://git.yourdomain.com/api/v1/repos/{{$json[\"repository\"][\"full_name\"]}}/raw/README.md",
        "authentication": "genericCredentialType",
        "genericAuthType": "httpBasicAuth"
      },
      "name": "Fetch README",
      "type": "n8n-nodes-base.httpRequest",
      "position": [850, 200]
    },
    {
      "parameters": {
        "url": "https://docs.yourdomain.com/graphql",
        "authentication": "genericCredentialType",
        "genericAuthType": "httpHeaderAuth",
        "sendBody": true,
        "specifyBody": "json",
        "jsonBody": "={\n  \"query\": \"mutation { pages { update(id: 1, content: \\\"{{$json[\"data\"]}}\\\", isPublished: true) { responseResult { succeeded errorCode message } } } }\"\n}"
      },
      "name": "Update Wiki.js Page",
      "type": "n8n-nodes-base.httpRequest",
      "position": [1050, 200]
    }
  ],
  "connections": {
    "Gitea Push Webhook": { "main": [[{ "node": "Check README Changed", "type": "main", "index": 0 }]] },
    "Check README Changed": { "main": [[{ "node": "README Changed?", "type": "main", "index": 0 }]] },
    "README Changed?": { "main": [[{ "node": "Fetch README", "type": "main", "index": 0 }], []] },
    "Fetch README": { "main": [[{ "node": "Update Wiki.js Page", "type": "main", "index": 0 }]] }
  }
}
```

### How to Import n8n Workflows

1. Go to n8n dashboard (`https://n8n.yourdomain.com`)
2. Click **Workflows** → **Add Workflow**
3. Click the three dots menu → **Import from File** or paste JSON
4. Configure credentials for each node (Slack, Email, etc.)
5. Activate the workflow

### Setting Up n8n Credentials

| Credential | Path | Required Fields |
|------------|------|-----------------|
| **Slack** | Settings → Credentials → Slack OAuth2 API | OAuth Access Token |
| **SMTP** | Settings → Credentials → SMTP | Host, Port, User, Password |
| **HTTP Basic Auth** | Settings → Credentials → HTTP Basic Auth | User, Password |
| **HTTP Header Auth** | Settings → Credentials → HTTP Header Auth | Header Name, Value |

---

## �📚 Additional Resources

- [Traefik Documentation](https://doc.traefik.io/traefik/)
- [OpenProject Documentation](https://www.openproject.org/docs/)
- [Gitea Documentation](https://docs.gitea.io/)
- [Woodpecker CI Documentation](https://woodpecker-ci.org/docs/)
- [n8n Documentation](https://docs.n8n.io/)
- [Wiki.js Documentation](https://docs.requarks.io/)
- [Grafana Documentation](https://grafana.com/docs/)
- [Frappe/ERPNext Documentation](https://frappeframework.com/docs)

---

**Document Version**: 1.0.0  
**Last Updated**: January 2026  
**Author**: OpenAgile Team

---

> [!TIP]
> For questions or issues, check the troubleshooting section or create an issue in your Gitea repository.
