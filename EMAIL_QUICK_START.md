# Email Setup Summary

Your Single Origin Society project now has complete email functionality configured and tested. Here's what was set up:

---

## ✅ What Was Installed

### Email Service Providers (Choose One)

- **SendGrid** (recommended for production)
- **Gmail SMTP** (good for testing/small volume)
- **Mailgun SMTP** (professional option)
- **Console Backend** (development mode - prints to console)

### Configuration Files

- ✅ `sos_project/settings.py` - Email backend configuration
- ✅ `.env.example` - Environment variable templates  
- ✅ `services/content/notifications.py` - Email sending functions
- ✅ `services/management/commands/send_test_email.py` - Testing command
- ✅ `requirements.txt` - Added `sendgrid-django` package
- ✅ `EMAIL_SETUP.md` - Comprehensive email guide

### Email Functions Available

```python
from services.content.notifications import (
    send_welcome_email,              # New user registration
    send_order_confirmation,         # After purchase
    send_password_reset,             # Password recovery
    send_support_ticket_confirmation,# Support inquiries
    send_wholesale_inquiry_confirmation,
    send_ambassador_inquiry_confirmation,
)
```

---

## 🚀 Quick Start (Development)

### Test Email Immediately

```bash
python manage.py send_test_email your-email@example.com
```

Output will show email content (console backend).

---

## 📧 Configure for Production

### Option 1: SendGrid (Recommended)

1. Sign up: https://sendgrid.com (free tier available)
2. Create API key in Dashboard → Settings → API Keys
3. Add to `.env`:
   ```
   SENDGRID_API_KEY=SG.xxxxxxxxxxxxxxxxxxxxxxxxxxxx
   ```
4. Test:
   ```bash
   python manage.py send_test_email your-email@example.com
   ```

### Option 2: Gmail

1. Enable 2-Factor Authentication: https://myaccount.google.com/security
2. Create App Password: https://myaccount.google.com/apppasswords
3. Add to `.env`:
   ```
   EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
   EMAIL_HOST=smtp.gmail.com
   EMAIL_PORT=587
   EMAIL_USE_TLS=True
   EMAIL_HOST_USER=your-gmail@gmail.com
   EMAIL_HOST_PASSWORD=your-app-password
   DEFAULT_FROM_EMAIL=your-gmail@gmail.com
   ```
4. Test:
   ```bash
   python manage.py send_test_email your-email@example.com
   ```

### Option 3: Custom SMTP

```bash
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=your.smtp.server
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-user
EMAIL_HOST_PASSWORD=your-password
```

---

## 🔧 Render Deployment

Add these environment variables in Render dashboard:

**For SendGrid:**
```
SENDGRID_API_KEY=SG.xxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

**For Gmail/SMTP:**
```
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-gmail@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
DEFAULT_FROM_EMAIL=your-gmail@gmail.com
```

Then test in Render Shell:
```bash
python manage.py send_test_email your-email@example.com
```

---

## 📝 Using Email in Your Code

### Send Email After Registration

```python
from django.contrib.auth import get_user_model
from services.content.notifications import send_welcome_email

User = get_user_model()

# In your registration view:
user = User.objects.create_user(...)

try:
    send_welcome_email(user)
except Exception as e:
    print(f"Email failed (non-blocking): {e}")
```

### Send Order Confirmation

```python
from services.content.notifications import send_order_confirmation

# After order creation:
send_order_confirmation(order)
```

### Send Password Reset

```python
from services.content.notifications import send_password_reset

reset_link = f"https://yourdomain.com/reset/{token}/"
send_password_reset(user, reset_link)
```

### Add Custom Email

```python
from django.core.mail import send_mail
from django.conf import settings

send_mail(
    subject="Your Subject",
    message="Your message",
    from_email=settings.DEFAULT_FROM_EMAIL,
    recipient_list=["recipient@example.com"],
    fail_silently=False,  # Raises exception on error
)
```

---

## 🧪 Testing

### Local Development

1. **Console mode (default in DEBUG):**
   ```
   Email prints to console instead of sending
   ```

2. **Test command:**
   ```bash
   python manage.py send_test_email test@example.com
   ```

3. **Check configuration:**
   ```bash
   python manage.py shell
   ```
   ```python
   from django.conf import settings
   print(settings.EMAIL_BACKEND)
   print(settings.DEFAULT_FROM_EMAIL)
   ```

---

## 🚨 Troubleshooting

**"Connection refused" error:**
- Verify `EMAIL_HOST` and `EMAIL_PORT` in `.env`
- Ensure network allows outbound port 587

**"Authentication failed":**
- For Gmail: use App Password (not regular password)
- For SendGrid: verify API key format (starts with `SG.`)
- Check `EMAIL_HOST_USER` and `EMAIL_HOST_PASSWORD`

**Email not sending:**
- Verify backend is configured: `python manage.py send_test_email test@example.com`
- Check logs for errors
- Ensure `DEFAULT_FROM_EMAIL` is a valid address

**"TLS required" error:**
- Set `EMAIL_USE_TLS=True` in `.env`

---

## 📖 Full Documentation

See [EMAIL_SETUP.md](EMAIL_SETUP.md) for:
- Detailed setup for each provider
- Advanced configuration options
- Monitoring and logging
- Best practices
- Full API reference

---

## ✨ Next Steps

1. **Choose your email provider** (SendGrid or Gmail recommended)
2. **Add credentials to `.env`**
3. **Test with `python manage.py send_test_email your-email@example.com`**
4. **Integrate email functions** into your views/signals
5. **Deploy to Render** with environment variables set

---

## Questions?

- Check [EMAIL_SETUP.md](EMAIL_SETUP.md) for comprehensive guide
- Test locally first: `python manage.py send_test_email`
- Review Django email docs: https://docs.djangoproject.com/en/6.0/topics/email/

Happy emailing! 🎉
