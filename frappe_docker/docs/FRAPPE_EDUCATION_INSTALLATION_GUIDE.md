# 📚 Frappe Education App Installation Guide

## Complete Step-by-Step Guide for OpenAgile Board ERPNext (Frappe Docker Setup)

---

## ⚠️ CRITICAL: Environment and Deployment Rules

> [!CAUTION]
> **DO NOT RUN `docker compose` COMMANDS LOCALLY!**
>
> This project uses a **CI/CD deployment model**. Your local workstation is for **code editing only**.
> All Docker commands run on the **remote production server** (`185.216.177.250`).

### Deployment Architecture

```
┌────────────────────────────────────────────────────────────────────────────┐
│ LOCAL WORKSTATION                                                          │
│ Path: /home/zubbyik/dev/obsidan_global/docker_compose_projects/openagile   │
│                                                                            │
│ ✅ ALLOWED: Edit code, modify configs, commit changes                      │
│ ❌ FORBIDDEN: docker compose commands, running containers                  │
└────────────────────────────────────────────────────────────────────────────┘
                              │
                              │ git push origin main
                              ▼
┌────────────────────────────────────────────────────────────────────────────┐
│ GITHUB ACTIONS                                                             │
│ Repo: github.com/zubbyik/zubbyik-openagile_frappe_update                  │
│                                                                            │
│ Trigger: Push to main branch (frappe_docker/ changes)                      │
│ Action: SSH → Server → Run deploy-compose.sh                               │
└────────────────────────────────────────────────────────────────────────────┘
                              │
                              │ SSH + git pull + deploy
                              ▼
┌────────────────────────────────────────────────────────────────────────────┐
│ PRODUCTION SERVER                                                          │
│ IP: 185.216.177.250                                                        │
│ Path: /home/zubbyik/openagile/frappe_docker                               │
│                                                                            │
│ ✅ WHERE CONTAINERS RUN                                                    │
│ ✅ WHERE DOCKER COMMANDS EXECUTE                                           │
└────────────────────────────────────────────────────────────────────────────┘
```

### Command Execution Rules

| Action | Where to Execute | How |
|--------|------------------|-----|
| Edit source code | **Local workstation** | Use your editor |
| Modify compose files | **Local workstation** | Edit in `frappe_docker/` |
| Run `docker compose` | **Server only** | Via SSH or GitHub Actions |
| Run `bench` commands | **Server only** | Via SSH into container |
| Deploy changes | **GitHub Actions** | `git push origin main` |
| Manual deploy | **Server SSH** | `./deploy-compose.sh` |

---

## 🎯 What This Guide Covers

This guide walks you through installing the Frappe Education app:

1. **Phase A (Local)**: Download/prepare app code
2. **Phase B (Cloudflare)**: Configure DNS
3. **Phase C (Local)**: Update Traefik configuration
4. **Phase D (Deploy)**: Push to GitHub for automated deployment
5. **Phase E (Server SSH)**: Create site and complete setup
6. **Phase F (Browser)**: Verify and test

---

## 📝 Step-by-Step Installation

### Phase A: Download Education App (LOCAL)

> [!NOTE]
> These steps modify files on your **local workstation**. No Docker commands here!

#### Step A.1: Clone the Education App

```bash
# ON LOCAL WORKSTATION
cd /home/zubbyik/dev/obsidan_global/docker_compose_projects/openagile/frappe_docker

# Clone education app into apps directory
cd apps
git clone https://github.com/frappe/education.git --branch version-15
cd ..
```

#### Step A.2: Verify the App Exists Locally

```bash
# ON LOCAL WORKSTATION
ls -la apps/education
# Should show the cloned app directory

# Check it has the expected structure
ls apps/education/education
```

---

### Phase B: Configure DNS (CLOUDFLARE)

> [!NOTE]
> This step is done in the **Cloudflare Dashboard** - no terminal commands.

#### Step B.1: Add DNS Record

