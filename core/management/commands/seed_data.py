import os
import yaml
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta

User = get_user_model()


class Command(BaseCommand):
    help = (
        "Seeds the database with premium 5-star hotel data from seed_data.yaml. "
        "Uses get_or_create — existing records are NEVER deleted or overwritten."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--file",
            type=str,
            default="seed_data.yaml",
            help="Path to the seed YAML file (default: seed_data.yaml in project root)",
        )

    def handle(self, *args, **options):
        file_path = options["file"]

        if not os.path.exists(file_path):
            self.stderr.write(self.style.ERROR(f"Seed file not found: {file_path}"))
            return

        self.stdout.write(self.style.NOTICE(f"Loading seed data from {file_path}..."))

        with open(file_path, "r", encoding="utf-8") as f:
            try:
                data = yaml.safe_load(f)
            except yaml.YAMLError as exc:
                self.stderr.write(self.style.ERROR(f"Error parsing YAML: {exc}"))
                return

        if not data:
            self.stderr.write(self.style.ERROR("YAML file is empty."))
            return

        # -- 1. Superuser
        if not User.objects.filter(username="admin").exists():
            User.objects.create_superuser(
                "admin", "admin@hotelichchha.com", "admin123",
                phone="+977-9855012345", is_hotel_admin=True, is_guest=False
            )
            self.stdout.write(self.style.SUCCESS("Created superuser 'admin' (password: admin123)."))
        else:
            self.stdout.write(self.style.WARNING("Superuser 'admin' already exists. Skipping."))

        # -- 2. Currencies
        from settings_manager.models.currency import Currency
        for c in data.get("currencies", []):
            iso = c.get("iso_code")
            if not iso:
                continue
            qs = Currency.objects.get_queryset().set_active_test(enabled=False)
            if qs.filter(iso_code=iso).exists():
                self.stdout.write(self.style.WARNING(f"Currency '{iso}' already exists. Skipping."))
            else:
                Currency.objects.create(
                    iso_code=iso,
                    name=c.get("name"),
                    symbol=c.get("symbol"),
                    sequence=c.get("sequence"),
                    is_published=c.get("is_published", True),
                    is_custom=c.get("is_custom", False),
                )
                self.stdout.write(self.style.SUCCESS(f"Created currency: {iso}"))

        # -- 3. Hotel Settings (singleton)
        from settings_manager.models.hotel_settings import HotelSettings
        s = data.get("hotel_settings")
        if s:
            _, created = HotelSettings.objects.get_or_create(id=1, defaults=s)
            if created:
                self.stdout.write(self.style.SUCCESS("Created Hotel Settings."))
            else:
                self.stdout.write(self.style.WARNING("Hotel Settings already exist. Skipping."))

        # -- 4. About Preview (singleton)
        from homepage.models.about_preview import AboutPreview
        ap = data.get("about_preview")
        if ap:
            _, created = AboutPreview.objects.get_or_create(id=1, defaults=ap)
            if created:
                self.stdout.write(self.style.SUCCESS("Created About Preview."))
            else:
                self.stdout.write(self.style.WARNING("About Preview already exists. Skipping."))

        # -- 5. Navigation Menus
        from settings_manager.models.navigation import NavigationMenu
        for m in data.get("navigation_menus", []):
            name = m.get("name")
            position = m.get("position")
            if not name or not position:
                continue
            _, created = NavigationMenu.objects.get_or_create(
                name=name, position=position,
                defaults={
                    "url": m.get("url", "/"),
                    "order": m.get("order", 0),
                    "is_published": m.get("is_published", True),
                }
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f"Created nav item: {name} ({position})"))
            else:
                self.stdout.write(self.style.WARNING(f"Nav item '{name}' ({position}) already exists. Skipping."))

        # -- 6. Hero Slides
        from homepage.models.hero_slide import HeroSlide
        for slide in data.get("hero_slides", []):
            title = slide.get("title")
            if not title:
                continue
            _, created = HeroSlide.objects.get_or_create(
                title=title,
                defaults={k: v for k, v in slide.items() if k != "title"}
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f"Created hero slide: {title}"))
            else:
                self.stdout.write(self.style.WARNING(f"Hero slide '{title}' already exists. Skipping."))

        # -- 7. Room Facilities
        from rooms.models.room_facility import RoomFacility
        for fac in data.get("room_facilities", []):
            name = fac.get("name")
            if not name:
                continue
            _, created = RoomFacility.objects.get_or_create(
                name=name,
                defaults={k: v for k, v in fac.items() if k != "name"}
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f"Created facility: {name}"))
            else:
                self.stdout.write(self.style.WARNING(f"Facility '{name}' already exists. Skipping."))

        # -- 7.5. Room Categories
        from rooms.models.room_category import RoomCategory
        for cat in data.get("room_categories", []):
            slug = cat.get("slug")
            if not slug:
                continue
            _, created = RoomCategory.objects.get_or_create(
                slug=slug,
                defaults={
                    "name": cat.get("name"),
                    "order": cat.get("order", 0),
                    "is_published": cat.get("is_published", True),
                }
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f"Created Room Category: {cat.get('name')}"))
            else:
                self.stdout.write(self.style.WARNING(f"Room Category '{slug}' already exists. Skipping."))

        # -- 8. Rooms
        from rooms.models.room import Room
        from rooms.models.room_category import RoomCategory
        for room_data in data.get("rooms", []):
            slug = room_data.get("slug")
            if not slug:
                continue
            facility_names = room_data.pop("facilities", [])
            images = room_data.pop("images", [])
            policies = room_data.pop("policies", [])
            seasonal_prices = room_data.pop("seasonal_prices", [])
            prices_data = room_data.pop("prices", [])
            
            category_slug = room_data.get("category")
            if category_slug:
                cat_obj = RoomCategory.objects.filter(slug=category_slug).first()
                room_data["category"] = cat_obj

            room_obj, created = Room.objects.get_or_create(
                slug=slug,
                defaults={k: v for k, v in room_data.items()}
            )
            
            from rooms.models.room_base_price import RoomBasePrice
            from settings_manager.models.currency import Currency
            for p_data in prices_data:
                ccode = p_data.get("currency")
                c_obj = Currency.objects.filter(iso_code=ccode).first()
                if c_obj:
                    RoomBasePrice.objects.update_or_create(
                        room=room_obj,
                        currency=c_obj,
                        defaults={
                            'base_price': p_data.get("base_price"),
                            'discount_price': p_data.get("discount_price")
                        }
                    )
            if created:
                for fname in facility_names:
                    fac = RoomFacility.objects.filter(name=fname).first()
                    if fac:
                        room_obj.facilities.add(fac)
                
                # Seed Room Images
                from rooms.models.room_image import RoomImage
                for img in images:
                    RoomImage.objects.create(
                        room=room_obj,
                        image=img.get("image"),
                        is_primary=img.get("is_primary", False),
                        alt_text=img.get("alt_text", "")
                    )
                
                # Seed Room Policies
                from rooms.models.room_policy import RoomPolicy
                for pol in policies:
                    RoomPolicy.objects.create(
                        room=room_obj,
                        title=pol.get("title"),
                        description=pol.get("description")
                    )
                
                # Seed Room Seasonal Prices
                from rooms.models.room_seasonal_price import RoomSeasonalPrice
                for prc in seasonal_prices:
                    RoomSeasonalPrice.objects.create(
                        room=room_obj,
                        name=prc.get("name"),
                        start_date=prc.get("start_date"),
                        end_date=prc.get("end_date"),
                        price_override=prc.get("price_override"),
                        is_active=prc.get("is_active", True)
                    )

                self.stdout.write(self.style.SUCCESS(f"Created room: {room_obj.title} (with images, policies, and seasonal prices)"))
            else:
                self.stdout.write(self.style.WARNING(f"Room '{slug}' already exists. Skipping."))

        # -- 9. Dining Venues
        from dining.models.venue import DiningVenue
        for venue in data.get("dining_venues", []):
            slug = venue.get("slug")
            if not slug:
                continue
            venue_obj, created = DiningVenue.objects.get_or_create(
                slug=slug,
                defaults={k: v for k, v in venue.items() if k != "slug"}
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f"Created dining venue: {venue_obj.name}"))
            else:
                self.stdout.write(self.style.WARNING(f"Dining venue '{slug}' already exists. Skipping."))

        # -- 10. Recreation Activities
        from recreation.models.activity import RecreationActivity
        for act in data.get("recreation_activities", []):
            slug = act.get("slug")
            if not slug:
                continue
            act_obj, created = RecreationActivity.objects.get_or_create(
                slug=slug,
                defaults={k: v for k, v in act.items() if k != "slug"}
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f"Created activity: {act_obj.name}"))
            else:
                self.stdout.write(self.style.WARNING(f"Activity '{slug}' already exists. Skipping."))

        # -- 11. Nearby Attractions
        from nearby_places.models.attraction import Attraction
        for attr in data.get("attractions", []):
            name = attr.get("name")
            if not name:
                continue
            _, created = Attraction.objects.get_or_create(
                name=name,
                defaults={k: v for k, v in attr.items() if k != "name"}
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f"Created attraction: {name}"))
            else:
                self.stdout.write(self.style.WARNING(f"Attraction '{name}' already exists. Skipping."))

        # -- 12. Testimonials
        from testimonials.models.testimonial import Testimonial
        for t in data.get("testimonials", []):
            guest_name = t.get("guest_name")
            source = t.get("source")
            if not guest_name:
                continue
            _, created = Testimonial.objects.get_or_create(
                guest_name=guest_name, source=source,
                defaults={k: v for k, v in t.items() if k not in ("guest_name", "source")}
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f"Created testimonial: {guest_name}"))
            else:
                self.stdout.write(self.style.WARNING(f"Testimonial '{guest_name}' already exists. Skipping."))

        # -- 13. SEO Data (page meta + banner defaults)
        from seo.models.seo_data import SEOData
        for seo in data.get("seo_data", []):
            path = seo.get("path")
            if not path:
                continue
            _, created = SEOData.objects.get_or_create(
                path=path,
                defaults={k: v for k, v in seo.items() if k != "path"}
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f"Created SEO data: {path}"))
            else:
                self.stdout.write(self.style.WARNING(f"SEO data for '{path}' already exists. Skipping."))

        # -- 14. Coupons
        from booking.models.coupon import Coupon
        for coupon in data.get("coupons", []):
            code = coupon.get("code")
            if not code:
                continue
            if Coupon.objects.filter(code=code).exists():
                self.stdout.write(self.style.WARNING(f"Coupon '{code}' already exists. Skipping."))
                continue
            days = coupon.pop("valid_days_from_now", 365)
            Coupon.objects.create(
                code=code,
                discount_type=coupon.get("discount_type", "percentage"),
                discount_value=coupon.get("discount_value", 10),
                min_spend=coupon.get("min_spend", 0),
                valid_from=timezone.now() - timedelta(days=1),
                valid_to=timezone.now() + timedelta(days=days),
                is_active=coupon.get("is_active", True),
            )
            self.stdout.write(self.style.SUCCESS(f"Created coupon: {code}"))

        # -- 15. Branches
        from contact.models.branch import Branch
        for b in data.get("branches", []):
            name = b.get("name")
            if not name:
                continue
            _, created = Branch.objects.get_or_create(
                name=name,
                defaults={k: v for k, v in b.items() if k != "name"}
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f"Created branch: {name}"))
            else:
                self.stdout.write(self.style.WARNING(f"Branch '{name}' already exists. Skipping."))

        # -- 16. Payment Processors
        from payments.models.payment_processor import PaymentProcessor, PaymentProcessorCurrency
        from settings_manager.models.currency import Currency
        
        processors_to_seed = data.get("payment_processors", [])
        
        for p_data in processors_to_seed:
            code = p_data['code']
            existing = PaymentProcessor._base_manager.filter(code=code).first()
            if existing:
                if not existing.is_active:
                    existing.is_active = True
                    existing.deleted_at = None
                    existing.save()
                    self.stdout.write(self.style.SUCCESS(f"Restored soft-deleted payment processor: {p_data['name']}"))
                else:
                    self.stdout.write(self.style.WARNING(f"Payment processor '{p_data['name']}' already exists. Skipping."))
                processor = existing
            else:
                processor = PaymentProcessor.objects.create(
                    code=code,
                    name=p_data['name'],
                    apply_tax=p_data['apply_tax'],
                    is_published=p_data['is_published']
                )
                self.stdout.write(self.style.SUCCESS(f"Created payment processor: {p_data['name']}"))
                
            # Associate currencies
            for cur_code in p_data['currencies']:
                currency_obj = Currency.objects.get_queryset().set_active_test(enabled=False).filter(iso_code=cur_code).first()
                if currency_obj:
                    PaymentProcessorCurrency.objects.get_or_create(
                        payment_processor=processor,
                        currency=currency_obj
                    )

        self.stdout.write(self.style.SUCCESS("\nDatabase seeding completed successfully!"))

