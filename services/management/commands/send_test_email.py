from django.core.management.base import BaseCommand
from django.conf import settings
from django.core.mail import send_mail


class Command(BaseCommand):
    help = "Test email configuration by sending a test email"

    def add_arguments(self, parser):
        parser.add_argument(
            "recipient",
            type=str,
            help="Email address to send test email to",
        )

    def handle(self, *args, **options):
        recipient = options["recipient"]
        subject = "Test Email from Single Origin Society"
        message = f"""
This is a test email from your Single Origin Society Django application.

If you're receiving this, your email configuration is working correctly!

Email Backend: {settings.EMAIL_BACKEND}
From Email: {settings.DEFAULT_FROM_EMAIL}

Test completed at: {settings.EMAIL_HOST}

Best regards,
Single Origin Society System
        """.strip()

        try:
            send_mail(
                subject=subject,
                message=message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[recipient],
                fail_silently=False,
            )
            self.stdout.write(
                self.style.SUCCESS(f"✓ Test email sent successfully to {recipient}")
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f"✗ Failed to send test email: {str(e)}")
            )
