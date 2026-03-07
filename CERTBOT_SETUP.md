# SSL/TLS Setup with Certbot and System Nginx

## Architecture

```
Internet (HTTPS on 443)
    ↓
System Nginx (port 80, 443) - Reverse Proxy
    ↓
Docker Nginx (port 8001) - Inside container
    ↓
Docker Backend (8000) - Behind Docker Nginx
```

## Step-by-Step Setup

### 1. Install Certbot

```bash
sudo apt-get update
sudo apt-get install certbot python3-certbot-nginx -y
```

### 2. Create System Nginx Config

Create `/etc/nginx/sites-available/showcase`:

```bash
sudo nano /etc/nginx/sites-available/showcase
```

Paste this config:

```nginx
server {
    listen 80;
    server_name sec.bhos.tech www.sec.bhos.tech;

    location / {
        proxy_pass http://localhost:8001;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### 3. Enable the Config

```bash
sudo ln -s /etc/nginx/sites-available/showcase /etc/nginx/sites-enabled/showcase
sudo nginx -t
sudo systemctl reload nginx
```

### 4. Get SSL Certificate

```bash
sudo certbot --nginx -d sec.bhos.tech -d www.sec.bhos.tech
```

**Follow prompts:**
- Email: your-email@example.com
- Agree to terms (A)
- Share email (Y or N)
- Redirect HTTP to HTTPS (2 - recommended)

### 5. Verify Cert

```bash
sudo certbot certificates
```

Should show:
```
Certificate Name: sec.bhos.tech
  Domains: sec.bhos.tech, www.sec.bhos.tech
  Expiry Date: 2026-06-05
```

### 6. Auto-Renewal Setup

```bash
sudo systemctl enable certbot.timer
sudo systemctl start certbot.timer

# Check renewal schedule
sudo systemctl list-timers certbot.timer
```

### 7. Test Auto-Renewal (Don't Actually Renew)

```bash
sudo certbot renew --dry-run
```

## Enabling SECURE_SSL_REDIRECT

Before SSL is configured, keep `SECURE_SSL_REDIRECT=False` in `.env.production` to allow HTTP health checks during deployment.

**After Certbot is fully configured and working:**

1. SSH into your VPS
2. Edit `.env.production`:
   ```bash
   nano /home/deploy/showcase/.env.production
   ```
3. Change `SECURE_SSL_REDIRECT=False` to `SECURE_SSL_REDIRECT=True`
4. Save and exit
5. Push a new commit or manually restart: `docker compose -f docker-compose.prod.yml --env-file .env.production restart backend`

## Environment Variables for Backend

Once SSL is configured, `.env.production` should have:

```bash
SECURE_SSL_REDIRECT=True
SECURE_HSTS_SECONDS=31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS=True
SECURE_HSTS_PRELOAD=True
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True
```

## Testing SSL

```bash
# Check SSL on command line
curl -I https://sec.bhos.tech

# Or visit in browser
https://sec.bhos.tech
```

## Troubleshooting

**Port 80 still in use:**
```bash
sudo ss -tlnp | grep :80
sudo systemctl status nginx
```

**Certificate renewal issues:**
```bash
sudo certbot renew -v
```

**View nginx error logs:**
```bash
sudo tail -f /var/log/nginx/error.log
```

## Certificate Expiry Reminder

Certbot auto-renewal checks daily. You'll get email reminders before expiry from Let's Encrypt.

Manual renewal (if needed):
```bash
sudo certbot renew --force-renewal
sudo systemctl reload nginx
```
