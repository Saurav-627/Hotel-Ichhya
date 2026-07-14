import os
import yaml
from django.core.management.base import BaseCommand
from settings_manager.models.hotel_settings import HotelSettings
from settings_manager.models.currency import Currency
from settings_manager.models.navigation import NavigationMenu

class Command(BaseCommand):
    help = "Imports initial hotel configuration settings, currencies, and navigation links from a YAML file."

    def add_arguments(self, parser):
        parser.add_argument(
            "--file",
            type=str,
            default="initial_data.yaml",
            help="Path to the YAML data file (default: initial_data.yaml in project root)",
        )

    def handle(self, *args, **options):
        file_path = options["file"]
        
        if not os.path.exists(file_path):
            self.stderr.write(self.style.ERROR(f"File not found: {file_path}"))
            return

        self.stdout.write(self.style.NOTICE(f"Loading data from {file_path}..."))

        with open(file_path, "r", encoding="utf-8") as f:
            try:
                data = yaml.safe_load(f)
            except yaml.YAMLError as exc:
                self.stderr.write(self.style.ERROR(f"Error parsing YAML: {exc}"))
                return

        if not data:
            self.stderr.write(self.style.ERROR("YAML file is empty."))
            return

        # 1. Import Hotel Settings
        if HotelSettings.objects.exists():
            self.stdout.write(self.style.WARNING("Hotel Global Settings already exist. Skipping settings import."))
        else:
            settings_data = data.get("hotel_settings")
            if settings_data:
                HotelSettings.objects.create(**settings_data)
                self.stdout.write(self.style.SUCCESS("Created new Hotel Global Settings."))

        # 2. Import Currencies
        if Currency.objects.exists():
            self.stdout.write(self.style.WARNING("Currencies already exist. Skipping currencies import."))
        else:
            currencies = data.get("currencies", [])
            for c_data in currencies:
                iso_code = c_data.get("iso_code")
                Currency.objects.create(
                    iso_code=iso_code,
                    name=c_data.get("name"),
                    symbol=c_data.get("symbol"),
                    is_published=c_data.get("is_published", True),
                    sequence=c_data.get("sequence"),
                    is_custom=c_data.get("is_custom", False),
                )
                self.stdout.write(self.style.SUCCESS(f"Created currency: {iso_code}"))

        # 3. Import Navigation Menus
        if NavigationMenu.objects.exists():
            self.stdout.write(self.style.WARNING("Navigation menu items already exist. Skipping menu import."))
        else:
            menus = data.get("navigation_menus", [])
            for m_data in menus:
                name = m_data.get("name")
                position = m_data.get("position")
                NavigationMenu.objects.create(
                    name=name,
                    position=position,
                    url=m_data.get("url"),
                    order=m_data.get("order", 0),
                )
                self.stdout.write(self.style.SUCCESS(f"Created menu item: {name} ({position})"))

        self.stdout.write(self.style.SUCCESS("Initial data import completed!"))
