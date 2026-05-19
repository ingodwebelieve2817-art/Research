"""
HOW TO USE THIS COMMAND
───────────────────────
When you are ready to add your customer dataset, prepare a CSV file with
these columns (the header row must match exactly):

    name, phone, whatsapp_number, city, service_interest

Example rows:
    Emeka Obi,+2348012345678,+2348012345678,Lagos,plumber
    Aisha Musa,+2347031234567,,Abuja,barber
    Chidi Nwosu,+2348098765432,,Kano,electrician

whatsapp_number can be left blank — the phone column will be used instead.

Then run:
    python manage.py import_customers /path/to/your/file.csv

Options:
    --clear     Delete all existing customers before importing (fresh load)
    --dry-run   Preview what would be imported without saving anything
"""
import csv
from django.core.management.base import BaseCommand, CommandError
from customers.models import Customer, SERVICE_INTEREST_CHOICES

VALID_INTERESTS = {slug for slug, _ in SERVICE_INTEREST_CHOICES}


class Command(BaseCommand):
    help = "Import customers from a CSV file into the platform dataset"

    def add_arguments(self, parser):
        parser.add_argument("csv_file", type=str, help="Path to the CSV file")
        parser.add_argument("--clear", action="store_true", help="Clear existing customers first")
        parser.add_argument("--dry-run", action="store_true", help="Preview without saving")

    def handle(self, *args, **options):
        csv_path = options["csv_file"]
        dry_run = options["dry_run"]

        try:
            file = open(csv_path, newline="", encoding="utf-8")
        except FileNotFoundError:
            raise CommandError(f"File not found: {csv_path}")

        if options["clear"] and not dry_run:
            deleted, _ = Customer.objects.all().delete()
            self.stdout.write(self.style.WARNING(f"Cleared {deleted} existing customers."))

        created = skipped = errors = 0

        with file:
            reader = csv.DictReader(file)
            for i, row in enumerate(reader, start=2):  # start=2 because row 1 is header
                name = row.get("name", "").strip()
                phone = row.get("phone", "").strip()
                whatsapp = row.get("whatsapp_number", "").strip()
                city = row.get("city", "").strip()
                interest = row.get("service_interest", "").strip().lower()

                # Basic validation
                if not all([name, phone, city, interest]):
                    self.stdout.write(self.style.ERROR(f"  Row {i}: missing field — skipped: {row}"))
                    errors += 1
                    continue

                if interest not in VALID_INTERESTS:
                    self.stdout.write(
                        self.style.ERROR(f"  Row {i}: unknown service_interest '{interest}' — skipped")
                    )
                    errors += 1
                    continue

                if dry_run:
                    self.stdout.write(f"  [DRY RUN] Would import: {name} | {phone} | {city} | {interest}")
                    created += 1
                    continue

                _, was_created = Customer.objects.update_or_create(
                    phone=phone,
                    defaults={
                        "name": name,
                        "whatsapp_number": whatsapp,
                        "city": city,
                        "service_interest": interest,
                    },
                )
                if was_created:
                    created += 1
                else:
                    skipped += 1

        label = "Would import" if dry_run else "Imported"
        self.stdout.write(self.style.SUCCESS(
            f"\nDone. {label}: {created} | Updated/skipped: {skipped} | Errors: {errors}"
        ))
