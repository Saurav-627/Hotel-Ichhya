import os
from datetime import timedelta

import yaml
from django.apps import apps
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.utils import timezone

User = get_user_model()

# Global Model Mapping Registry:
# key -> (app_label, model_name, lookup_fields, is_singleton)
GLOBAL_MODEL_REGISTRY = {
    # Settings & Config
    "hotel_settings": ("settings_manager", "HotelSettings", None, True),
    "currencies": ("settings_manager", "Currency", ["iso_code"], False),
    "navigation_menus": ("settings_manager", "NavigationMenu", ["name", "position"], False),
    "seo_banners": ("seo", "SEOData", ["path"], False),
    "seo_data": ("seo", "SEOData", ["path"], False),
    "payment_processors": ("payments", "PaymentProcessor", ["code"], False),

    # Homepage & CMS
    "about_preview": ("homepage", "AboutPreview", None, True),
    "hero_slides": ("homepage", "HeroSlide", ["title"], False),

    # Rooms & Facilities
    "room_categories": ("rooms", "RoomCategory", ["slug"], False),
    "room_facilities": ("rooms", "RoomFacility", ["name"], False),

    # Dining, Recreation & Events
    "dining_venues": ("dining", "DiningVenue", ["slug"], False),
    "recreation_activities": ("recreation", "RecreationActivity", ["slug"], False),
    "event_venues": ("conference", "EventVenue", ["name"], False),
    "event_types": ("conference", "EventType", ["slug"], False),

    # Other Apps
    "attractions": ("nearby_places", "Attraction", ["name"], False),
    "testimonials": ("testimonials", "Testimonial", ["guest_name", "source"], False),
    "branches": ("contact", "Branch", ["name"], False),
    "inquiry_categories": ("contact", "InquiryCategory", ["slug"], False),
    "coupons": ("booking", "Coupon", ["code"], False),
    "addons": ("booking", "Addon", ["name"], False),

    # About Page & Leadership
    "about_page": ("about", "AboutPage", None, True),
    "team_members": ("about", "TeamMember", ["name"], False),
    "facility_highlights": ("about", "AboutFacility", ["title"], False),
    "about_facilities": ("about", "AboutFacility", ["title"], False),
}


def filter_model_fields(model, data_dict):
    """Dynamically filters dictionary keys to match only real fields present on the target Django model."""
    valid_field_names = {f.name for f in model._meta.get_fields() if not f.is_relation or f.concrete}
    return {k: v for k, v in data_dict.items() if k in valid_field_names}


def prepare_item_data(key, item, valid_data):
    """Applies model-specific dynamic preprocessing (e.g. date calculation for Coupons)."""
    if key == "coupons":
        valid_days = item.get("valid_days_from_now", 365)
        if "valid_from" not in valid_data:
            valid_data["valid_from"] = timezone.now() - timedelta(days=1)
        if "valid_to" not in valid_data:
            valid_data["valid_to"] = timezone.now() + timedelta(days=valid_days)
    return valid_data


