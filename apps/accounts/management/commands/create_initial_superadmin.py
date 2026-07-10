import getpass

from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.core.management.base import BaseCommand, CommandError

from apps.accounts.models import User


class Command(BaseCommand):
    help = (
        "Interactively create the first super_admin account. Refuses to run "
        "if a super_admin already exists, and never accepts a password as a "
        "command-line argument (avoids leaking it into shell history)."
    )

    def handle(self, *args, **options):
        if User.objects.filter(role=User.Role.SUPER_ADMIN).exists():
            raise CommandError(
                "A super_admin already exists. Use Django Admin to manage roles from here on."
            )

        email = input("Email: ").strip().lower()
        if not email:
            raise CommandError("Email is required.")
        if User.objects.filter(email=email).exists():
            raise CommandError(f"A user with email {email!r} already exists.")

        full_name = input("Full name: ").strip()
        if not full_name:
            raise CommandError("Full name is required.")

        password = getpass.getpass("Password: ")
        password_confirm = getpass.getpass("Confirm password: ")
        if password != password_confirm:
            raise CommandError("Passwords do not match.")

        try:
            validate_password(password)
        except ValidationError as exc:
            raise CommandError("\n".join(exc.messages))

        user = User.objects.create_superuser(email=email, password=password, full_name=full_name)
        self.stdout.write(self.style.SUCCESS(f"Super admin created: {user.email}"))
