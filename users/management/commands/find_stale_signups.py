"""
Diagnose / clean up 'account already exists' false positives.

Because ACCOUNT_EMAIL_VERIFICATION is 'mandatory' with enumeration
prevention on, allauth intentionally shows the exact same "check your
email" screen whether or not an address is already registered -- it
does NOT tell a signup attempt "that email is taken" on screen. So if a
real first-time user is seeing an "account already exists" message,
the most likely explanation is that a User + EmailAddress row for that
email already exists in the database (e.g. left over from an abandoned
signup attempt, a seed/test account, or an import) and was never
verified.

Usage:
    python manage.py find_stale_signups            # just list them
    python manage.py find_stale_signups --delete    # delete unverified duplicates older than 24h
"""
from datetime import timedelta

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone

from allauth.account.models import EmailAddress


class Command(BaseCommand):
    help = "Find (and optionally delete) stale, never-verified signup accounts."

    def add_arguments(self, parser):
        parser.add_argument(
            "--delete",
            action="store_true",
            help="Delete stale unverified accounts instead of just listing them.",
        )
        parser.add_argument(
            "--older-than-hours",
            type=int,
            default=24,
            help="Only consider accounts created more than N hours ago (default: 24).",
        )
        parser.add_argument(
            "--email",
            type=str,
            default=None,
            help="Only check a specific email address.",
        )

    def handle(self, *args, **options):
        cutoff = timezone.now() - timedelta(hours=options["older_than_hours"])

        qs = User.objects.filter(
            date_joined__lt=cutoff,
            is_staff=False,
            is_superuser=False,
        ).exclude(
            emailaddress__verified=True,
        )

        if options["email"]:
            qs = qs.filter(email__iexact=options["email"])

        if not qs.exists():
            self.stdout.write(self.style.SUCCESS("No stale unverified accounts found."))
            return

        self.stdout.write(f"Found {qs.count()} stale unverified account(s):\n")
        for user in qs:
            self.stdout.write(f"  - {user.email} (joined {user.date_joined:%Y-%m-%d %H:%M})")

        if options["delete"]:
            count = qs.count()
            emails = list(qs.values_list("email", flat=True))
            EmailAddress.objects.filter(user__in=qs).delete()
            qs.delete()
            self.stdout.write(self.style.WARNING(
                f"\nDeleted {count} stale account(s): {', '.join(emails)}"
            ))
            self.stdout.write("Those emails can now be used to sign up fresh.")
        else:
            self.stdout.write(self.style.NOTICE(
                "\nRun again with --delete to remove these and free up their email addresses."
            ))