def post_process_item(key, obj, item):
    """Applies post-creation/update relationship logic (e.g. PaymentProcessor Currency links, EventVenue Base Prices, Addon Prices)."""
    if key == "payment_processors":
        currencies_list = item.get("currencies") or item.get("payment_currencies") or []
        if currencies_list:
            from payments.models.payment_processor import PaymentProcessorCurrency
            from settings_manager.models.currency import Currency
            for ccode in currencies_list:
                # pyrefly: ignore [missing-attribute]
                curr = Currency.objects.get_queryset().set_active_test(enabled=False).filter(iso_code=ccode).first()
                if curr:
                    PaymentProcessorCurrency.objects.get_or_create(
                        payment_processor=obj,
                        currency=curr
                    )
    elif key == "event_venues":
        prices_data = item.get("base_prices") or item.get("prices") or []
        if prices_data:
            from conference.models.venue_base_price import VenueBasePrice
            from settings_manager.models.currency import Currency
            for p_data in prices_data:
                ccode = p_data.get("currency")
                # pyrefly: ignore [missing-attribute]
                c_obj = Currency.objects.get_queryset().set_active_test(enabled=False).filter(iso_code=ccode).first()
                if c_obj:
                    VenueBasePrice.objects.update_or_create(
                        venue=obj,
                        currency=c_obj,
                        defaults={'base_price': p_data.get("base_price")}
                    )
        layouts_data = item.get("layouts") or []
        if layouts_data:
            from conference.models.venue_layout import VenueLayout
            for l_data in layouts_data:
                VenueLayout.objects.update_or_create(
                    venue=obj,
                    name=l_data.get("name"),
                    defaults={
                        'capacity': l_data.get("capacity", 0),
                        'is_active': l_data.get("is_active", True),
                        'display_order': l_data.get("display_order", 0),
                    }
                )
    elif key == "coupons":
        min_spends_data = item.get("min_spends") or []
        if min_spends_data:
            from booking.models.coupon import CouponMinSpend
            from settings_manager.models.currency import Currency
            for ms in min_spends_data:
                ccode = ms.get("currency")
                min_spend_val = ms.get("min_spend")
                if ccode and min_spend_val is not None:
                    # pyrefly: ignore [missing-attribute]
                    curr = Currency.objects.get_queryset().set_active_test(enabled=False).filter(iso_code=ccode).first()
                    if curr:
                        CouponMinSpend.objects.update_or_create(
                            coupon=obj,
                            currency=curr,
                            defaults={'min_spend': min_spend_val}
                        )
    elif key == "addons":
        prices_data = item.get("prices") or []
        if prices_data:
            from booking.models.addon import AddonPrice
            from settings_manager.models.currency import Currency
            for pr in prices_data:
                ccode = pr.get("currency")
                price_val = pr.get("price")
                if ccode and price_val is not None:
                    # pyrefly: ignore [missing-attribute]
                    curr = Currency.objects.get_queryset().set_active_test(enabled=False).filter(iso_code=ccode).first()
                    if curr:
                        AddonPrice.objects.update_or_create(
                            addon=obj,
                            currency=curr,
                            defaults={"price": price_val}
                        )
        venues_list = item.get("event_venues") or item.get("venues") or []
        if venues_list:
            from conference.models.venue import EventVenue
            from django.db.models import Q
            venues_qs = EventVenue.objects.filter(Q(name__in=venues_list) | Q(slug__in=venues_list))
            if venues_qs.exists():
                obj.event_venues.set(venues_qs)
    elif key == "event_types":
        venues_list = item.get("venues") or []
        if venues_list:
            from conference.models.venue import EventVenue
            from django.db.models import Q
            venues_qs = EventVenue.objects.filter(Q(name__in=venues_list) | Q(slug__in=venues_list))
            if venues_qs.exists():
                obj.venues.set(venues_qs)


