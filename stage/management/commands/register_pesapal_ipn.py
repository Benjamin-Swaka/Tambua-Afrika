"""
Run this ONCE per environment (once for sandbox, once again when you
switch to live keys) to register your IPN endpoint with Pesapal.

    python manage.py register_pesapal_ipn

Copy the printed ipn_id into your .env as PESAPAL_IPN_ID. Every ticket
payment after that reuses the same registered ID -- you don't need to
re-run this per transaction.
"""
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from stage.pesapal import register_ipn, PesapalError


class Command(BaseCommand):
    help = "Register the Pesapal IPN URL and print the ipn_id to save in .env."

    def handle(self, *args, **options):
        ipn_url = f"{settings.SITE_BASE_URL}/stage/pesapal/ipn/"

        self.stdout.write(f"Registering IPN URL: {ipn_url}")
        if settings.PESAPAL_ENV != "live":
            self.stdout.write(self.style.WARNING(
                "PESAPAL_ENV is 'sandbox' -- this registers against Pesapal's "
                "test environment. Re-run this command after switching to "
                "live keys, since sandbox and live IPN registrations are separate."
            ))

        try:
            data = register_ipn(ipn_url)
        except PesapalError as exc:
            raise CommandError(str(exc))

        self.stdout.write(self.style.SUCCESS(f"Registered. ipn_id = {data['ipn_id']}"))
        self.stdout.write("Add this to your .env file:")
        self.stdout.write(self.style.NOTICE(f"PESAPAL_IPN_ID={data['ipn_id']}"))
