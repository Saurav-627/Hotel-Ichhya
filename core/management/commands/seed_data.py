from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone
from settings_manager.models.hotel_settings import HotelSettings
from settings_manager.models.navigation import NavigationMenu
from homepage.models.hero_slide import HeroSlide
from homepage.models.about_preview import AboutPreview
from rooms.models.room_facility import RoomFacility
from rooms.models.room import Room
from dining.models.venue import DiningVenue
from recreation.models.activity import RecreationActivity
from nearby_places.models.attraction import Attraction
from testimonials.models.testimonial import Testimonial
from seo.models.seo_data import SEOData
from booking.models.coupon import Coupon
import datetime

User = get_user_model()

class Command(BaseCommand):
    help = 'Seeds the database with premium 5-star hotel data for Hotel Ichha'

    def handle(self, *args, **kwargs):
        self.stdout.write("Seeding database...")

        # 1. Create Superuser if not exists
        if not User.objects.filter(username="admin").exists():
            User.objects.create_superuser("admin", "admin@hotelichha.com", "admin123", phone="+977-9855012345", is_hotel_admin=True, is_guest=False)
            self.stdout.write("Created superuser 'admin' with password 'admin123'.")

        # 1b. Seed Currencies
        from settings_manager.models.currency import Currency
        Currency.objects.get_queryset().set_active_test(enabled=False).delete(is_soft=False)
        Currency.objects.create(iso_code="USD", name="US Dollar", symbol="$", sequence=1, is_published=True, is_custom=False)
        Currency.objects.create(iso_code="NPR", name="Nepalese Rupee", symbol="₨", sequence=2, is_published=True, is_custom=False)
        Currency.objects.create(iso_code="EUR", name="Euro", symbol="€", sequence=3, is_published=True, is_custom=False)
        Currency.objects.create(iso_code="GBP", name="British Pound", symbol="£", sequence=4, is_published=True, is_custom=False)
        self.stdout.write("Seeded Currencies.")

        # 2. Hotel Settings (Singleton)
        settings_obj, created = HotelSettings.objects.get_or_create(id=1, defaults={
            'site_name': 'Hotel Ichha',
            'theme': 'luxury',
            'contact_phone': '+977-51-590011',
            'contact_email': 'concierge@hotelichha.com',
            'address': 'Simara, Bara, Nepal',
            'about_text': 'Hotel Ichha is a premier 5-star sanctuary located in the heart of Simara, Bara. Designed to blend modern grandeur with warm Nepalese hospitality, we provide luxury chambers, elite wellness spas, fine dining lounges, and world-class conference facilities.',
            'copyright_text': '&copy; 2026 Hotel Ichha Resort. All Rights Reserved.',
            'facebook_url': 'https://facebook.com',
            'instagram_url': 'https://instagram.com',
            'twitter_url': 'https://twitter.com',
        })
        if not created:
            settings_obj.site_name = 'Hotel Ichha'
            settings_obj.theme = 'luxury'
            settings_obj.save()
        self.stdout.write("Seeded Hotel Settings.")

        # 3. About Preview
        AboutPreview.objects.get_or_create(id=1, defaults={
            'title': 'Discover A Sanctuary Of Grandeur',
            'subtitle': 'Welcome to Hotel Ichha',
            'content': 'Nestled in the lush greenery of Simara, Bara, Hotel Ichha is your gate to exquisite peace and premium relaxation. We boast masterfully curated accommodations, state-of-the-art recreation facilities, and distinct dining venue options that cater to international guests and delegates alike.\n\nFrom our infinity pool deck to the therapeutic Golden Lotus Spa, every corner of our property is designed to inspire comfort and wonder.',
            'video_url': 'https://www.youtube.com/embed/dQw4w9WgXcQ',
            'stat1_label': 'Luxury Chambers',
            'stat1_value': '80+',
            'stat2_label': 'Event Venues',
            'stat2_value': '4',
            'stat3_label': 'Star Rating',
            'stat3_value': '5-Star',
            'stat4_label': 'Satisfied Guests',
            'stat4_value': '25k+',
        })
        self.stdout.write("Seeded About Preview.")

        # 4. Navigation Menus
        NavigationMenu.objects.all().delete()
        
        # Header Menu Link Items
        rooms_nav = NavigationMenu.objects.create(name="Rooms & Suites", url="/rooms/", position="header", order=1)
        dining_nav = NavigationMenu.objects.create(name="Dining", url="/dining/", position="header", order=2)
        rec_nav = NavigationMenu.objects.create(name="Recreation", url="/recreation/", position="header", order=3)
        gallery_nav = NavigationMenu.objects.create(name="Gallery", url="/gallery/", position="header", order=4)
        blog_nav = NavigationMenu.objects.create(name="Journal", url="/blogs/", position="header", order=5)
        contact_nav = NavigationMenu.objects.create(name="Contact", url="/contact/", position="header", order=6)

        # Footer Quick Links
        NavigationMenu.objects.create(name="Book A Chamber", url="/rooms/", position="footer_links", order=1)
        NavigationMenu.objects.create(name="Fine Gastronomy", url="/dining/", position="footer_links", order=2)
        NavigationMenu.objects.create(name="Wellness Spa", url="/recreation/", position="footer_links", order=3)
        NavigationMenu.objects.create(name="Contact Desk", url="/contact/", position="footer_links", order=4)

        # Footer OTA Links
        NavigationMenu.objects.create(name="Booking.com", url="https://booking.com", position="footer_ota", order=1)
        NavigationMenu.objects.create(name="Agoda Partner", url="https://agoda.com", position="footer_ota", order=2)
        NavigationMenu.objects.create(name="Tripadvisor Reviews", url="https://tripadvisor.com", position="footer_ota", order=3)
        
        self.stdout.write("Seeded Navigation Menus.")

        # 5. Hero Slides
        HeroSlide.objects.all().delete()
        HeroSlide.objects.create(
            title="A Haven of Elite Luxury & Calm",
            subtitle="Hotel Ichha Resort",
            cta_text="Book Your Stay",
            cta_url="/rooms/",
            cta2_text="Explore Dining",
            cta2_url="/dining/",
            order=1,
            overlay_opacity=0.60
        )
        HeroSlide.objects.create(
            title="Savor Award-Winning Gastronomy",
            subtitle="The Royal Orchid Restaurant",
            cta_text="Reserve Table",
            cta_url="/dining/",
            order=2,
            overlay_opacity=0.60
        )
        self.stdout.write("Seeded Hero Slides.")

        # 6. Room Facilities
        RoomFacility.objects.all().delete()
        wifi = RoomFacility.objects.create(name="Ultra High-Speed Wifi", icon_class="fa-solid fa-wifi", is_featured=True)
        parking = RoomFacility.objects.create(name="Valet Parking", icon_class="fa-solid fa-square-parking", is_featured=True)
        pool = RoomFacility.objects.create(name="Infinity Pool", icon_class="fa-solid fa-swimming-pool", is_featured=True)
        gym = RoomFacility.objects.create(name="Elite Fitness Gym", icon_class="fa-solid fa-dumbbell", is_featured=True)
        spa = RoomFacility.objects.create(name="Golden Lotus Spa", icon_class="fa-solid fa-spa", is_featured=True)
        service = RoomFacility.objects.create(name="24/7 Room Service", icon_class="fa-solid fa-bell-concierge", is_featured=True)
        self.stdout.write("Seeded Room Facilities.")

        # 7. Rooms & Chambers
        Room.objects.all().delete()
        deluxe = Room.objects.create(
            title="Deluxe Royal Chamber",
            slug="deluxe-royal-chamber",
            category="deluxe",
            description="Our Deluxe Royal Chambers offer absolute serenity and comfort. Adorned with plush kingsize beds, local handcrafted wood furnishings, and panoramic garden views, they are the ideal escape for leisure travelers.",
            highlights="King Size Pillow-Top Bed\nMini Bar & Espresso Maker\nHigh-definition Smart LED TV\nSpacious work desk",
            base_price=120.00,
            currency="USD",
            room_size=420,
            max_adults=2,
            max_children=1,
            bed_type="King Size Bed",
            is_featured=True
        )
        deluxe.facilities.add(wifi, service, parking)

        exec_suite = Room.objects.create(
            title="Executive Diplomatic Suite",
            slug="executive-diplomatic-suite",
            category="executive",
            description="Designed for delegates and corporate high-flyers, our Executive Suites feature a separate grand living lounge, private dining setup, and direct workstation desks. Includes access to our premium lounge club.",
            highlights="Separate grand lounge section\nPrivate dining room space\nPre-stocked luxury mini bar\nComplementary spa access",
            base_price=250.00,
            currency="EUR",
            room_size=680,
            max_adults=3,
            max_children=1,
            bed_type="Grand King Bed",
            is_featured=True
        )
        exec_suite.facilities.add(wifi, service, parking, gym, spa)

        honeymoon = Room.objects.create(
            title="Honeymoon Sanctuary Suite",
            slug="honeymoon-sanctuary-suite",
            category="honeymoon_suite",
            description="Celebrate love in our exquisite Honeymoon Sanctuary. Featuring candle-lit ambiance accents, an in-room private jacuzzi pool, custom velvet drapery, and complimentary champagne service upon arrival.",
            highlights="In-suite private jacuzzi bath\nComplimentary champagne on ice\nBreakfast in bed service\nPrivate balcony overlook",
            base_price=42000.00,
            currency="NPR",
            room_size=550,
            max_adults=2,
            max_children=0,
            bed_type="King Velvet Bed",
            is_featured=True
        )
        honeymoon.facilities.add(wifi, service, pool, spa, parking)
        self.stdout.write("Seeded Rooms.")

        # 8. Dining Venues
        DiningVenue.objects.all().delete()
        DiningVenue.objects.create(
            name="The Royal Orchid Restaurant",
            slug="the-royal-orchid-restaurant",
            category="restaurant",
            description="Our flagship dining space serving international and traditional Asian cuisines. Enjoy dining in a masterfully architected ambient hall overlooking the garden water cascades.",
            timings="06:00 AM - 11:00 PM",
            capacity=120,
            featured_dishes="Slow-roasted Himalayan Lamb Shanks & local spices",
            is_featured=True
        )
        DiningVenue.objects.create(
            name="Cinnamon Lounge & Bar",
            slug="cinnamon-lounge-bar",
            category="bar",
            description="Unwind after hours with premium spirits, single malts, and handpicked wines. Features live jazz performances on weekends.",
            timings="04:00 PM - 12:00 AM",
            capacity=60,
            featured_dishes="Smoked Ginger-infused Whiskey Sour",
            is_featured=True
        )
        self.stdout.write("Seeded Dining Venues.")

        # 9. Recreation
        RecreationActivity.objects.all().delete()
        RecreationActivity.objects.create(
            name="Golden Lotus Spa",
            slug="golden-lotus-spa",
            category="spa",
            description="Experience ancient therapeutic massages, herbal wrap packages, and deep-tissue scrubs administered by certified wellness experts.",
            timings="08:00 AM - 08:00 PM",
            price_info="Packages starting at $45.00",
            is_active=True
        )
        RecreationActivity.objects.create(
            name="Infinity Oasis Pool",
            slug="infinity-oasis-pool",
            category="pool",
            description="Our solar-heated pool is perfect for a refreshing morning swim. Features comfortable sunbeds and a poolside cocktail service kiosk.",
            timings="07:00 AM - 09:00 PM",
            price_info="Complimentary for guests",
            is_active=True
        )
        self.stdout.write("Seeded Recreation.")

        # 10. Attractions
        Attraction.objects.all().delete()
        Attraction.objects.create(
            name="Gadhimai Temple Complex",
            category="temple",
            distance="12 km",
            travel_time="20 mins drive",
            description="The historic Gadhimai Temple is a renowned spiritual destination attracting millions of pilgrims globally.",
            order=1,
            is_active=True
        )
        Attraction.objects.create(
            name="Parsa National Park",
            category="nature",
            distance="24 km",
            travel_time="40 mins drive",
            description="Explore wild elephant habitats, tigers, and exotic birdwatching safaris in this vast tropical jungle national park.",
            order=2,
            is_active=True
        )
        self.stdout.write("Seeded Attractions.")

        # 11. Testimonials
        Testimonial.objects.all().delete()
        Testimonial.objects.create(
            guest_name="Sarah Jenkins",
            country="United States",
            source="google",
            rating=5,
            review_text="An absolutely stunning property! The rooms are so luxurious, the pool is beautiful, and the staff is extremely helpful.",
            is_featured=True
        )
        Testimonial.objects.create(
            guest_name="Amit Sharma",
            country="India",
            source="tripadvisor",
            rating=5,
            review_text="Hotel Ichha is easily the best hotel in the Bara area. Immaculate food, grand conference halls, and clean suites.",
            is_featured=True
        )
        self.stdout.write("Seeded Testimonials.")

        # 12. SEO Data (Home Route)
        SEOData.objects.all().delete()
        SEOData.objects.create(
            path="/",
            meta_title="Hotel Ichha | 5-Star Luxury Resort in Bara, Nepal",
            meta_description="Book rooms at Hotel Ichha in Simara, Bara, Nepal. Explore our premium chambers, fine dining restaurants, spas, and conference packages.",
            twitter_card="summary_large_image",
            structured_data='{"@context": "https://schema.org", "@type": "Hotel", "name": "Hotel Ichha", "image": "https://images.unsplash.com/photo-1542314831-068cd1dbfeeb?q=80&w=1200", "address": {"@type": "PostalAddress", "streetAddress": "Simara", "addressLocality": "Bara", "addressCountry": "NP"}, "starRating": {"@type": "Rating", "ratingValue": "5"}}'
        )
        self.stdout.write("Seeded SEO Data.")

        # 13. Coupon
        Coupon.objects.all().delete()
        Coupon.objects.create(
            code="WELCOME10",
            discount_type="percentage",
            discount_value=10.00,
            min_spend=100.00,
            valid_from=timezone.now() - timezone.timedelta(days=1),
            valid_to=timezone.now() + timezone.timedelta(days=365),
            is_active=True
        )
        self.stdout.write("Seeded Coupon 'WELCOME10'.")

        self.stdout.write(self.style.SUCCESS("Database seeding completed successfully!"))
