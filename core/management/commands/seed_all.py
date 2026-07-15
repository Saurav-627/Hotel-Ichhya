from django.core.management.base import BaseCommand
from django.core.management import call_command


class Command(BaseCommand):
    help = (
        "Runs all seed and import commands in the correct order from their YAML files. "
        "Safe to run multiple times — existing records are always skipped, never deleted.\n\n"
        "  1. import_initial_data  (initial_data.yaml   — currencies, settings, nav, SEO banners)\n"
        "  2. seed_data            (seed_data.yaml       — rooms, dining, recreation, gallery, etc.)\n"
        "  3. seed_conference      (seed_conference.yaml — conference/event venue halls)\n"
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--update",
            action="store_true",
            default=False,
            help="Pass --update to import_initial_data to overwrite existing records there.",
        )

    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE("=" * 55))
        self.stdout.write(self.style.NOTICE(" Hotel Ichchha — Full Data Import"))
        self.stdout.write(self.style.NOTICE("=" * 55))

        # Step 1: initial_data.yaml (settings, currencies, nav menus, SEO banners)
        self.stdout.write(self.style.NOTICE("\n[1/3] Importing initial_data.yaml..."))
        kwargs = {}
        if options.get("update"):
            kwargs["update"] = True
        call_command("import_initial_data", **kwargs)

        # Step 2: seed_data.yaml (rooms, dining, recreation, hero slides, testimonials, etc.)
        self.stdout.write(self.style.NOTICE("\n[2/3] Seeding seed_data.yaml..."))
        call_command("seed_data")

        # Step 3: seed_conference.yaml (conference & event venue halls)
        self.stdout.write(self.style.NOTICE("\n[3/3] Seeding seed_conference.yaml..."))
        call_command("seed_conference")

        self.stdout.write(self.style.NOTICE("\n" + "=" * 55))
        self.stdout.write(self.style.SUCCESS(" All data imported successfully!"))
        self.stdout.write(self.style.NOTICE("=" * 55))
