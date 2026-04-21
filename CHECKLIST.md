# Pre-Deployment Checklist

Use this checklist before pushing to GitHub and deploying to Render.

## Code Quality

- [ ] Run `python manage.py check` (no errors)
- [ ] Run `python manage.py test` (all pass)
- [ ] No debug print statements left in code
- [ ] No TODO/FIXME comments in production paths
- [ ] Static files collected: `python manage.py collectstatic --noinput`

## Configuration

- [ ] `.env.example` updated with all required variables
- [ ] `.gitignore` excludes `.env`, `*.pyc`, `venv/`, `db.sqlite3`, `media/`
- [ ] `DJANGO_DEBUG=False` in Render environment
- [ ] `DJANGO_SECRET_KEY` is strong (not shared)
- [ ] `ALLOWED_HOSTS` includes Render domain
- [ ] Database credentials are secure

## Deployment Files

- [ ] `Procfile` present with release and web commands
- [ ] `render.yaml` configured with correct service/database setup
- [ ] `runtime.txt` specifies Python 3.11+
- [ ] `.github/workflows/django.yml` exists for CI/CD
- [ ] `requirements.txt` pinned to specific versions (no `*`)

## Security

- [ ] No API keys/passwords in code (all in env vars)
- [ ] `SECURE_SSL_REDIRECT=True` in production
- [ ] `SESSION_COOKIE_SECURE=True` in production
- [ ] `CSRF_COOKIE_SECURE=True` in production
- [ ] HSTS headers configured
- [ ] CSP headers configured

## Database

- [ ] Migrations are up-to-date (`python manage.py migrate`)
- [ ] PostgreSQL (or configured DB engine) ready
- [ ] Database backups configured (if using Render PostgreSQL)

## Stripe (if applicable)

- [ ] Webhook endpoint configured in Stripe dashboard
- [ ] `STRIPE_PUBLIC_KEY` set
- [ ] `STRIPE_SECRET_KEY` set
- [ ] `STRIPE_WEBHOOK_SECRET` set

## GitHub

- [ ] Repository pushed to GitHub
- [ ] `main` branch is protected
- [ ] Branch has no uncommitted changes
- [ ] `.github/workflows/django.yml` will auto-test on PR

## Render Setup

- [ ] GitHub account connected to Render
- [ ] Web service created and linked to repository
- [ ] PostgreSQL database created (if needed)
- [ ] Environment variables added (via dashboard or `render.yaml`)
- [ ] Build and start commands configured

## Post-Deployment

- [ ] Visit deployed URL and verify homepage loads
- [ ] Admin portal accessible (`/admin/`)
- [ ] Create superuser in Render Shell
- [ ] Test login flow
- [ ] Verify static files load (CSS, images, JS)
- [ ] Check logs for errors
- [ ] Test Stripe payment flow (if applicable)

---

## Monitoring

- [ ] Set up Render metrics/monitoring
- [ ] Enable database backups
- [ ] Configure error notifications (email/Slack)
- [ ] Monitor logs regularly for errors

---

## Rollback Plan

If deployment fails:
1. Check Render dashboard **Deploys** tab
2. Click previous working deployment
3. Click **Redeploy**
4. Verify service is back online
5. Check logs to find issue
6. Fix locally, push to GitHub, auto-redeploy

---

Questions? See [DEPLOYMENT.md](DEPLOYMENT.md) for detailed guide.
