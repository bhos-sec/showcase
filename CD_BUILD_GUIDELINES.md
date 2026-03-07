# 📋 CD Flow Build Guidelines

Complete step-by-step instructions to build a production-ready continuous deployment pipeline.

---

## Phase 1: Infrastructure Setup (VPS)

### 1.1 VPS Prerequisites
- [ ] Linux server (Ubuntu 20.04+ recommended)
- [ ] Docker installed (`docker --version`)
- [ ] Docker Compose installed (`docker compose version`)
- [ ] Git installed (`git --version`)
- [ ] SSH access configured
- [ ] Minimum 2GB RAM, 20GB storage

**Check VPS readiness:**
```bash
ssh deploy@your-vps-ip "docker --version && docker compose version && git --version"
```

### 1.2 Create Deploy User (Non-root)
```bash
# SSH into VPS as root
ssh root@your-vps-ip

# Create deploy user
adduser --disabled-password --gecos "" deploy
usermod -aG docker deploy
usermod -aG sudo deploy

# Switch to deploy user
su - deploy
```

### 1.3 Directory Structure
```bash
# As deploy user
mkdir -p /home/deploy/showcase/{backups,logs,data}
cd /home/deploy/showcase

# Clone repo
git clone https://github.com/bhos-sec/showcase.git .

# Set permissions
chmod 700 /home/deploy/showcase
```

### 1.4 SSH Key Pair (For GitHub Actions)
```bash
# Generate ED25519 key (modern, secure)
ssh-keygen -t ed25519 \
  -C "github-actions-deploy" \
  -f ~/.ssh/github-actions \
  -N ""

# Add public key to authorized_keys
cat ~/.ssh/github-actions.pub >> ~/.ssh/authorized_keys
chmod 600 ~/.ssh/authorized_keys

# Display private key (save this for GitHub Secrets)
cat ~/.ssh/github-actions
```

**Store safely:**
- Private key → GitHub Secret: `VPS_SSH_KEY`
- Public key → Added to `~/.ssh/authorized_keys` on VPS ✓

### 1.5 Production Environment File
```bash
# Create .env.production on VPS (NEVER commit to Git)
cat > /home/deploy/showcase/.env.production << 'EOF'
# Django Settings
DEBUG=False
SECRET_KEY=$(python3 -c 'import secrets; print(secrets.token_urlsafe(50))')
ALLOWED_HOSTS=your-domain.com,www.your-domain.com,your-vps-ip

# GitHub API Integration
GITHUB_TOKEN=ghp_your_personal_access_token_here
GITHUB_ORG=bhos-sec

# Frontend Config
VITE_API_URL=https://api.your-domain.com
VITE_APP_NAME=Collective Showcase

# Redis (Message Broker)
REDIS_URL=redis://redis:6379/0
CELERY_BROKER_URL=redis://redis:6379/0
CELERY_RESULT_BACKEND=redis://redis:6379/0

# Email
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
EOF

# Secure it
chmod 600 /home/deploy/showcase/.env.production
```

---

## Phase 2: GitHub Configuration

### 2.1 Personal Access Token (For GHCR)
1. Go to GitHub → **Settings** → **Developer settings** → **Personal access tokens** → **Tokens (classic)**
2. Click **"Generate new token"**
3. Token name: `GHCR_DEPLOY_TOKEN`
4. Expiration: 90 days (rotate regularly)
5. **Scopes needed:**
   - ✅ `write:packages` — Push Docker images
   - ✅ `read:packages` — Pull Docker images
   - ✅ `repo` — Clone repo
6. Click **"Generate token"** → Copy the value

### 2.2 Repository Secrets
Go to repository → **Settings** → **Secrets and variables** → **Actions** → **New repository secret**

Add these 6 secrets:

| Secret Name | Value | Example |
|---|---|---|
| `VPS_HOST` | VPS IP or domain | `192.168.1.100` |
| `VPS_USER` | Deploy user | `deploy` |
| `VPS_PORT` | SSH port | `22` |
| `VPS_SSH_KEY` | Private SSH key (entire file) | `-----BEGIN OPENSSH PRIVATE KEY-----...` |
| `VPS_APP_PATH` | App path on VPS | `/home/deploy/showcase` |
| `GHCR_TOKEN` | Personal access token | `ghp_xxxxxxxxxxxx...` |

