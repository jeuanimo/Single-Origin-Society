# Email Configuration Guide

This guide explains how to set up and use email in Single Origin Society.

---

## Email Backends

Single Origin Society supports multiple email backends:

### 1. **SendGrid (Recommended for Production)**

**Pros:**
- Professional email delivery
- Reliable webhook support for transactional emails
- Built-in analytics and monitoring
- Free tier available (100 emails/day)
- Best for Render deployment

**Setup:**

1. Create a free SendGrid account: https://sendgrid.com
2. Generate an API key in Dashboard → Settings → API Keys
3. Add to `.env`:
   ```
   SENDGRID_API_KEY=SG.xxxxxxxxxxxxxxxxxxxxxxxxxxxx
   ```
4. Render setup:
   ```
   Environment variable: SENDGRID_API_KEY=<your-key>
   ```
5. Install package:
   ```bash
   pip install sendgrid-django
   ```

### 2. **Gmail SMTP**

**Pros:**
- Free and simple
- Good for testing
- Works immediately

**Cons:**
- Limited to 500 emails/day (free account)
- Less suitable for high-volume production

**Setup:**

1. Enable 2-Factor Authentication on your Gmail account
2. Create an App Password: https://myaccount.google.com/apppasswords
3. Add to `.env`:
   ```
   EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
   EMAIL_HOST=smtp.gmail.com
   EMAIL_PORT=587
   EMAIL_USE_TLS=True
   EMAIL_HOST_USER=your-email@gmail.com
   EMAIL_HOST_PASSWORD=your-app-specific-password
   DEFAULT_FROM_EMAIL=your-email@gmail.com
   ```

### 3. **Mailgun SMTP**

**Pros:**
- Professional email service
- Good for production
- Pay-as-you-go pricing

**Setup:**

1. Create Mailgun account: https://mailgun.com
2. Get SMTP credentials from Mailgun dashboard
3. Add to `.env`:
   ```
   EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
   EMAIL_HOST=smtp.mailgun.org
   EMAIL_PORT=587
   EMAIL_USE_TLS=True
   EMAIL_HOST_USER=postmaster@your-domain.mailgun.org
   EMAIL_HOST_PASSWORD=your-mailgun-password
   ```

### 4. **Console Backend (Development Only)**

Emails print to console instead of being sent (default in DEBUG mode).

```bash
# To use explicitly:
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
```

---

## Configuration

### Required Environment Variables

```env
# Always required
DEFAULT_FROM_EMAIL=noreply@singleoriginsociety.com
SERVER_EMAIL=admin@singleoriginsociety.com

# Required for SendGrid
SENDGRID_API_KEY=SG.xxx

# Required for SMTP
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-password
```

### Django Settings

Email configuration is in `sos_project/settings.py`:

```python
# Auto-select backend based on environment
EMAIL_BACKEND = os.environ.get(
    "EMAIL_BACKEND",
    "django.core.mail.backends.console.EmailBackend" if DEBUG 
    else "django.core.mail.backends.smtp.EmailBackend"
)

# SendGrid overrides (if API key provided)
if os.environ.get("SENDGRID_API_KEY"):
    EMAIL_BACKEND = "sendgrid_backend.SendgridBackend"
    SENDGRID_API_KEY = os.environ.get("SENDGRID_API_KEY")

# SMTP configuration
EMAIL_HOST = os.environ.get("EMAIL_HOST", "smtp.gmail.com")
EMAIL_PORT = int(os.environ.get("EMAIL_PORT", "587"))
EMAIL_USE_TLS = os.environ.get("EMAIL_USE_TLS", "True").lower() in ("true", "1")
EMAIL_HOST_USER = os.environ.get("EMAIL_HOST_USER", "")
EMAIL_HOST_PASSWORD = os.environ.get("EMAIL_HOST_PASSWORD", "")
DEFAULT_FROM_EMAIL = os.environ.get("DEFAULT_FROM_EMAIL", "noreply@singleoriginsociety.com")
SERVER_EMAIL = os.environ.get("SERVER_EMAIL", DEFAULT_FROM_EMAIL)
```

---

## Using Email Functions

### Import the Notifications Module

```python
from services.content.notifications import (
    send_order_confirmation,
    send_password_reset,
    send_welcome_email,
    send_support_ticket_confirmation,
    send_wholesale_inquiry_confirmation,
    send_ambassador_inquiry_confirmation,
)
```

### Send Order Confirmation

```python
from services.content.notifications import send_order_confirmation

# After order creation
send_order_confirmation(order)
```

### Send Welcome Email

```python
from services.content.notifications import send_welcome_email

# After user registration
send_welcome_email(user)
```

### Send Password Reset

```python
from services.content.notifications import send_password_reset

# When user requests password reset
reset_link = f"https://yourdomain.com/reset/{token}/"
send_password_reset(user, reset_link)
```

### Send Support Ticket Confirmation

```python
from services.content.notifications import send_support_ticket_confirmation

# After support ticket creation
send_support_ticket_confirmation(ticket)
```

### Send Custom Email

