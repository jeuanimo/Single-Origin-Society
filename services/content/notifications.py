from django.conf import settings
from django.core.mail import send_mail


def send_inquiry_notification(subject, message):
    recipient = getattr(settings, "DEFAULT_FROM_EMAIL", "") or "no-reply@example.com"
    send_mail(
        subject=subject,
        message=message,
        from_email=recipient,
        recipient_list=[recipient],
        fail_silently=True,
    )
