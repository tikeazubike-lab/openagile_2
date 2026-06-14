# Personal WireGuard VPN (wg-easy)

## Overview
This directory contains a Docker Compose setup for a personal WireGuard VPN using the `wg-easy` image. It completely avoids the destructive host-level firewall overwriting issues present in solutions like Algo VPN, running in isolated Docker network space instead.

## Features
- **WireGuard Server**: Running on `51820/UDP` (Host mapped).
- **Web UI**: Access client management via `https://vpn.zubbystudio.shop` (Routed through Traefik).
- **DNS**: Clients default to using Cloudflare (`1.1.1.1`, `1.0.0.1`). Configured via the Admin Panel on first boot.
- **IPv6**: Explicitly **disabled** (`DISABLE_IPV6=true`) due to missing `ip6_tables` kernel module on the Netcup host (`6.8.0-90-generic`).
- **Isolation**: Runs in a container without modifying host iptables directly.
- **CI/CD Deployment**: Deployed automatically via GitHub Actions `.github/workflows/deploy-wireguard.yml`.

## Architecture & Traffic Flow
There are two separate paths of traffic:
1. **The Web UI (TCP Port 443 -> 51821):** Users navigate to `https://vpn.zubbystudio.shop`. This hits Traefik via TCP, which routes it over the `openagile_openagile_network` to the `wg-easy` dashboard. This is purely for VPN administration.
2. **The VPN Tunnel (UDP Port 51820):** Incoming VPN client traffic connects directly to `vpn.zubbystudio.shop:51820` via UDP. This *bypasses* Traefik entirely.

## Key Deployment Notes (IMPORTANT for future agents)

### wg-easy Version: v15 (Breaking Changes from v14)
We pin to `ghcr.io/wg-easy/wg-easy:15`. Version 15 is a **complete rewrite** of the project with critical differences from v14:

1. **Password**: v15 does NOT support `PASSWORD_HASH` (bcrypt). If this variable is present, the container **explicitly crashes** with: `"You are using an invalid Configuration for wg-easy"`. Use the `INIT_PASSWORD` variable with a **plain text** password instead. v15 handles hashing internally.

2. **IPv6**: On the Netcup host kernel, `ip6_tables` is not available. Without `DISABLE_IPV6=true`, `wg-easy` tries to set up IPv6 routing, crashes, and dies in a restart loop.

3. **Most Settings Moved to UI**: Variables like `WG_DEFAULT_DNS`, `WG_ALLOWED_IPS`, `WG_PERSISTENT_KEEPALIVE` are now configured from the **Admin Panel in the Web UI** after first login. They no longer belong in the `.env` file.

4. **`.env` Only Needs**:
   ```bash
   WG_HOST=vpn.zubbystudio.shop   # Used by Traefik label interpolation
   INIT_PASSWORD=your_plain_text_password  # Set ONCE; then managed via the UI
   DISABLE_IPV6=true              # Required on Netcup (ip6_tables not available)
   ```

### Traefik Integration (Critical Labels)
The container MUST have this label for Traefik to correctly route when attached to multiple networks:
```yaml
- "traefik.docker.network=openagile_openagile_network"
```
Without it, Traefik doesn't know which network to use and silently ignores the container.

## Management & Operations Manual

### Web UI Dashboard Operations
1. Navigate to: `https://vpn.zubbystudio.shop`
2. **Password**: Log in using the `INIT_PASSWORD` you set (plain text). After first login, password management is done entirely within the Web UI.

Once logged in, operations are highly visual:
- **Add a Client**: Click "+ New", type a client name (e.g., "iPhone", "MacBook"), and save.
- **Connect a Mobile Device**: Click the QR Code icon next to the client name, open the WireGuard App on the device, tap "Scan from QR Code", and scan the screen.
- **Connect a PC/Mac**: Click the Download icon next to the client name to download the `.conf` profile. Import this file into the WireGuard desktop application.
- **Revoke Access**: To permanently cut off a device, click the Trash/Delete icon next to the client name. The key is instantly revoked.
- **Configure DNS/Allowed IPs**: Done via the Admin Panel within the Web UI (Settings section).

### System Infrastructure Operations

#### Cloudflare DNS Requirements
The `vpn.zubbystudio.shop` A-record in Cloudflare **MUST** be set to "DNS Only" (Grey Cloud). If it is "Proxied" (Orange Cloud), all VPN connections will fail because Cloudflare's free proxy drops UDP traffic.

#### Updating Configuration
Do not manually edit the `.env` file on the server. The CI/CD pipeline intentionally overwrites it using GitHub Secrets.
To update a secret:
1. Go to OpenAgile GitHub Repository -> Settings -> Secrets and variables -> Actions.
2. Update `WG_HOST` or `WG_PASSWORD_HASH` (this maps to `INIT_PASSWORD` in the deploy script).
3. Re-run the "Deploy WireGuard VPN" action from the Actions tab.

### GitHub Secrets Required
| Secret | Value | Purpose |
|--------|-------|---------|
| `SSH_PRIVATE_KEY` | Private key for Netcup server | SSH access for deployment |
| `WG_HOST` | `vpn.zubbystudio.shop` | Traefik routing label domain |
| `WG_PASSWORD_HASH` | Plain text password (NOT bcrypt!) | wg-easy v15 INIT_PASSWORD |

### File Structure Reference
- `docker-compose.yml`: Core service definition. Binds `51820/udp`, attaches to Traefik via `openagile_openagile_network`.
- `.env`: Dynamically generated on the server by GitHub Actions. Contains `WG_HOST`, `INIT_PASSWORD`, and `DISABLE_IPV6=true`.
- `data/` (Volume): Persistent storage for WireGuard client keys, SQLite config, and internal configurations.
- `diagnose-vpn.sh`: Diagnostic script for troubleshooting Traefik/container connectivity issues.
- `.github/workflows/deploy-wireguard.yml`: Full CI/CD deployment pipeline.

## Troubleshooting Shortcuts

| Symptom | Root Cause | Fix |
|---------|-----------|-----|
| `ERR_SSL_UNRECOGNIZED_NAME_ALERT` | Container is crash-looping, so Traefik has nothing to proxy | Check `docker logs wg-easy`, fix the crash |
| Route missing from Traefik dashboard | Container down, or missing `traefik.docker.network` label | Run `./diagnose-vpn.sh` |
| `"You are using an invalid Configuration"` | `PASSWORD` or `PASSWORD_HASH` env var exists in `.env` | Change to `INIT_PASSWORD=plaintext_password` |
| Container restarting with `ip6_tables not found` | Netcup kernel lacks IPv6 nat module | Add `DISABLE_IPV6=true` to `.env` |
| `git pull` diverges in CI | Server repo has local uncommitted changes | Workflow uses `git fetch && git reset --hard origin/main` |