**Optional:**
- `SLACK_WEBHOOK` — For deployment notifications

### 2.3 Verify Secrets Are Set
```bash
# Go to repository → Settings → Secrets and variables → Actions
# You should see all 6 secrets as dots (hidden values)
```

---

## Phase 3: Docker Configuration

### 3.1 Backend Dockerfile (Production)
**File:** `docker/backend/Dockerfile.prod`

**Checklist:**
- [ ] Multi-stage build (builder + production)
- [ ] Based on `python:3.12-slim`
- [ ] Uses production requirements
- [ ] Non-root user (`django` user)
- [ ] Gunicorn as app server
- [ ] Health check included

**Current status:** ✅ Already created and ready

### 3.2 Frontend Dockerfile
**File:** `docker/frontend/Dockerfile`

**Checklist:**
- [ ] Multi-stage build (builder + nginx)
- [ ] Builder: `node:20-alpine`, runs `npm run build`
- [ ] Runtime: `nginx:alpine` serves built files
- [ ] Non-root user for nginx
- [ ] Health check included

**Current status:** ✅ Already created and ready

### 3.3 Docker Compose Production
**File:** `docker-compose.prod.yml`

**Checklist:**
- [ ] Services defined: backend, frontend (nginx), redis, db (if needed)
- [ ] Images built from Dockerfiles
- [ ] Volumes mounted for persistence
- [ ] Environment variables loaded from `.env.production`
- [ ] Health checks for critical services
- [ ] Restart policies set (`unless-stopped`)

**Current status:** ✅ Already created and ready

### 3.4 Test Docker Build Locally
```bash
# Build images
docker compose -f docker-compose.prod.yml build

# Start services
docker compose -f docker-compose.prod.yml up -d

# Check status
docker compose -f docker-compose.prod.yml ps

# View logs
docker compose -f docker-compose.prod.yml logs -f backend

# Stop
docker compose -f docker-compose.prod.yml down
```

---

## Phase 4: GitHub Actions Workflow

### 4.1 Workflow File Created
**File:** `.github/workflows/deploy.yml`

**Checklist:**
- [ ] Trigger: Push to `main` branch
- [ ] Manual trigger: `workflow_dispatch` enabled
- [ ] Build job: Builds backend & frontend images
- [ ] Push job: Pushes to GHCR with tags
- [ ] Deploy job: SSH into VPS and runs deployment script

**Current status:** ✅ Already created and ready

### 4.2 Workflow Steps Breakdown

**Build & Push Job:**
1. Checkout code
2. Setup Docker Buildx
3. Login to GHCR
4. Build backend image → Push to `ghcr.io/bhos-sec/showcase/backend:latest` & `:sha`
5. Build frontend image → Push to `ghcr.io/bhos-sec/showcase/frontend:latest` & `:sha`

**Deploy Job (on VPS):**
1. SSH into VPS
2. Pull latest code from Git
3. Source `.env.production`
4. Login to GHCR
5. Pull latest images
6. Backup database
7. Deploy containers (`docker compose up`)
8. Run migrations
9. Collect static files
10. Health check

### 4.3 Verify Workflow Syntax
```bash
# Install act (GitHub Actions local runner)
brew install act  # macOS
# or: sudo apt install act  # Linux

# Test workflow locally
act push -j build-and-push
```

---

## Phase 5: CI/CD Pipeline Testing

### 5.1 Pre-Deployment Checklist
- [ ] All 6 GitHub secrets are set
- [ ] VPS SSH key pair generated
- [ ] `.env.production` created on VPS
- [ ] Docker & Docker Compose installed on VPS
- [ ] Repository cloned on VPS
- [ ] VPS has internet access to GitHub & GHCR

### 5.2 First Deployment: Manual Trigger
1. Go to GitHub repo → **Actions** tab
2. Click **"Deploy to VPS"** on the left
3. Click **"Run workflow"** dropdown
4. Select branch: `main`
5. Click **"Run workflow"** (green button)
6. Monitor the logs

**Expected flow:**
- Build job: 3-5 minutes (building Docker images)
- Deploy job: 2-3 minutes (SSH to VPS, pull images, restart containers)

