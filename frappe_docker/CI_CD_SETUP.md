# Frappe/ERPNext CI/CD Setup Guide

## Overview

This project now has **automated deployment** via GitHub Actions. Every push to the `main` branch that affects the `frappe_docker/` directory automatically deploys to the OpenAgile server at `185.216.177.250`.

---

## Initial Setup (One-Time)

### 1. Verify SSH Key in GitHub Secrets

The deployment uses the existing `SSH_PRIVATE_KEY` secret that's already configured for the Estate Portfolio deployment.

**To verify it's set up:**
1. Go to: https://github.com/zubbyik/zubbyik-openagile_frappe_update
2. Navigate to **Settings** → **Secrets and variables** → **Actions**
3. Confirm `SSH_PRIVATE_KEY` exists

**If you need to update it:**
```bash
# On your local machine, display your private key:
cat ~/.ssh/id_rsa
# Or if you use a different key:
cat ~/.ssh/id_ed25519
```
Copy the entire key content (including `-----BEGIN ... KEY-----` and `-----END ... KEY-----`) and update the secret.

### 2. Verify Server Git Repository

SSH to your server and confirm the repository is properly configured:

```bash
ssh zubbyik@185.216.177.250
cd /home/zubbyik/openagile
git status  # Should show current branch
git remote -v  # Should show GitHub remote
```

If not initialized:
```bash
git init
git remote add origin git@github.com:zubbyik/zubbyik-openagile_frappe_update.git
git fetch origin
git checkout main
```

---

## How It Works

### Automatic Deployment

1. **You push code** from your workstation:
   ```bash
   cd /home/zubbyik/dev/obsidan_global/docker_compose_projects/openagile
   git add frappe_docker/
   git commit -m "Update Frappe configuration"
   git push origin main
   ```

2. **GitHub Actions triggers** automatically when:
   - Changes are pushed to the `main` branch
   - Changes affect files in `frappe_docker/` directory
   - The workflow file itself is modified

3. **Deployment process**:
   - Connects to server via SSH
   - Pulls latest code from GitHub
   - Runs `deploy-compose.sh` script which:
     - Stops existing containers
     - Starts services with all overrides
     - Installs custom apps via pip
     - Restarts backend
     - Runs health checks
   - Verifies deployment:
     - Checks container status
     - Lists installed apps
     - Tests site accessibility via curl

4. **View deployment logs**:
   - Go to: https://github.com/zubbyik/zubbyik-openagile_frappe_update/actions
   - Click on the latest workflow run
   - Expand steps to see detailed logs

### Manual Deployment

You can trigger deployment manually:

1. **Via GitHub UI**:
   - Go to: https://github.com/zubbyik/zubbyik-openagile_frappe_update/actions
   - Select **Deploy Frappe/ERPNext Stack** workflow
   - Click **Run workflow** → **Run workflow**

2. **Via Server SSH**:
   ```bash
   ssh zubbyik@185.216.177.250
   cd /home/zubbyik/openagile/frappe_docker
   ./deploy-compose.sh
   ```

---

## Deployment Script Features

The enhanced `deploy-compose.sh` script includes:

### ✅ Idempotency
- Safe to run multiple times
- Checks for existing installations
- Graceful handling of already-running services

### 🔍 Health Checks
- Container status verification
- Python environment validation
- Database connectivity checks
- Site accessibility tests (when not in CI mode)

### 🎨 Colored Output
- **Green**: Success messages
- **Yellow**: Warnings
- **Red**: Errors

### 🔄 Conditional Rebuilding
- Detects changes in Dockerfile or requirements
- Only rebuilds images when necessary
- Saves time on deployments

### 📊 Comprehensive Logging
- Clear status messages
- Detailed error reporting
- Exit codes for CI/CD integration

---

## Monitoring

### GitHub Actions
- **Workflow Runs**: https://github.com/zubbyik/zubbyik-openagile_frappe_update/actions
- **Deployment History**: View all past deployments and their status

### Application URLs
- **Main ERPNext**: https://erpnext.zubbystudio.shop
- **Library**: https://library.erpnext.zubbystudio.shop
- **Education**: https://edu.erpnext.zubbystudio.shop
- **Landing Page**: https://edu.erpnext.zubbystudio.shop/landing

### Server Logs
```bash
# View all services
ssh zubbyik@185.216.177.250 "cd ~/openagile/frappe_docker && docker compose logs -f"

# View specific service
ssh zubbyik@185.216.177.250 "cd ~/openagile/frappe_docker && docker compose logs -f backend"

# Check container status
ssh zubbyik@185.216.177.250 "cd ~/openagile/frappe_docker && docker compose ps"
```

---

## Troubleshooting

### Deployment Fails with "Permission Denied"
**Cause**: SSH key mismatch or server authentication issue