1. Log into **Cloudflare Dashboard**: https://dash.cloudflare.com
2. Select domain: `zubbystudio.shop`
3. Navigate to **DNS → Records**
4. Click **Add record**:

| Setting | Value |
|---------|-------|
| **Type** | A |
| **Name** | edu.erpnext |
| **IPv4 Address** | `185.216.177.250` (same as erpnext.zubbystudio.shop) |
| **Proxy status** | ☁️ Proxied (orange cloud) |
| **TTL** | Auto |

5. Click **Save**

#### Step B.2: Verify DNS Propagation

```bash
# Can run from anywhere (local or server)
dig edu.erpnext.zubbystudio.shop +short
# Should return: 185.216.177.250 (or Cloudflare proxy IP)

nslookup edu.erpnext.zubbystudio.shop
```

---

### Phase C: Update Traefik Configuration (LOCAL)

> [!NOTE]
> Edit files on your **local workstation**. Do NOT restart services locally!

#### Step C.1: Edit the Traefik Override File

```bash
# ON LOCAL WORKSTATION
cd /home/zubbyik/dev/obsidan_global/docker_compose_projects/openagile/frappe_docker
nano overrides/compose.external-traefik.yaml
```

#### Step C.2: Add Education Site Router

Add these labels for the education site in the `frontend` service section:

```yaml
      # Education site - ADD THIS BLOCK
      - "traefik.http.routers.erpnext-education.rule=Host(`edu.erpnext.zubbystudio.shop`)"
      - "traefik.http.routers.erpnext-education.entrypoints=websecure"
      - "traefik.http.routers.erpnext-education.tls=true"
      - "traefik.http.routers.erpnext-education.tls.certresolver=cloudflare"
      - "traefik.http.routers.erpnext-education.service=erpnext-frontend"
```

Update the HTTP redirect rule to include the new site:

```yaml
      - "traefik.http.routers.erpnext-http.rule=Host(`erpnext.zubbystudio.shop`) || Host(`library.erpnext.zubbystudio.shop`) || Host(`edu.erpnext.zubbystudio.shop`)"
```

Add security headers middleware:

```yaml
      - "traefik.http.routers.erpnext-education.middlewares=erpnext-headers"
```

#### Step C.3: Update deploy-compose.sh (if needed)

Verify `deploy-compose.sh` includes the education app in the pip install list:

```bash
# ON LOCAL WORKSTATION
grep -A 5 "APPS=" deploy-compose.sh
```

If education is missing, edit:

```bash
nano deploy-compose.sh
```

Find the `APPS` array and ensure it includes:

```bash
APPS=("library_management" "education" "edu_theme")
```

---

### Phase D: Deploy via GitHub (CI/CD)

> [!IMPORTANT]
> **This is how changes reach the production server.**
> Do NOT run docker commands locally!

#### Step D.1: Commit and Push Changes

```bash
# ON LOCAL WORKSTATION
cd /home/zubbyik/dev/obsidan_global/docker_compose_projects/openagile

# Stage changes
git add frappe_docker/

# Commit with descriptive message
git commit -m "Add Frappe Education app and configure Traefik routing"

# Push to trigger deployment
git push origin main
```

#### Step D.2: Monitor Deployment

1. Open: https://github.com/zubbyik/zubbyik-openagile_frappe_update/actions
2. Watch the **Deploy Frappe/ERPNext Stack** workflow
3. Wait for green checkmark (deployment complete)

**What the deployment does:**
- SSHs to server (`185.216.177.250`)
- Pulls latest code
- Runs `deploy-compose.sh` which:
  - Restarts containers with all overrides
  - Installs custom apps via pip
  - Builds assets
  - Runs health checks

---

### Phase E: Create Education Site (SERVER SSH)

> [!CAUTION]
> These commands run on the **PRODUCTION SERVER**, not locally!

#### Step E.1: SSH to the Server

```bash
# FROM LOCAL WORKSTATION
ssh zubbyik@185.216.177.250
```

#### Step E.2: Navigate to Project Directory