### 5.3 Monitor Logs
```
Actions → Deploy to VPS → Latest Run
├── build-and-push
│   ├── Checkout code ✅
│   ├── Set up Docker Buildx ✅
│   ├── Login to Container Registry ✅
│   ├── Build and push backend image ✅
│   └── Build and push frontend image ✅
└── deploy
    ├── Deploy to VPS ✅
    │   ├── 🚀 Starting deployment...
    │   ├── 📦 Backing up database...
    │   ├── 🔄 Redeploying containers...
    │   ├── 🗄️  Running migrations...
    │   ├── 📂 Collecting static files...
    │   ├── ✅ Verifying deployment...
    │   └── ✨ Deployment successful!
    └── Complete ✅
```

### 5.4 Test Health Endpoint
```bash
# From local machine
curl https://your-domain.com/api/health/

# Should return:
# {"status": "ok"}

# Or test from VPS directly
curl http://localhost:8000/api/health/
```

### 5.5 Verify Services Running
```bash
# SSH into VPS
ssh -i ~/.ssh/github-actions deploy@your-vps-ip

# Check services
docker compose -f docker-compose.prod.yml ps

# Expected output:
# NAME                 COMMAND              STATUS
# backend              gunicorn config...   Up (healthy)
# frontend             nginx -g daemon      Up (healthy)
# redis                redis-server         Up (healthy)

# View logs
docker compose -f docker-compose.prod.yml logs backend
```

---

## Phase 6: Automatic Deployments

### 6.1 Enable Auto-Deploy
Once manual testing passes, auto-deploy activates automatically when you push to main:

```bash
# Make a change
echo "# Updated" >> README.md

# Commit and push to main
git add .
git commit -m "test: verify auto-deployment"
git push origin main

# Watch Actions tab → Deploy to VPS workflow should trigger automatically
```

### 6.2 Commit Triggers Deployment
- **Branch:** `main` (or any branch in your workflow config)
- **Trigger:** Push or merge to main
- **Auto-deploy:** Yes, if all checks pass

### 6.3 Deployment Timeline
```
You push to main
        ↓
GitHub Actions triggers (within 30 seconds)
        ↓
Build Docker images (3-5 min)
        ↓
Push images to GHCR (~1-2 min)
        ↓
SSH deploy to VPS (2-3 min)
        ↓
Health check passes ✅
        ↓
Live on production (Total: ~8-10 minutes)
```

---

## Phase 7: Monitoring & Maintenance

### 7.1 Daily Checks
```bash
# SSH into VPS
ssh deploy@your-vps-ip

# Check all services running
docker compose -f docker-compose.prod.yml ps

# View recent logs
docker compose -f docker-compose.prod.yml logs --tail 50 backend

# Check disk space
df -h

# Check backups exist
ls -lah /home/deploy/showcase/backups/
```

### 7.2 Weekly Maintenance
```bash
# Pull latest images
docker compose -f docker-compose.prod.yml pull

# Prune old images
docker image prune -a --force

# Check for updates
git fetch origin
git log --oneline origin/main -5
```

### 7.3 Monthly Tasks
- [ ] Rotate SSH keys
- [ ] Rotate GitHub token
- [ ] Review deployment logs
- [ ] Test rollback procedure
- [ ] Optimize database (run analytics)

---

## Phase 8: Troubleshooting Guide

### Issue: Deployment Fails in GitHub Actions
**Solution:**
1. Check Actions tab → see error message
2. SSH into VPS → check Docker status
3. Verify secrets are set correctly
4. Check `.env.production` syntax

### Issue: "Permission denied (publickey)"
**Solution:**
```bash
# On VPS
cat ~/.ssh/github-actions.pub >> ~/.ssh/authorized_keys
chmod 600 ~/.ssh/authorized_keys

# Verify
ssh -i ~/.ssh/github-actions -T deploy@your-vps-ip "echo Connected"
```

### Issue: "Unable to pull image from GHCR"
**Solution:**
```bash
# Verify GHCR_TOKEN is set and has correct scopes
# On VPS, test Docker login
echo "ghp_xxxx" | docker login ghcr.io -u USERNAME --password-stdin

# Pull image manually
docker pull ghcr.io/bhos-sec/showcase/backend:latest
```

### Issue: Health Check Failed
**Solution:**
```bash
# On VPS
docker compose -f docker-compose.prod.yml logs backend

# Check if migrations ran
docker compose -f docker-compose.prod.yml exec backend python manage.py migrate --list

# Run migrations manually
docker compose -f docker-compose.prod.yml exec backend python manage.py migrate
```