**Solution**:
```bash
# Test SSH connection
ssh -i ~/.ssh/id_rsa zubbyik@185.216.177.250 "echo 'Connection successful'"

# If fails, verify key is in server's authorized_keys
ssh-copy-id -i ~/.ssh/id_rsa.pub zubbyik@185.216.177.250
```

### Containers Don't Start
**Cause**: Docker Compose configuration error or resource constraints

**Solution**:
```bash
# SSH to server
ssh zubbyik@185.216.177.250
cd ~/openagile/frappe_docker

# Check container status
docker compose ps

# View logs for errors
docker compose logs backend
docker compose logs frontend

# Manually restart
./deploy-compose.sh
```

### Apps Not Installed (ModuleNotFoundError)
**Cause**: Python environment lost after container restart

**Solution**:
The deployment script automatically reinstalls apps. If manual fix needed:
```bash
ssh zubbyik@185.216.177.250
cd ~/openagile/frappe_docker

# Reinstall apps
docker compose exec backend /home/frappe/frappe-bench/env/bin/pip install -e apps/library_management
docker compose exec backend /home/frappe/frappe-bench/env/bin/pip install -e apps/education
docker compose exec backend /home/frappe/frappe-bench/env/bin/pip install -e apps/edu_theme

# Restart backend
docker compose restart backend
```

### Sites Return 404 or 502
**Cause**: Backend not ready, database issues, or Traefik routing problem

**Solution**:
```bash
ssh zubbyik@185.216.177.250
cd ~/openagile/frappe_docker

# Check backend logs
docker compose logs backend | tail -50

# Verify bench is working
docker compose exec backend bench list-apps

# Check database connectivity
docker compose exec db mysql -u root -padmin -e "SHOW DATABASES;"

# Verify Traefik routing
cd ~/openagile
docker compose logs traefik | grep frappe
```

### Frontend Assets 404
**Cause**: Volume mounts not working or symlink issues

**Solution**:
The deployment uses direct volume mounts (defined in `overrides/compose.frontend-custom-apps.yaml`) to bypass symlink issues. If problems persist:
```bash
ssh zubbyik@185.216.177.250
cd ~/openagile/frappe_docker

# Verify mounts are active
docker compose config | grep -A 10 "frontend:"

# Check if assets exist
ls -la apps/edu_theme/edu_theme/public/
ls -la apps/education/education/public/
ls -la apps/library_management/library_management/public/

# Restart frontend
docker compose restart frontend
```

---

## Development Workflow

### Making Changes

1. **Edit code** on your workstation:
   ```bash
   cd /home/zubbyik/dev/obsidan_global/docker_compose_projects/openagile/frappe_docker
   # Make your changes to apps, configs, etc.
   ```

2. **Test locally** (optional):
   ```bash
   # If you have a local Docker setup
   ./deploy-compose.sh
   ```

3. **Commit and push**:
   ```bash
   cd /home/zubbyik/dev/obsidan_global/docker_compose_projects/openagile
   git add frappe_docker/
   git commit -m "Descriptive message about changes"
   git push origin main
   ```

4. **Monitor deployment**:
   - Watch GitHub Actions: https://github.com/zubbyik/zubbyik-openagile_frappe_update/actions
   - Check server logs if needed

### Best Practices

- **Commit messages**: Use clear, descriptive messages
- **Test before push**: If possible, test changes locally first
- **Monitor deployments**: Watch the first few deployments to ensure everything works
- **Incremental changes**: Make small, focused commits rather than large batches
- **Branch protection**: Consider using feature branches for major changes

---

## Security Best Practices

### Dedicated Deployment Key (Recommended)

For better security, create a separate SSH key just for deployments:

```bash
# On your local machine
ssh-keygen -t ed25519 -C "github-actions-frappe-deploy" -f ~/.ssh/frappe_deploy_key
# Press Enter for no passphrase (required for automation)

# Copy the public key to your server
ssh-copy-id -i ~/.ssh/frappe_deploy_key.pub zubbyik@185.216.177.250

# Update GitHub secret with the new private key
cat ~/.ssh/frappe_deploy_key
# Copy output and update SSH_PRIVATE_KEY secret in GitHub
```

### Environment Variables

Never commit sensitive data to Git:
- `.env` files are in `.gitignore`
- Database passwords should only exist on the server
- API keys should be managed via environment variables

---

## Next Steps

After initial setup, test the pipeline:

```bash
# Make a small test change
cd /home/zubbyik/dev/obsidan_global/docker_compose_projects/openagile
echo "# CI/CD Test - $(date)" >> frappe_docker/README.md
git add frappe_docker/README.md
git commit -m "Test CI/CD pipeline"
git push origin main

# Watch the deployment at:
# https://github.com/zubbyik/zubbyik-openagile_frappe_update/actions
```

Once confirmed working, you can make real changes with confidence!
