# CI/CD Setup Instructions

## Overview

This project now has automated deployment via **GitHub Actions**. Every push to the `main` branch automatically deploys to the OpenAgile server at `185.216.177.250`.

## Initial Setup (One-Time)

### 1. Add SSH Private Key to GitHub Secrets

1. Go to your GitHub repository: https://github.com/zubbyik/zubbyik-openagile_frappe_update
2. Navigate to **Settings** → **Secrets and variables** → **Actions**
3. Click **New repository secret**
4. Name: `SSH_PRIVATE_KEY`
5. Value: Copy your **entire** private SSH key (the one you use to connect to the server)
   ```bash
   # On your local machine, display your private key:
   cat ~/.ssh/id_rsa
   # Or if you use a different key:
   cat ~/.ssh/id_ed25519
   ```
6. Paste the entire key content (including `-----BEGIN ... KEY-----` and `-----END ... KEY-----`)
7. Click **Add secret**

### 2. Ensure Server Has Git Repository

SSH to your server and verify the project is a git repository:

```bash
ssh zubbyik@185.216.177.250
cd /home/zubbyik/openagile/egbuna_estate_account_streamlight/estate-portfolio
git status  # Should show current branch and status
git remote -v  # Should show GitHub remote
```

If not initialized, run:
```bash
git init
git remote add origin git@github.com:zubbyik/zubbyik-openagile_frappe_update.git
git fetch origin
git checkout main
```

## How It Works

### Automatic Deployment

1. **You push code** from your local machine:
   ```bash
   git add .
   git commit -m "Fix EODHD ticker format"
   git push origin main
   ```

2. **GitHub Actions triggers** automatically and:
   - Connects to your server via SSH
   - Pulls the latest code
   - Rebuilds Docker containers (if needed)
   - Restarts the application
   - Runs the EODHD scraper as verification

3. **View deployment logs**:
   - Go to your GitHub repo → **Actions** tab
   - Click on the latest workflow run
   - Expand steps to see detailed logs

### Manual Deployment

You can also trigger deployment manually:
1. Go to GitHub repo → **Actions** tab
2. Select **Deploy to OpenAgile Server** workflow
3. Click **Run workflow** → **Run workflow**

## Monitoring

- **GitHub Actions**: https://github.com/zubbyik/zubbyik-openagile_frappe_update/actions
- **Application**: https://estate.zubbystudio.shop
- **Server Logs**: `ssh zubbyik@185.216.177.250 "cd ~/openagile/egbuna_estate_account_streamlight/estate-portfolio && docker compose logs -f streamlit"`

## Security Best Practices (Optional)

### Create a Dedicated Deployment Key

For better security, create a separate SSH key just for deployments:

```bash
# On your local machine
ssh-keygen -t ed25519 -C "github-actions-deploy" -f ~/.ssh/deploy_key
# Press Enter for no passphrase (required for automation)

# Copy the public key to your server
ssh-copy-id -i ~/.ssh/deploy_key.pub zubbyik@185.216.177.250

# Update GitHub secret with the new private key
cat ~/.ssh/deploy_key
# Copy output and update SSH_PRIVATE_KEY secret in GitHub
```

## Troubleshooting

### Deployment Fails with "Permission Denied"
- Verify the SSH key in GitHub secrets matches your server's authorized_keys
- Check: `ssh -i ~/.ssh/id_rsa zubbyik@185.216.177.250 "echo 'Connection successful'"`

### Containers Don't Restart
- SSH to server and check: `docker compose ps`
- View logs: `docker compose logs streamlit`
- Manually restart: `docker compose up -d --build`

### Scraper Still Shows Errors
- The EODHD scraper now uses `.XNSA` suffix (fixed in this deployment)
- Check if `EODHD_API_KEY` is set in server's `.env` file
- Verify API key is valid at https://eodhd.com

## Next Steps

After setting up the GitHub secret, test the pipeline:

```bash
# Make a small change
echo "# CI/CD Test" >> README.md
git add README.md
git commit -m "Test CI/CD pipeline"
git push origin main

# Watch the deployment at:
# https://github.com/zubbyik/zubbyik-openagile_frappe_update/actions
```
