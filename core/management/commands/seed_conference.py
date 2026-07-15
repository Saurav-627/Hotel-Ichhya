import os
import yaml
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = (
        "Seeds conference/event venue data from seed_conference.yaml. "
        "Uses get_or_create keyed by venue name — existing venues are NEVER deleted."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--file",
            type=str,
            default="seed_conference.yaml",
            help="Path to the conference seed YAML file (default: seed_conference.yaml in project root)",
        )

    def handle(self, *args, **options):
        file_path = options["file"]

        if not os.path.exists(file_path):
            self.stderr.write(self.style.ERROR(f"Seed file not found: {file_path}"))
            return

        self.stdout.write(self.style.NOTICE(f"Loading conference data from {file_path}..."))

        with open(file_path, "r", encoding="utf-8") as f:
            try:
                data = yaml.safe_load(f)
            except yaml.YAMLError as exc:
                self.stderr.write(self.style.ERROR(f"Error parsing YAML: {exc}"))
                return

        if not data:
            self.stderr.write(self.style.ERROR("YAML file is empty."))
            return

        from conference.models.venue import EventVenue

        for venue in data.get("event_venues", []):
            name = venue.get("name")
            if not name:
                continue
            venue_obj, created = EventVenue.objects.get_or_create(
                name=name,
                defaults={
                    "description": venue.get("description", ""),
                    "capacity": venue.get("capacity", 0),
                    "layout_options": venue.get("layout_options", ""),
                    "base_price": venue.get("base_price", 0),
                    "is_active": venue.get("is_active", True),
                }
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f"Created event venue: {name}"))
            else:
                self.stdout.write(self.style.WARNING(f"Event venue '{name}' already exists. Skipping."))

        self.stdout.write(self.style.SUCCESS("\nConference venue seeding completed!"))