class Command(BaseCommand):
    help = (
        "Single Unified Data Importer for Hotel Ichchha. "
        "Imports data from YAML files (core/records/). "
        "If a model already contains data: SKIPS the model to preserve admin edits. "
        "Use --update to update matching records, or --force to force re-importing all items."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--file",
            type=str,
            default=None,
            help="Path to specific YAML data file",
        )
        parser.add_argument(
            "--folder",
            type=str,
            default="core/records",
            help="Path to directory containing modular YAML data files (default: core/records)",
        )
        parser.add_argument(
            "--update",
            action="store_true",
            default=False,
            help="If set, update existing records instead of skipping them.",
        )
        parser.add_argument(
            "--force",
            action="store_true",
            default=False,
            help="If set, force import records from YAML even if data already exists in database.",
        )

    def handle(self, *args, **options):
        file_path = options.get("file")
        folder_path = options.get("folder")
        do_update = options.get("update", False)
        do_force = options.get("force", False)

        files_to_process = []
        if file_path:
            files_to_process.append(file_path)
        else:
            if folder_path and os.path.exists(folder_path):
                folder_files = [
                    os.path.join(folder_path, f)
                    for f in sorted(os.listdir(folder_path))
                    if f.endswith((".yaml", ".yml"))
                ]
                files_to_process.extend(folder_files)

        # -- 1. Ensure Superuser Admin
        if not User.objects.filter(username="admin").exists():
            # pyrefly: ignore [missing-attribute]
            User.objects.create_superuser(
                "admin", "admin@hotelichchha.com", "admin123",
                phone="+977-9855012345", is_hotel_admin=True, is_guest=False
            )
            self.stdout.write(self.style.SUCCESS("Created superuser 'admin' (password: admin123)."))
        else:
            self.stdout.write(self.style.WARNING("Superuser 'admin' already exists. Skipping."))

        for current_file in files_to_process:
            if not os.path.exists(current_file):
                continue

            self.stdout.write(self.style.NOTICE(f"\nProcessing data from {current_file}..."))

            with open(current_file, "r", encoding="utf-8") as f:
                try:
                    data = yaml.safe_load(f)
                except yaml.YAMLError as exc:
                    self.stderr.write(self.style.ERROR(f"Error parsing YAML ({current_file}): {exc}"))
                    continue

            if not data:
                self.stderr.write(self.style.ERROR(f"YAML file is empty: {current_file}"))
                continue

            # -- 2. Process All Registered Models Dynamically
            for key, config in GLOBAL_MODEL_REGISTRY.items():
                if key not in data:
                    continue

                app_label, model_name, lookup_fields, is_singleton = config
                try:
                    model = apps.get_model(app_label, model_name)
                except LookupError:
                    self.stderr.write(self.style.ERROR(f"Model {app_label}.{model_name} not found."))
                    continue

                raw_data = data[key]

                # SINGLETON MODELS
                if is_singleton:
                    if not isinstance(raw_data, dict):
                        continue
                    valid_data = filter_model_fields(model, raw_data)
                    valid_data = prepare_item_data(key, raw_data, valid_data)

                    existing = model.objects.first()
                    if existing:
                        if do_update or do_force:
                            for k, v in valid_data.items():
                                setattr(existing, k, v)
                            existing.save()
                            post_process_item(key, existing, raw_data)
                            self.stdout.write(self.style.SUCCESS(f"  - Updated {model_name} (Singleton)"))
                        else:
                            self.stdout.write(self.style.WARNING(f"  - {model_name} already exists. Skipping."))
                    else:
                        new_obj = model.objects.create(**valid_data)
                        post_process_item(key, new_obj, raw_data)
                        self.stdout.write(self.style.SUCCESS(f"  - Created {model_name} (Singleton)"))

                # COLLECTION MODELS
                else:
                    if not isinstance(raw_data, list):
                        continue

                    # If table already contains records and neither --update nor --force is specified, skip model
                    existing_count = model.objects.count()
                    if existing_count > 0 and not do_update and not do_force:
                        self.stdout.write(
                            self.style.WARNING(
                                f"  - {model_name} already contains {existing_count} record(s). Skipping to preserve database customizations."
                            )
                        )
                        continue

                    count_created = 0
                    count_updated = 0
                    count_skipped = 0

                    for item in raw_data:
                        if not isinstance(item, dict):
                            continue

                        valid_data = filter_model_fields(model, item)
                        valid_data = prepare_item_data(key, item, valid_data)

                        # Special active manager lookup for Currency / PaymentProcessor
                        if model_name == "Currency" and "iso_code" in item:
                            existing = model.objects.get_queryset().set_active_test(enabled=False).filter(iso_code=item["iso_code"]).first()
                        elif model_name == "PaymentProcessor" and "code" in item:
                            existing = model._base_manager.filter(code=item["code"]).first()
                        else:
                            # pyrefly: ignore [not-iterable]
                            lookup_kwargs = {field: item.get(field) for field in lookup_fields if item.get(field) is not None}
                            if not lookup_kwargs:
                                continue
                            existing = model.objects.filter(**lookup_kwargs).first()

                        if existing:
                            if do_update or do_force:
                                for k, v in valid_data.items():
                                    setattr(existing, k, v)
                                if hasattr(existing, 'is_active'):
                                    existing.is_active = True
                                if hasattr(existing, 'deleted_at'):
                                    existing.deleted_at = None
                                existing.save()
                                post_process_item(key, existing, item)
                                count_updated += 1
                            else:
                                count_skipped += 1
                        else:
                            new_obj = model.objects.create(**valid_data)
                            post_process_item(key, new_obj, item)
                            count_created += 1

                    self.stdout.write(
                        self.style.SUCCESS(
                            f"  - Processed {model_name}: {count_created} created, {count_updated} updated, {count_skipped} skipped."
                        )
                    )

            # -- 3. Complex Models: Rooms with nested FKs, M2Ms, Images, Policies, Seasonal Prices & Prices
            if "rooms" in data:
                from rooms.models.room import Room
                from rooms.models.room_category import RoomCategory
                from rooms.models.room_facility import RoomFacility
                from rooms.models.room_base_price import RoomBasePrice
                from rooms.models.room_image import RoomImage
                from rooms.models.room_policy import RoomPolicy
                from rooms.models.room_seasonal_price import RoomSeasonalPrice
                from settings_manager.models.currency import Currency

                existing_room_count = Room.objects.count()
                if existing_room_count > 0 and not do_update and not do_force:
                    self.stdout.write(
                        self.style.WARNING(
                            f"  - Room already contains {existing_room_count} record(s). Skipping to preserve database customizations."
                        )
                    )
                else:
                    count_created = 0
                    count_updated = 0
                    count_skipped = 0

                    for room_data in data.get("rooms", []):
                        slug = room_data.get("slug")
                        if not slug:
                            continue
                        facility_names = room_data.pop("facilities", [])
                        images = room_data.pop("images", [])
                        policies = room_data.pop("policies", [])
                        seasonal_prices = room_data.pop("seasonal_prices", [])
                        prices_data = room_data.pop("prices", [])
                        included_addons = room_data.pop("included_addons", [])

                        category_slug = room_data.get("category")
                        if category_slug:
                            cat_obj = RoomCategory.objects.filter(slug=category_slug).first()
                            room_data["category"] = cat_obj

                        valid_room_fields = filter_model_fields(Room, room_data)

                        existing = Room.objects.filter(slug=slug).first()
                        if existing:
                            if do_update or do_force:
                                for k, v in valid_room_fields.items():
                                    setattr(existing, k, v)
                                existing.save()
                                room_obj = existing
                                count_updated += 1
                            else:
                                count_skipped += 1
                                continue
                        else:
                            valid_room_fields["slug"] = slug
                            room_obj = Room.objects.create(**valid_room_fields)
                            count_created += 1

                        for p_data in prices_data:
                            ccode = p_data.get("currency")
                            # pyrefly: ignore [missing-attribute]
                            c_obj = Currency.objects.get_queryset().set_active_test(enabled=False).filter(iso_code=ccode).first() or Currency.objects.filter(iso_code=ccode).first()
                            if c_obj:
                                RoomBasePrice.objects.update_or_create(
                                    room=room_obj,
                                    currency=c_obj,
                                    defaults={
                                        'base_price': p_data.get("base_price"),
                                        'discount_price': p_data.get("discount_price")
                                    }
                                )

                        for fname in facility_names:
                            fac = RoomFacility.objects.filter(name=fname).first()
                            if fac:
                                room_obj.facilities.add(fac)

                        if included_addons:
                            from booking.models.addon import Addon
                            addons_qs = Addon.objects.filter(name__in=included_addons)
                            room_obj.included_addons.set(addons_qs)

                        for img in images:
                            img_path = img.get("image")
                            if img_path:
                                RoomImage.objects.get_or_create(
                                    room=room_obj,
                                    image=img_path,
                                    defaults={"is_primary": img.get("is_primary", False), "alt_text": img.get("alt_text", "")}
                                )

                        for pol in policies:
                            RoomPolicy.objects.get_or_create(
                                room=room_obj,
                                title=pol.get("title"),
                                defaults={"description": pol.get("description")}
                            )

                        for prc in seasonal_prices:
                            RoomSeasonalPrice.objects.get_or_create(
                                room=room_obj,
                                name=prc.get("name"),
                                start_date=prc.get("start_date"),
                                end_date=prc.get("end_date"),
                                defaults={
                                    "price_override": prc.get("price_override"),
                                    "is_active": prc.get("is_active", True)
                                }
                            )

                    self.stdout.write(
                        self.style.SUCCESS(
                            f"  - Processed Room: {count_created} created, {count_updated} updated, {count_skipped} skipped."
                        )
                    )

        self.stdout.write(self.style.SUCCESS("\nAll data import tasks completed successfully!"))