```python
from django.core.mail import send_mail
from django.conf import settings

send_mail(
    subject="Your Subject",
    message="Your message body",
    from_email=settings.DEFAULT_FROM_EMAIL,
    recipient_list=["recipient@example.com"],
    fail_silently=False,  # Raise exception on error
)
```

---

## Testing Email

### Option 1: Use Console Backend (Development)

Set `EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend` in `.env`

Emails will print to console instead of sending.

### Option 2: Send Test Email

```bash
python manage.py send_test_email your-email@example.com
```

This command:
- Tests your email configuration
- Verifies credentials are correct
- Confirms email backend is working

Expected output:
```
✓ Test email sent successfully to your-email@example.com
```

### Option 3: Use Django Shell

```bash
python manage.py shell
```

```python
from django.core.mail import send_mail
from django.conf import settings

send_mail(
    subject="Test Email",
    message="This is a test.",
    from_email=settings.DEFAULT_FROM_EMAIL,
    recipient_list=["your-email@example.com"],
)
```

---

## Integrating with Views

### Example: Send Welcome Email After Registration

```python
# In accounts/views.py
from django.contrib.auth import get_user_model
from services.content.notifications import send_welcome_email

User = get_user_model()

def register_view(request):
    if request.method == "POST":
        # ... create user ...
        user = User.objects.create_user(...)
        
        # Send welcome email
        try:
            send_welcome_email(user)
        except Exception as e:
            # Log error but don't break registration
            print(f"Failed to send welcome email: {e}")
        
        return redirect("login")
    
    return render(request, "register.html")
```

### Example: Send Order Confirmation

```python
# In checkout/views.py
from services.content.notifications import send_order_confirmation

def checkout_success(request):
    order = Order.objects.get(pk=request.GET.get("order_id"))
    
    # Send confirmation email
    try:
        send_order_confirmation(order)
    except Exception as e:
        # Log but don't break the flow
        print(f"Failed to send order confirmation: {e}")
    
    return render(request, "checkout_success.html", {"order": order})
```

---

## Monitoring & Troubleshooting

### Check Email Configuration

```bash
python manage.py shell
```

```python
from django.conf import settings

print(f"Backend: {settings.EMAIL_BACKEND}")
print(f"From Email: {settings.DEFAULT_FROM_EMAIL}")
print(f"SMTP Host: {settings.EMAIL_HOST}")
print(f"SMTP Port: {settings.EMAIL_PORT}")
print(f"Use TLS: {settings.EMAIL_USE_TLS}")
```

### Common Issues

**Issue: "Connection refused"**
- Verify `EMAIL_HOST` and `EMAIL_PORT` are correct
- Check if SMTP server is accessible from your network
- Ensure firewall allows outbound port 587 or 465

**Issue: "Authentication failed"**
- Verify `EMAIL_HOST_USER` and `EMAIL_HOST_PASSWORD`
- For Gmail: use App Password, not regular password
- For SendGrid: verify API key format starts with `SG.`

**Issue: "TLS required"**
- Set `EMAIL_USE_TLS=True` in `.env`
- Or use port 465 with SSL (requires `EMAIL_USE_SSL=True`)

**Issue: "Email bounced"**
- Check `DEFAULT_FROM_EMAIL` is a valid verified sender
- For SendGrid: verify sender domain in Sender Authentication
- For Gmail: use your actual Gmail address

---

## Render Deployment

### Add Environment Variables

In Render dashboard → Environment:

1. **SendGrid Option:**
   ```
   SENDGRID_API_KEY=SG.xxxxxxxxxxxxxxxxxxxxxxxxxxxx
   ```

2. **SMTP Option:**
   ```
   EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
   EMAIL_HOST=smtp.gmail.com
   EMAIL_PORT=587
   EMAIL_USE_TLS=True
   EMAIL_HOST_USER=your-email@gmail.com
   EMAIL_HOST_PASSWORD=your-app-password
   DEFAULT_FROM_EMAIL=your-email@gmail.com
   ```

3. **Always Set:**
   ```
   DEFAULT_FROM_EMAIL=noreply@singleoriginsociety.com
   SERVER_EMAIL=admin@singleoriginsociety.com
   ```

### Test in Production

```bash
# In Render Shell:
python manage.py send_test_email your-email@example.com
```

---

## Best Practices

1. **Use try/except** when sending emails so failures don't break application
2. **Set `fail_silently=False`** during development to catch errors
3. **Monitor email logs** for bounces and delivery issues
4. **Use SendGrid for production** - more reliable than Gmail
5. **Verify sender domain** to improve deliverability
6. **Add unsubscribe links** for marketing emails (if applicable)
7. **Test thoroughly** before going live

---

## Additional Resources

- [Django Email Documentation](https://docs.djangoproject.com/en/6.0/topics/email/)
- [SendGrid Documentation](https://docs.sendgrid.com/)
- [Gmail App Passwords](https://support.google.com/accounts/answer/185833)
- [Mailgun Documentation](https://documentation.mailgun.com/)

---

## Support

If you encounter issues:
1. Check logs: `python manage.py send_test_email test@example.com`
2. Verify environment variables are set
3. Ensure email backend package is installed
4. Check provider's dashboard for errors/logs
