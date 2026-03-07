# Secure CD/Deployment Setup

This guide walks you through setting up GitHub Actions to automatically deploy to your VPS.

## Prerequisites

### 1. VPS Setup

Make sure your VPS has:
- Docker & Docker Compose installed
- Git repository cloned at a specific path (e.g., `/home/deploy/showcase`)
- `.env.production` file with secrets (never commit this)
- Backups directory: `mkdir -p /home/deploy/showcase/backups`

```bash
# On your VPS
mkdir -p /home/deploy/showcase
cd /home/deploy/showcase
git clone https://github.com/bhos-sec/showcase.git .
mkdir -p backups logs
```

### 2. Create Deployment SSH Key

Create a dedicated SSH key **on your VPS** for GitHub Actions (do NOT use your personal key):

```bash
# On your VPS, as the deploy user
ssh-keygen -t ed25519 -C "github-actions-deploy" -f ~/.ssh/github-actions -N ""

# Output the private key (you'll add this to GitHub Secrets)
cat ~/.ssh/github-actions

# Add the public key to authorized_keys
cat ~/.ssh/github-actions.pub >> ~/.ssh/authorized_keys
chmod 600 ~/.ssh/authorized_keys
```

### 3. GitHub Repository Secrets

In your repository: **Settings → Secrets and variables → Actions**

Add these secrets:

| Secret Name | Value |
|---|---|
| `VPS_HOST` | Your VPS IP address or domain (e.g., `192.168.1.100`) |
| `VPS_USER` | Deploy user (e.g., `deploy`) |
| `VPS_PORT` | SSH port (usually `22`, change if non-standard) |
| `VPS_SSH_KEY` | Contents of `~/.ssh/github-actions` (full private key) |
| `VPS_APP_PATH` | Path on VPS where app is cloned (e.g., `/home/deploy/showcase`) |
| `GHCR_TOKEN` | Personal Access Token with `packages:write` scope |
| `SLACK_WEBHOOK` | (Optional) Slack webhook for notifications |

**How to get GHCR_TOKEN:**
1. Go to GitHub Settings → Developer settings → Personal access tokens → Tokens (classic)
2. Generate new token with scopes: `write:packages`, `read:packages`
3. Copy and paste into `GHCR_TOKEN` secret

### 4. VPS Environment File

Create `.env.production` on your VPS (never commit to Git):

```bash
# On your VPS
cat > /home/deploy/showcase/.env.production << 'EOF'
# Backend
DEBUG=False
SECRET_KEY=your-very-secret-key-change-this
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com,your-vps-ip

# Security (disable SSL redirect until Certbot is set up, then enable)
SECURE_SSL_REDIRECT=False

# GitHub API
GITHUB_TOKEN=ghp_xxxxxxxxxxxx
GITHUB_ORG=bhos-sec

# Frontend
VITE_API_URL=https://api.yourdomain.com
VITE_APP_NAME=Collective Showcase

# Redis (for Celery)
REDIS_URL=redis://redis:6379/0

# Email (optional)
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
EOF

chmod 600 /home/deploy/showcase/.env.production
```

## Deployment Flow

### Automatic Deployment (on push to main)

```
1. Push code to main branch
   ↓
2. GitHub Actions workflow triggers
   ↓
3. Build backend Docker image → Push to GHCR
   ↓
4. Build frontend Docker image → Push to GHCR
   ↓
5. SSH into VPS and run deployment script
   ├─ Pull latest code from Git
   ├─ Login to GHCR
   ├─ Pull latest images
   ├─ Backup database
   ├─ Redeploy containers (zero downtime)
   ├─ Run migrations
   ├─ Collect static files
   ├─ Health check
   └─ Notify Slack (optional)
```

### Manual Deployment

If you need to manually trigger:
1. Go to repository → Actions
2. Click "Deploy to VPS" workflow
3. Click "Run workflow" → Select branch → "Run workflow"

## Security Best Practices

### ✅ DO

- ✅ Use SSH keys instead of passwords
- ✅ Rotate SSH keys regularly (e.g., every 90 days)
- ✅ Keep `.env.production` only on VPS, never commit to Git
- ✅ Use strong database passwords
- ✅ Limit GitHub token scope to minimum permissions
- ✅ Backup database before each deployment
- ✅ Test deployments on staging first
- ✅ Keep Docker images updated (`docker pull`)

### ❌ DON'T

- ❌ Don't commit secrets to Git
- ❌ Don't use the same SSH key for multiple VPS servers
- ❌ Don't share SSH keys via email/Slack
- ❌ Don't skip database backups
- ❌ Don't use `root` user for deployments
- ❌ Don't expose VPS IP in GitHub without SSH key protection

## Monitoring & Troubleshooting

### View Deployment Logs

In your GitHub repository: **Actions** tab → Select workflow run → Expand "Deploy to VPS" step

### SSH Into VPS Manually

```bash
ssh -i path/to/github-actions -p 22 deploy@your-vps-ip
cd /home/deploy/showcase
docker compose -f docker-compose.prod.yml logs -f backend
```

### Common Issues

**Issue: "Permission denied (publickey)"**
- Solution: Verify SSH key is in `~/.ssh/authorized_keys` on VPS
```bash
cat ~/.ssh/github-actions.pub >> ~/.ssh/authorized_keys
```

**Issue: "Unable to pull image from GHCR"**
- Solution: Verify GITHUB_TOKEN is set and has `packages:read` scope
```bash
echo "ghp_xxxx" | docker login ghcr.io -u USERNAME --password-stdin
```

**Issue: "Health check failed"**
- Solution: Check backend logs and ensure database migrations succeeded
```bash
docker compose -f docker-compose.prod.yml logs backend
docker compose -f docker-compose.prod.yml exec backend python manage.py migrate
```

### Manual Health Check

```bash
# From your local machine
curl https://yourdomain.com/api/health/
# Should return 200 OK
```

## Rollback Procedure

If a deployment breaks:

```bash
# On your VPS
cd /home/deploy/showcase

# View database backups
ls -lah backups/

# Restore previous database
cp backups/db_20260307_120000.sqlite3 data/db.sqlite3

# Checkout previous commit
git log --oneline | head -5
git checkout COMMIT_HASH

# Redeploy
docker compose -f docker-compose.prod.yml up -d --no-deps --build
docker compose -f docker-compose.prod.yml exec backend python manage.py migrate
```

## Pipeline Status Badge (Optional)

Add this to your README.md to show deployment status:

```markdown
[![Deploy to VPS](https://github.com/bhos-sec/showcase/actions/workflows/deploy.yml/badge.svg)](https://github.com/bhos-sec/showcase/actions/workflows/deploy.yml)
```

## Next Steps

1. ✅ Set up VPS directory and SSH key
2. ✅ Add GitHub repository secrets
3. ✅ Create `.env.production` on VPS
4. ✅ Add health check endpoint to backend (see below)
5. ✅ Test manual deployment using "Run workflow"
6. ✅ Monitor first automatic deployment after merge to main

## Health Check Endpoint (Backend)

Make sure your backend API has a health check endpoint. Add this to `backend/config/urls.py`:

```python
from django.views.generic import TemplateResponse

def health_check(request):
    return TemplateResponse(request, 'health.html', status=200)
    # Or simpler:
    # from django.http import JsonResponse
    # return JsonResponse({"status": "healthy"})

urlpatterns = [
    # ... existing patterns
    path('api/health/', health_check),
]
```

---

**Questions?** Check GitHub Actions logs or contact the team.
