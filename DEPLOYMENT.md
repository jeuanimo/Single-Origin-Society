# Deploying Single Origin Society to Render

This guide walks you through publishing the Single Origin Society Django project to Render.com via GitHub.

## Prerequisites

- GitHub account with the project repository
- Render.com account (free tier available)
- Stripe keys (test or live)

---

## Step 1: Prepare the GitHub Repository

### 1a. Initialize/Update Git

```bash
cd "Single Origin Society"

# If not already initialized
git init
git add .
git commit -m "Initial commit: Single Origin Society e-commerce platform"

# Add GitHub remote
git remote add origin https://github.com/YOUR_USERNAME/single-origin-society.git
git branch -M main
git push -u origin main
```

### 1b. Verify .gitignore

Ensure your `.gitignore` excludes:
- `.env` (never commit secrets)
- `venv/` / `env/`
- `*.pyc` / `__pycache__/`
- `db.sqlite3`
- `media/` (optional for production uploads)
- `.vscode/`

---

## Step 2: Set Up Render Deployment

### 2a. Connect GitHub to Render

1. Log in to [Render.com](https://render.com)
2. Click **New +** → **Web Service**
3. Select **Build and deploy from a Git repository**
4. Authorize Render to access your GitHub account
5. Select the `single-origin-society` repository
6. Connect

### 2b. Configure the Web Service

**Name:** `single-origin-society` (or your preferred name)

**Environment:** `Python 3`

**Build Command:** (should auto-detect from Procfile/render.yaml)
```
pip install --upgrade pip && pip install -r requirements.txt && python manage.py collectstatic --noinput
```

**Start Command:** (auto-detected)
```
gunicorn sos_project.wsgi:application
```

**Plan:** Free or Pro (depending on needs)

### 2c. Add Environment Variables

In Render dashboard, go to **Environment** and add:

| Key | Value |
|-----|-------|
| `DJANGO_DEBUG` | `False` |
| `DJANGO_ALLOWED_HOSTS` | `your-service.onrender.com` |
| `DJANGO_SECRET_KEY` | *Generate a new strong key* |
| `STRIPE_PUBLIC_KEY` | `pk_test_...` or `pk_live_...` |
| `STRIPE_SECRET_KEY` | `sk_test_...` or `sk_live_...` |
| `STRIPE_WEBHOOK_SECRET` | `whsec_...` |

**Database variables** (if using Render PostgreSQL):
- `DB_ENGINE`: `django.db.backends.postgresql`
- `DB_HOST`: *auto-populated if attached*
- `DB_NAME`: *auto-populated*
- `DB_USER`: *auto-populated*
- `DB_PASSWORD`: *auto-populated*
- `DB_PORT`: `5432`

### 2d. Add PostgreSQL Database (Recommended)

1. On Render dashboard, click **New +** → **PostgreSQL**
2. Name: `single-origin-society-db`
3. Region: same as your web service
4. PostgreSQL Version: 15
5. Click **Create Database**
6. Copy the connection string
7. On your web service, go to **Environment** and click **Add from Database**
8. Select the database you just created

---

## Step 3: Deploy

### 3a. Trigger Initial Deployment

1. Render auto-deploys on every `git push` to `main`
2. Or manually click **Manual Deploy** → **Deploy latest commit** in Render dashboard

### 3b. Monitor Logs

- View deployment logs in Render dashboard
- Common issues:
  - **Static files not found**: Ensure `python manage.py collectstatic` ran
  - **Database connection failed**: Verify environment variables match database
  - **500 errors**: Check logs; likely SECRET_KEY or database issue

### 3c. Run Migrations

After first deployment, Render typically runs the release command (from Procfile):

```
release: python manage.py migrate
```

If migrations don't auto-run, open Render shell and manually migrate:

```bash
# In Render dashboard, go to Shell
python manage.py migrate
python manage.py createsuperuser
```

---

## Step 4: Post-Deployment Configuration

### 4a. Create Superuser

```bash
# Via Render Shell (in Render dashboard)
python manage.py createsuperuser
# Follow prompts for email and password
```

### 4b. Configure Site Domain

1. Visit your deployed URL: `https://your-service.onrender.com`
2. Verify homepage loads correctly
3. Update `DJANGO_ALLOWED_HOSTS` if using custom domain

### 4c. Set Up Stripe Webhook

1. Go to [Stripe Dashboard](https://dashboard.stripe.com/webhooks)
2. Create new endpoint
3. URL: `https://your-service.onrender.com/stripe/webhook/`
4. Events: Select `payment_intent.succeeded`, `charge.refunded`, etc.
5. Copy the signing secret to Render environment as `STRIPE_WEBHOOK_SECRET`

### 4d. Access Admin Portal

- URL: `https://your-service.onrender.com/admin/`
- Login with your superuser credentials
- Verify all apps are installed and running

---

## Step 5: Continuous Deployment

### 5a. GitHub Integration

Render automatically deploys on `git push` to your connected branch:

```bash
# Make code changes locally
git add .
git commit -m "Feature: add new product filter"
git push origin main

# Render auto-builds and deploys within seconds
```

### 5b. Rollback

If a deployment breaks:
1. Go to Render dashboard → **Deploys**
2. Click previous successful deployment
3. Click **Redeploy**

---

## Troubleshooting

### Issue: Static Files Return 404

**Solution:** Ensure `STATIC_ROOT` and `STATIC_URL` are configured correctly.

```bash
# In Render Shell:
python manage.py collectstatic --noinput --clear
```

### Issue: Database Connection Refused

**Solution:** Verify `DB_HOST`, `DB_NAME`, `DB_USER`, `DB_PASSWORD` are set correctly.

```bash
# In Render Shell, test connection:
python manage.py dbshell
```

### Issue: SECRET_KEY Warning in Logs

**Solution:** Generate a strong random key in Render environment variables.

```python
# In Python:
from django.core.management.utils import get_random_secret_key
print(get_random_secret_key())
```

### Issue: CORS or CSRF Errors

**Solution:** Verify `DJANGO_ALLOWED_HOSTS` includes your Render domain:

```
DJANGO_ALLOWED_HOSTS=your-service.onrender.com
```

---

## Performance & Scaling

- **Free tier:** Spins down after 15 minutes of inactivity (cold start ~30s)
- **Pro/Standard:** Always running, faster response times
- **Database:** Free PostgreSQL limited to 1GB; upgrade for production data
- **Media uploads:** Consider S3 or similar for production

---

## Backup & Monitoring

### Enable Backups

1. Render dashboard → Your PostgreSQL database
2. Click **Settings** → **Automated Backups**
3. Enable daily automated backups

### View Metrics

- Render dashboard shows CPU, memory, and request metrics
- Check logs for errors and performance issues

---

## Next Steps

1. **Custom Domain:** Render dashboard → your service → Settings → Custom Domain
2. **SSL/TLS:** Auto-enabled by Render (free Let's Encrypt)
3. **Email:** Integrate SendGrid, Mailgun, or similar for transactional emails
4. **Monitoring:** Set up alerts in Render dashboard

---

## Support

- [Render Docs](https://render.com/docs)
- [Django Deployment Checklist](https://docs.djangoproject.com/en/6.0/howto/deployment/checklist/)
- GitHub Issues for project-specific problems

Good luck with your deployment! 🚀