---

## Phase 9: Security Hardening

### 9.1 SSH Hardening
- [ ] Use ED25519 keys (modern, secure)
- [ ] Disable password authentication
- [ ] Disabled root login
- [ ] Use non-standard SSH port (optional)

### 9.2 Secrets Management
- [ ] Never commit `.env.production` to Git
- [ ] Rotate SSH keys annually
- [ ] Rotate GitHub tokens every 90 days
- [ ] Store backup keys securely (offline)

### 9.3 Database Security
- [ ] Backups encrypted (optional)
- [ ] Database backups stored separate from data
- [ ] Tested restore procedure

### 9.4 Docker Security
- [ ] Images use non-root users
- [ ] No hardcoded secrets in images
- [ ] Regular image updates
- [ ] Dockerfile vulnerability scanning

---

## Phase 10: Rollback & Recovery

### 10.1 Quick Rollback
```bash
# On VPS
cd /home/deploy/showcase

# See recent commits
git log --oneline origin/main -10

# Checkout previous commit
git checkout PREVIOUS_COMMIT_HASH

# Redeploy
docker compose -f docker-compose.prod.yml up -d --no-deps --build

# Run migrations (if schema changed)
docker compose -f docker-compose.prod.yml exec backend python manage.py migrate
```

### 10.2 Database Rollback
```bash
# On VPS
cd /home/deploy/showcase

# List backups
ls -lah backups/

# Restore from backup
cp backups/db_20260307_120000.sqlite3 data/db.sqlite3

# Restart backend
docker compose -f docker-compose.prod.yml restart backend
```

---

## Checklist: Complete CD Pipeline

- [ ] **Phase 1:** VPS setup complete
  - [ ] Deploy user created
  - [ ] SSH key pair generated
  - [ ] `.env.production` created
  - [ ] Directory structure ready

- [ ] **Phase 2:** GitHub configuration
  - [ ] Personal access token created
  - [ ] All 6 repository secrets added
  - [ ] Secrets verified

- [ ] **Phase 3:** Docker ready
  - [ ] Backend Dockerfile.prod ✅
  - [ ] Frontend Dockerfile ✅
  - [ ] docker-compose.prod.yml ✅
  - [ ] Local build tested

- [ ] **Phase 4:** GitHub Actions workflow
  - [ ] `.github/workflows/deploy.yml` in place ✅
  - [ ] Workflow file syntax valid

- [ ] **Phase 5:** Testing
  - [ ] Manual deployment tested
  - [ ] Health check passes
  - [ ] Services running on VPS

- [ ] **Phase 6:** Auto-deploy
  - [ ] Push to main triggers deployment
  - [ ] Auto-deployments working

- [ ] **Phase 7-10:** Operations ready
  - [ ] Monitoring checks in place
  - [ ] Troubleshooting guide reviewed
  - [ ] Security hardening done
  - [ ] Rollback procedure documented

---

## Quick Reference

### Commands on VPS
```bash
# Check deployment status
docker compose -f docker-compose.prod.yml ps

# See logs
docker compose -f docker-compose.prod.yml logs -f backend

# SSH into container
docker compose -f docker-compose.prod.yml exec backend bash

# Run Django management command
docker compose -f docker-compose.prod.yml exec backend python manage.py [command]

# Stop all services
docker compose -f docker-compose.prod.yml down

# Start all services
docker compose -f docker-compose.prod.yml up -d
```

### GitHub Actions
```bash
# View workflow status
GitHub repo → Actions tab

# Manual trigger
GitHub repo → Actions → Deploy to VPS → Run workflow

# View logs
Click on workflow run → Deploy to VPS step
```

---

## Support Resources

- [DEPLOYMENT.md](DEPLOYMENT.md) — Full deployment documentation
- [CD_QUICKSTART.md](CD_QUICKSTART.md) — 5-minute setup guide
- [GitHub Actions Docs](https://docs.github.com/en/actions)
- [Docker Docs](https://docs.docker.com/)
- [Django Deployment](https://docs.djangoproject.com/en/stable/howto/deployment/)

---

**Status:** All infrastructure code is ready. Follow the phases above to complete setup.