```bash
# ON SERVER
cd ~/openagile/frappe_docker
```

#### Step E.3: Enable DNS Multitenancy

```bash
# ON SERVER - Enter backend container
docker compose exec -it backend bash

# Inside container:
bench config dns_multitenant on
echo -n "" > sites/currentsite.txt

# Verify
cat sites/common_site_config.json | grep dns_multitenant
# Output: "dns_multitenant": true
```

#### Step E.4: Create the New Site

```bash
# Inside backend container:
bench new-site edu.erpnext.zubbystudio.shop \
  --db-name education_db \
  --mariadb-root-password admin \
  --admin-password YourSecurePassword123! \
  --install-app erpnext \
  --install-app education
```

#### Step E.5: Configure the Site

```bash
# Inside backend container:
bench --site edu.erpnext.zubbystudio.shop enable-scheduler
bench --site edu.erpnext.zubbystudio.shop clear-cache
bench --site all list

# Exit container
exit
```

#### Step E.6: Build Assets and Restart (on Server)

```bash
# ON SERVER (outside container)
docker compose exec backend bench build --app education
docker compose restart backend frontend
```

#### Step E.7: Exit SSH

```bash
exit
```

---

### Phase F: Verification (BROWSER)

#### Step F.1: Browser Testing

1. Open: https://edu.erpnext.zubbystudio.shop
2. Verify SSL certificate is valid (no warnings)
3. Login with:
   - **Username**: `Administrator`
   - **Password**: (password you set in Step E.4)

#### Step F.2: Verify Education Module

1. Press `/` (Awesome Bar)
2. Type `Student` - should see Student DocType
3. Check sidebar for **Education** module with:
   - Student
   - Course
   - Program
   - Academic Year
   - Academic Term

---

## 🔧 Troubleshooting

> [!WARNING]
> All troubleshooting commands run on the **SERVER** via SSH, not locally!

### SSH to Server First

```bash
# FROM LOCAL WORKSTATION
ssh zubbyik@185.216.177.250
cd ~/openagile/frappe_docker
```

### Issue 1: 404 - Site Not Found

```bash
# ON SERVER
docker compose exec backend cat sites/common_site_config.json | grep dns_multitenant
docker compose exec backend cat sites/currentsite.txt
docker compose exec backend bench --site all list
```

### Issue 2: Education Module Not Visible

```bash
# ON SERVER
docker compose exec backend bench --site edu.erpnext.zubbystudio.shop install-app education
docker compose exec backend bench --site edu.erpnext.zubbystudio.shop migrate
docker compose exec backend bench build --app education
```

### Issue 3: Assets 404

```bash
# ON SERVER
docker compose exec backend bench build
docker compose restart frontend
```

---

## 📖 Quick Reference: Where to Run Commands

| Command Type | Environment | Example |
|-------------|-------------|---------|
| Edit code files | Local workstation | `nano apps/education/...` |
| Git operations | Local workstation | `git add`, `git commit`, `git push` |
| Check DNS | Anywhere | `dig edu.erpnext.zubbystudio.shop` |
| docker compose | **Server SSH only** | `ssh server` then `docker compose ps` |
| bench commands | **Server SSH only** | Inside container via `docker compose exec` |
| View logs | **Server SSH only** | `docker compose logs backend` |

---

## 🚀 Deployment Workflow Summary

```
1. EDIT (Local)      →  Edit files in frappe_docker/
2. COMMIT (Local)    →  git add . && git commit -m "message"
3. PUSH (Local)      →  git push origin main
4. WAIT (GitHub)     →  Watch Actions for green checkmark
5. SSH (Server)      →  Create site, run migrations (one-time setup)
6. VERIFY (Browser)  →  Test at https://edu.erpnext.zubbystudio.shop
```

---

**Last Updated**: January 2026  
**Server IP**: 185.216.177.250  
**Repository**: github.com/zubbyik/zubbyik-openagile_frappe_update

**Author**: OpenAgile Board Team
