# ⚡ CD Setup: Quick Start Checklist

Get your automated deployment running in 5 minutes.

## Phase 1: VPS Setup (5 min)

```bash
# 1. SSH into your VPS
ssh deploy@your-vps-ip

# 2. Create deployment SSH key
ssh-keygen -t ed25519 -C "github-actions-deploy" -f ~/.ssh/github-actions -N ""

# 3. Display the private key (copy this)
cat ~/.ssh/github-actions

# 4. Add public key to authorized_keys
cat ~/.ssh/github-actions.pub >> ~/.ssh/authorized_keys
chmod 600 ~/.ssh/authorized_keys

# 5. Create app directory
mkdir -p /home/deploy/showcase/backups
cd /home/deploy/showcase

# 6. Clone repository
git clone https://github.com/bhos-sec/showcase.git .

# 7. Create production environment file
cat > .env.production << 'EOF'
DEBUG=False
SECRET_KEY=$(python3 -c 'import secrets; print(secrets.token_urlsafe(50))')
ALLOWED_HOSTS=your-domain.com,your-vps-ip

GITHUB_TOKEN=ghp_your_token_here
GITHUB_ORG=bhos-sec

VITE_API_URL=https://api.your-domain.com
VITE_APP_NAME=Collective Showcase

REDIS_URL=redis://redis:6379/0
CELERY_BROKER_URL=redis://redis:6379/0
CELERY_RESULT_BACKEND=redis://redis:6379/0

EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
EOF

chmod 600 .env.production
```

## Phase 2: GitHub Secrets (2 min)

Go to **GitHub Repository → Settings → Secrets and variables → Actions**

Add these secrets:

```
VPS_HOST          = your-vps-ip-or-domain
VPS_USER          = deploy
VPS_PORT          = 22
VPS_APP_PATH      = /home/deploy/showcase
VPS_SSH_KEY       = [paste entire private key from ~/.ssh/github-actions]
GHCR_TOKEN        = ghp_your_personal_access_token
```

**How to get GHCR_TOKEN:**
1. Go to GitHub → Settings → Developer settings → Personal access tokens → Tokens (classic)
2. Click "Generate new token"
3. Name: `GHCR_DEPLOY`
4. Scopes: Check `write:packages`, `read:packages`, `repo`
5. Copy and paste value into `GHCR_TOKEN` secret

## Phase 3: Test Deployment (1 min)

### Option A: Manual Trigger (Recommended First Time)
1. Go to your GitHub repo → **Actions** tab
2. Click **"Deploy to VPS"** workflow on the left
3. Click **"Run workflow"** → Select branch: `main` → **"Run workflow"**
4. Monitor the logs as deployment runs (2-3 minutes)

### Option B: Automatic Deployment
1. Make a change to any file
2. Commit and push to `main` branch
3. Watch the magic happen in the Actions tab

## Phase 4: Verify Deployment

```bash
# Check health endpoint
curl https://your-domain.com/api/health/

# Should return:
# {"status": "ok"}

# SSH into VPS and check logs
ssh -i ~/.ssh/github-actions deploy@your-vps-ip
cd /home/deploy/showcase
docker compose -f docker-compose.prod.yml logs -f backend
```

---

## Troubleshooting

**"Permission denied (publickey)"**
- SSH key not added to authorized_keys
- ```bash
  cat ~/.ssh/github-actions.pub >> ~/.ssh/authorized_keys
  chmod 600 ~/.ssh/authorized_keys
  ```

**"Unable to pull image"**
- GITHUB_TOKEN doesn't have `packages:read` scope
- Verify token has correct scopes in GitHub settings

**"Health check failed"**
- Backend not running or migrations failed
- ```bash
  docker compose -f docker-compose.prod.yml logs backend
  docker compose -f docker-compose.prod.yml exec backend python manage.py migrate
  ```

---

## What Gets Deployed

Each push to `main` triggers:
1. ✅ Build backend Docker image → Push to GHCR
2. ✅ Build frontend Docker image → Push to GHCR  
3. ✅ SSH into VPS
4. ✅ Pull latest code
5. ✅ Backup database
6. ✅ Pull images from GHCR
7. ✅ Restart containers
8. ✅ Run migrations
9. ✅ Collect static files
10. ✅ Health check

---

## Security Checklist

- ✅ SSH key is Ed25519 (modern, secure)
- ✅ Private key stored ONLY in GitHub Secrets
- ✅ Deploy user is NOT root
- ✅ Database backed up before each deploy
- ✅ No secrets in Git commits (use .env.production)
- ✅ GitHub token has minimal required scopes

---

## Useful Commands

```bash
# View deployment logs
# GitHub Actions UI → Actions → Deploy to VPS workflow

# SSH into VPS and check status
ssh -i ~/.ssh/github-actions deploy@your-vps-ip
docker compose -f docker-compose.prod.yml ps

# View backend logs
docker compose -f docker-compose.prod.yml logs backend

# Manual health check
curl http://localhost:8000/api/health/

# Rollback to previous version
git log --oneline | head -5
git checkout COMMIT_HASH_TO_ROLLBACK_TO
git push --force origin main  # ⚠️ Use carefully!
```

---

## Next Steps

- [ ] Complete VPS setup (Phase 1)
- [ ] Add GitHub secrets (Phase 2)
- [ ] Test deployment (Phase 3)
- [ ] Setup domain/SSL (optional, add to Nginx config)
- [ ] Monitor first live deployments

**Questions?** See [DEPLOYMENT.md](DEPLOYMENT.md) for detailed documentation.
