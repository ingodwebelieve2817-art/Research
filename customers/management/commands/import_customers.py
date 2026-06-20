"""
HOW TO USE THIS COMMAND
───────────────────────
Prepare a CSV file with these columns (header row must match exactly):

    name, phone, whatsapp_number, city

Example rows:
    Emeka Obi,+2348012345678,+2348012345678,Lagos
    Aisha Musa,+2347031234567,,Abuja
    Chidi Nwosu,+2348098765432,,Kano

whatsapp_number can be left blank — the phone column will be used instead.

Then run:
    python manage.py import_customers /path/to/your/file.csv

Options:
    --clear     Delete all existing customers before importing (fresh load)
    --dry-run   Preview what would be imported without saving anything
"""
import csv
from django.core.management.base import BaseCommand, CommandError
from customers.models import Customer


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

        created = updated = errors = 0

        with file:
            reader = csv.DictReader(file)
            for i, row in enumerate(reader, start=2):
                name = row.get("name", "").strip()
                phone = row.get("phone", "").strip()
                whatsapp = row.get("whatsapp_number", "").strip()
                city = row.get("city", "").strip()

                if not all([name, phone, city]):
                    self.stdout.write(self.style.ERROR(
                        f"  Row {i}: missing name/phone/city — skipped: {row}"
                    ))
                    errors += 1
                    continue

                if dry_run:
                    self.stdout.write(f"  [DRY RUN] Would import: {name} | {phone} | {city}")
                    created += 1
                    continue

                _, was_created = Customer.objects.update_or_create(
                    phone=phone,
                    defaults={"name": name, "whatsapp_number": whatsapp, "city": city},
                )
                if was_created:
                    created += 1
                else:
                    updated += 1

        label = "Would import" if dry_run else "Imported"
        self.stdout.write(self.style.SUCCESS(
            f"\nDone. {label}: {created} new | {updated} updated | {errors} errors"
        ))
