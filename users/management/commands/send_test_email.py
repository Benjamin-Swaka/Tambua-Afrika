"""
Quick sanity check for SMTP email delivery.

Usage:
    python manage.py send_test_email you@example.com
"""
from django.conf import settings
from django.core.mail import send_mail
from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    help = "Send a test email to confirm SMTP credentials actually work."

    def add_arguments(self, parser):
        parser.add_argument("to_email", type=str, help="Address to send the test email to.")

    def handle(self, *args, **options):
        to_email = options["to_email"]

        if settings.EMAIL_BACKEND.endswith("console.EmailBackend"):
            self.stdout.write(self.style.WARNING(
                "You're on the console email backend right now (no real SMTP "
                "credentials configured), so this will just print below "
                "instead of actually sending anywhere. Set EMAIL_HOST_USER "
                "and EMAIL_HOST_PASSWORD in your .env first."
            ))

        try:
            sent = send_mail(
                subject="Tambua Afrika - Test Email",
                message="If you're reading this in your inbox, SMTP is configured correctly.",
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[to_email],
                fail_silently=False,
            )
        except Exception as exc:
            raise CommandError(f"Sending failed: {exc}")

        if sent:
            self.stdout.write(self.style.SUCCESS(f"Test email sent to {to_email}."))
        else:
            self.stdout.write(self.style.ERROR("send_mail() returned 0 -- nothing was sent."))
