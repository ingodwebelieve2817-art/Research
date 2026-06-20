import sys
from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth import get_user_model

User = get_user_model()


class Command(BaseCommand):
    help = "Creates a single Super Admin (superuser) account in the system."

    def handle(self, *args, **options):
        # 1. Enforce that only one Super Admin can exist initially
        superuser_exists = User.objects.filter(is_superuser=True).exists()
        if superuser_exists:
            self.stdout.write(
                self.style.WARNING(
                    "A Super Admin account already exists. Only one Super Admin account is permitted."
                )
            )
            return

        self.stdout.write(self.style.SUCCESS("--- Creating the Single Super Admin Account ---"))

        # 2. Collect inputs interactively
        username = input("Username: ").strip()
        if not username:
            raise CommandError("Username cannot be blank.")

        if User.objects.filter(username=username).exists():
            raise CommandError(f"A user with username '{username}' already exists.")

        email = input("Email address: ").strip()
        if not email:
            raise CommandError("Email address cannot be blank.")

        password = input("Password: ").strip()
        if not password or len(password) < 6:
            raise CommandError("Password must be at least 6 characters long.")

        confirm_password = input("Confirm Password: ").strip()
        if password != confirm_password:
            raise CommandError("Passwords do not match.")

        # 3. Create the superuser
        try:
            user = User.objects.create_superuser(
                username=username,
                email=email,
                password=password,
                is_active=True,
            )
            self.stdout.write(
                self.style.SUCCESS(
                    f"Super Admin account successfully created for '{user.username}'."
                )
            )
        except Exception as e:
            raise CommandError(f"Failed to create Super Admin: {str(e)}")
