# 🏨 Hotel Ichchha — CMS, Admin & Architecture Comprehensive Report

> **Purpose:** This document is an exhaustive, technical and functional mapping of the entire **Hotel Ichchha Platform**. It details every administrative capability, CMS-controlled field, guest-submitted workflow, database model, payment gateway integration, email service, and hardcoded/architectural logic across all **17 modular Django apps**. Intended for software developers, hotel management, system administrators, and content editors.

---

## 📑 Table of Contents

1. [Executive Summary & Platform Architecture](#1-executive-summary--platform-architecture)
2. [Admin-Controlled Content & CMS Guide](#2-admin-controlled-content--cms-guide)
   - [2.1 Global Hotel Settings & White-Label Branding](#21-global-hotel-settings--white-label-branding)
   - [2.2 Navigation Menus & Hierarchy](#22-navigation-menus--hierarchy)
   - [2.3 Multi-Currency System](#23-multi-currency-system)
   - [2.4 Payment Processors Configuration](#24-payment-processors-configuration)
   - [2.5 Admin Real-Time Notifications](#25-admin-real-time-notifications)
   - [2.6 Homepage — Hero Carousel](#26-homepage--hero-carousel)
   - [2.7 Homepage — About Preview](#27-homepage--about-preview)
   - [2.8 About Page CMS & Executive Narrative](#28-about-page-cms--executive-narrative)
   - [2.9 Leadership Team & Board of Directors](#29-leadership-team--board-of-directors)
   - [2.10 5-Star Facility Highlights](#210-5-star-facility-highlights)
   - [2.11 Rooms, Accommodation & Availability Calendar](#211-rooms-accommodation--availability-calendar)
   - [2.12 Booking Add-on Services](#212-booking-add-on-services)
   - [2.13 Booking Discount Coupons & Currency Thresholds](#213-booking-discount-coupons--currency-thresholds)
   - [2.14 Dining Venues, PDF Menus & Multi-Image Galleries](#214-dining-venues-pdf-menus--multi-image-galleries)
   - [2.15 Recreation, Spa & Wellness Activities](#215-recreation-spa--wellness-activities)
   - [2.16 Conference, Banquet & Event Venues](#216-conference-banquet--event-venues)
   - [2.17 Resort Photo & Video Gallery](#217-resort-photo--video-gallery)
   - [2.18 Contact Branches & Maps](#218-contact-branches--maps)
   - [2.19 Blog Posts & Editorial Articles](#219-blog-posts--editorial-articles)
   - [2.20 Nearby Places & Tourist Attractions](#220-nearby-places--tourist-attractions)
   - [2.21 Guest Testimonials & Reviews](#221-guest-testimonials--reviews)
   - [2.22 SEO Engine & Dynamic Page Hero Banners](#222-seo-engine--dynamic-page-hero-banners)
   - [2.23 User Accounts & Role Permissions](#223-user-accounts--role-permissions)
3. [Guest-Submitted Data & Staff Workflows](#3-guest-submitted-data--staff-workflows)
   - [3.1 Room Reservations & Invoicing](#31-room-reservations--invoicing)
   - [3.2 Payment Transactions](#32-payment-transactions)
   - [3.3 Dining Table Reservations](#33-dining-table-reservations)
   - [3.4 Conference & Banquet Inquiries](#34-conference--banquet-inquiries)
   - [3.5 Contact Inquiries & SMTP Email Reply Modal](#35-contact-inquiries--smtp-email-reply-modal)
   - [3.6 Newsletter Subscriptions, Verification & Bulk Broadcast](#36-newsletter-subscriptions-verification--bulk-broadcast)
4. [Static, Hardcoded & Architectural Elements](#4-static-hardcoded--architectural-elements)
5. [Database Seeding & YAML Records Catalog](#5-database-seeding--yaml-records-catalog)
6. [Master CMS & Model Control Matrix](#6-master-cms--model-control-matrix)

---

## 1. Executive Summary & Platform Architecture

**Hotel Ichchha** is a 5-star luxury hospitality platform located in Simara, Bara, Nepal. The platform is designed with a **modular domain-driven architecture** consisting of **17 custom Django apps**.

```
                           ┌────────────────────────────────────────────────────────┐
                           │               Hotel Ichchha Web Platform               │
                           └──────────────────────────┬─────────────────────────────┘
                                                      │
         ┌────────────────────────────────────────────┼────────────────────────────────────────────┐
         │                                            │                                            │
         ▼                                            ▼                                            ▼
┌──────────────────┐                       ┌───────────────────────┐                    ┌──────────────────┐
│  Guest-Facing UI │                       │ Custom Admin Portal   │                    │ Async & Services │
│ (Tailwind/Alpine)│                       │ (/admin/ - Tailwind)  │                    │ (Celery/Redis/DB)│
└────────┬─────────┘                       └──────────┬────────────┘                    └────────┬─────────┘
         │                                            │                                          │
         ├─ Homepage & About CMS                      ├─ Multi-Currency Analytics Dashboard      ├─ Redis Caching
         ├─ Rooms & Availability Check                ├─ Booking & Invoice Management            ├─ Celery Workers
         ├─ Multi-Currency Checkout                   ├─ Room CRUD & Duplication Action          ├─ Email Service (SMTP)
         ├─ Dining & Event Inquiries                  ├─ Dynamic CMS & Hero Banners              ├─ Automated DB Backup
         └─ Gallery & Lightbox Sliders                └─ Settings, Currencies & Processors       └─ WhiteNoise Assets
```

### Key Architectural Characteristics:
* **Bespoke Custom Admin Dashboard (`admin_dashboard/`)**: Developed from the ground up using TailwindCSS, Alpine.js, and Chart.js. Third-party admin wrappers (such as Django Unfold) were replaced with clean, lightweight, fully customizable Django views and templates.
* **White-Label & Dynamic Site Identity**: Site name, logos (light, dark, admin), browser favicons, admin brand labels, theme options, contact info, and social links are managed directly from the database.
* **Server-Side Multi-Currency Isolation**: Seamless switching between USD, NPR, EUR, GBP, etc., with cookie persistence without requiring live API exchange rate lookups or duplicate room records.
* **Interactive Media Engine**: Zero-crop photo sliders, Alpine.js full-screen lightbox zoom, multi-image galleries per venue/activity, and automated imagekit thumbnail generation.
* **Production Deployment Ready**: Containerized with `Dockerfile` and `docker-compose.yml` for PostgreSQL 15, Redis 7, Gunicorn, and Celery.

---

## 2. Admin-Controlled Content & CMS Guide

### 2.1 Global Hotel Settings & White-Label Branding
* **Admin Path:** `Settings -> Hotel Global Settings` (`/admin/settings/`)
* **Model:** `settings_manager/models/hotel_settings.py` (`HotelSettings` — Singleton)
* **Description:** Controls global branding, logos, contact details, social media links, and administrative labels across the entire website and admin panel.

| Field | Type | Description / Live Placement |
|---|---|---|
| `site_name` | String | Hotel brand name displayed in header, footer, page titles, and invoice headers |
| `logo` | Image | Primary brand logo used in header, login pages, and guest invoices |
| `logo_dark` | Image | Dark-mode or high-contrast variant of the logo |
| `favicon` | Image | Browser tab icon (`.ico`, `.png`, `.svg`) injected in HTML `<head>` |
| `admin_logo` | Image | Logo rendered in the top-left sidebar of the admin dashboard and admin login |
| `admin_title` | String | Browser tab title displayed across all `/admin/*` views |
| `admin_label` | String | Brand label text rendered in the admin dashboard sidebar |
| `theme` | Choice | Default platform theme (Light, Dark, Luxury Gold, Festival) |
| `contact_phone` | String | Primary phone number rendered in header top bar, footer, and invoice metadata |
| `contact_email` | Email | Official inquiry email rendered in header top bar, footer, and invoices |
| `inquiry_notification_email`| Email | Staff inbox receiving instant email notifications for new guest inquiries and contact queries |
| `address` | String | Hotel physical address rendered in footer, contact page, and invoice header |
| `google_maps_iframe`| Text (HTML) | Raw iframe embed code for Google Maps displayed on contact page |
| `facebook_url` | URL | Link to hotel Facebook page in footer |
| `instagram_url`| URL | Link to hotel Instagram profile in footer and homepage feed |
| `twitter_url` | URL | Link to hotel X/Twitter profile in footer |
| `youtube_url` | URL | Link to hotel YouTube channel in footer |
| `tripadvisor_url`| URL | Link to hotel TripAdvisor profile in footer |
| `header_badge` | String | Top navigation announcement badge (e.g. "⭐ 5-Star Luxury Resort") |
| `header_cta_text` / `url`| String | Top header call-to-action button label and URL (e.g. "Book A Stay" -> `/rooms/`) |
| `about_text` | Text | Short hotel introduction paragraph rendered in the footer brand column |
| `copyright_text`| String | Custom copyright line rendered at the bottom of all pages |
| `awards_text` | String | Footer awards and accreditation badge (e.g. "Awards: World Luxury Hotel Winner 2026") |
| `contact_form_title`| String | Heading text rendered above the public contact inquiry form |
| `contact_form_subtitle`| String | Subtitle instructions rendered beneath the contact inquiry heading |
| `contact_form_button_text`| String | Submit button label rendered on the public contact inquiry form |

---

### 2.2 Navigation Menus & Hierarchy
* **Admin Path:** `Settings -> Navigation Menus` (`/admin/settings/navigation/`)
* **Model:** `settings_manager/models/navigation.py` (`Navigation`)
* **Description:** Dynamically renders desktop header menus, dropdown menus, mobile navigation drawers, and categorized footer link columns.

| Field | Type | Description |
|---|---|---|
| `name` | String | Display title of the menu item (e.g. "Rooms & Suites", "Gastronomy") |
| `url` | String | Target internal path (e.g. `/rooms/`) or external URL |
| `position` | Choice | Placement: `header` (Main Navigation), `footer_quick` (Quick Links), `footer_services` (Our Services), `footer_ota` (OTA Partners) |
| `order` | Integer | Sort sequence for display order |
| `parent` | FK (Self) | Optional parent item for multi-level nested dropdown menus |
| `is_published` | Boolean | Toggle link visibility without deleting the database record |

---

### 2.3 Multi-Currency System
* **Admin Path:** `Settings -> Currencies` (`/admin/settings/currencies/`)
* **Model:** `settings_manager/models/currency.py` (`Currency`)
* **Description:** Defines supported currencies for guest browsing and checkout.

| Field | Type | Description |
|---|---|---|
| `iso_code` | String (3) | ISO 4217 Currency Code (e.g. `USD`, `NPR`, `EUR`, `GBP`) |
| `name` | String | Full name (e.g. "US Dollar", "Nepalese Rupee") |
| `symbol` | String | Currency symbol (e.g. `$`, `Rs.`, `€`, `£`) |
| `sequence` | Integer | Display order in the frontend currency switcher modal and mobile drawer |
| `is_published` | Boolean | Enable/disable currency from the public switcher |
| `is_default` | Boolean | Default currency used when no cookie is present |

---

### 2.4 Payment Processors Configuration
* **Admin Path:** `Settings -> Payment Processors` (`/admin/payments/processors/`)
* **Model:** `payments/models/payment_processor.py` (`PaymentProcessor`, `PaymentProcessorCurrency`)
* **Description:** Manages available payment gateways and links them to accepted currencies.

| Field | Type | Description |
|---|---|---|
| `name` | String | Gateway display name (e.g. "eSewa ePay", "Khalti", "Stripe Checkout") |
| `code` | Slug | Unique system identifier (`esewa`, `khalti`, `stripe`, `bank_transfer`, `cash`) |
| `payment_currencies`| M2M | Linked `Currency` records that are permitted to pay through this gateway |
| `apply_tax` | Boolean | Designates whether VAT/tax (13%) is added during checkout with this gateway |
| `is_published` | Boolean | Enable/disable gateway on guest checkout page |

---

### 2.5 Admin Real-Time Notifications
* **Admin Path:** `Notifications` (`/admin/notifications/`)
* **Model:** `admin_dashboard/models/notification.py` (`Notification`)
* **Description:** Dispatches real-time alerts to staff regarding reservations, payments, and guest inquiries.

| Field | Type | Description |
|---|---|---|
| `notification_type` | Choice | `booking_created`, `payment_success`, `booking_confirmed`, `inquiry_received` |
| `title` | String | Alert title (e.g. "New Booking Placed [ICH-9821]") |
| `message` | Text | Detailed summary of the event |
| `link_url` | String | Direct target URL (e.g. `/admin/bookings/42/`) |
| `is_read` | Boolean | Read/unread status; unread count displays in top navbar badge |
| `created_at` | DateTime | Timestamp of event dispatch |

---

### 2.6 Homepage — Hero Carousel
* **Admin Path:** `CMS -> Hero Slides` (`/admin/cms/hero-slides/`)
* **Model:** `homepage/models/hero_slide.py` (`HeroSlide`)
* **Description:** Full-screen carousel at the top of the homepage with typography animations.

| Field | Type | Description |
|---|---|---|
| `title` | String | Main headline text |
| `subtitle` | String | Sub-headline or tagline above the main title |
| `background_image` | Image | High-resolution background photo (validated max 5 MB) |
| `background_video_url` | URL | Optional background video stream (MP4 or streaming URL) |
| `overlay_opacity` | Decimal | Darkness of dark tint overlay (0.00 = transparent, 1.00 = solid black) |
| `cta_text` | String | Primary button text (e.g. "Explore Rooms") |
| `cta_url` | String | Primary button destination link (e.g. `/rooms/`) |
| `cta2_text` | String | Secondary button text (e.g. "Discover Dining") |
| `cta2_url` | String | Secondary button destination link (e.g. `/dining/`) |
| `title_animation` | Choice | CSS animation: Fade In Down, Fade In Up, Zoom In, Slide In |
| `subtitle_animation`| Choice | CSS animation for subtitle |
| `order` | Integer | Slide sequence |
| `is_active` | Boolean | Toggle slide visibility |

---

### 2.7 Homepage — About Preview
* **Admin Path:** `CMS -> About Preview` (`/admin/cms/about-preview/`)
* **Model:** `homepage/models/about_preview.py` (`AboutPreview` — Singleton)
* **Description:** Homepage introductory section highlighting hotel background, promo video, and statistics counters.

| Field | Type | Description |
|---|---|---|
| `title` | String | Section heading (e.g. "Welcome to Hotel Ichchha") |
| `subtitle` | String | Tagline (e.g. "A Verdant 5-Star Sanctuary in Simara") |
| `content` | Text | Detailed descriptive body paragraph |
| `image` | Image | Featured photograph |
| `video_url` | URL | YouTube/Vimeo embed URL or external video link |
| `video_file` | File | Direct uploaded MP4 video asset |
| `stat1_value / stat1_label` | String | Counter 1 (e.g. "96" / "Luxury Rooms & Suites") |
| `stat2_value / stat2_label` | String | Counter 2 (e.g. "5-Star" / "Certified Luxury") |
| `stat3_value / stat3_label` | String | Counter 3 (e.g. "3" / "Gourmet Restaurants") |
| `stat4_value / stat4_label` | String | Counter 4 (e.g. "1,000+" / "Pax Banquet Capacity") |

---

### 2.8 About Page CMS & Executive Narrative
* **Admin Path:** `CMS -> About Page CMS Settings` (`/admin/cms/about-page/`)
* **Model:** `about/models/about_page.py` (`AboutPage` — Singleton)
* **Description:** Comprehensive dynamic CMS controlling the dedicated About Page (`/about/`).

| Section | Key Fields | What It Controls |
|---|---|---|
| **Hero Banner** | `hero_badge`, `hero_title`, `hero_subtitle`, `hero_description`, `hero_image`, `hero_button_text`, `hero_button_url` | Top hero banner with badges, titles, descriptions, and CTA buttons |
| **Story & Heritage** | `story_badge`, `story_title`, `story_subtitle`, `story_content`, `story_floating_badge`, `story_image_1`, `story_image_2` | Hotel heritage story narrative and dual showcase photo frames |
| **6 Quick Feature Badges**| `story_feature_1..6_icon`, `story_feature_1..6_text` | Six feature badges (e.g., 96 Luxury Rooms, Airport 5 Min, Ayurvedic Spa, etc.) |
| **Statistics Strip** | `stat1..4_value`, `stat1..4_label` | Four animated counter badges (96 Rooms, 5-Star, 27+ Years Leadership, 1,000+ Pax Hall) |
| **CEO Narrative** | `ceo_badge`, `ceo_title`, `ceo_name`, `ceo_role`, `ceo_credentials`, `ceo_image`, `ceo_quote`, `ceo_message`, `ceo_signature_text` | Executive message from CEO Rewanta Prasad Dhaubhadel (Rebu), Swiss Hotel Management School credentials, portrait, and signature |
| **Philosophy & Core Values**| `mission_title`, `mission_text`, `vision_title`, `vision_text`, `values_title`, `values_text` | Tri-column Mission, Vision, and Core Values cards |
| **Leadership Header** | `team_badge`, `team_title`, `team_subtitle` | Section heading for Board of Directors & Leadership |
| **Video Showcase** | `video_badge`, `video_title`, `video_subtitle`, `video_url`, `video_file`, `video_thumbnail` | Visual resort video tour with direct MP4 file upload, URL, and poster thumbnail |
| **Facilities Header** | `facilities_badge`, `facilities_title`, `facilities_subtitle` | Section heading for 5-Star Amenities grid |
| **Bottom CTA Banner** | `cta_badge`, `cta_title`, `cta_subtitle`, `cta_button_text`, `cta_button_url`, `cta_image` | Bottom reservation banner linking directly to rooms and concierge |

---

### 2.9 Leadership Team & Board of Directors
* **Admin Path:** `CMS -> Leadership Team` (`/admin/cms/team-members/`)
* **Model:** `about/models/team_member.py` (`TeamMember`)
* **Description:** Manages individual executive profiles rendered on the About page.

| Field | Type | Description |
|---|---|---|
| `name` | String | Full name of executive / director |
| `role` | String | Professional designation (e.g. "Chairman", "Chief Executive Officer", "Executive Chef") |
| `bio` | Text | Professional biography and achievements |
| `image` | Image | Portrait photograph (validated max 5 MB) |
| `order` | Integer | Display sequence in the team grid |
| `is_published` | Boolean | Toggle public visibility |
| `linkedin_url` | URL | LinkedIn profile link |
| `email` | Email | Direct contact email |
| `twitter_url` | URL | X / Twitter profile link |
| `facebook_url` | URL | Facebook profile link |

---

### 2.10 5-Star Facility Highlights
* **Admin Path:** `CMS -> Facility Highlights` (`/admin/cms/facility-highlights/`)
* **Model:** `about/models/facility_highlight.py` (`AboutFacility`)
* **Description:** Manages key amenity highlights displayed on the About page.

| Field | Type | Description |
|---|---|---|
| `title` | String | Amenity title (e.g. "Simara Airport Shuttle", "Ayurvedic Wellness Spa") |
| `description` | String | Short summary sentence |
| `icon` | String | FontAwesome icon class (e.g. `fa-solid fa-plane-arrival`, `fa-solid fa-spa`) |
| `order` | Integer | Display sequence |
| `is_published` | Boolean | Toggle public visibility |

---

### 2.11 Rooms, Accommodation & Availability Calendar
* **Admin Path:** `Rooms -> Rooms List` (`/admin/rooms/`)
* **Models:** `rooms/models/room.py`, `room_category.py`, `room_base_price.py`, `room_seasonal_price.py`, `room_image.py`, `room_facility.py`, `room_policy.py`, `room_availability.py`
* **Description:** Core inventory and pricing management engine.

#### 1. Main Room Record (`Room`)
* `title`: Room name (e.g. "Presidential Suite", "Executive King Room")
* `room_number`: Room code or number identifier (e.g. "101", "102", "Villa A")
* `category`: ForeignKey to `RoomCategory` (e.g. Suites, Deluxe, Executive)
* `description`: Full rich-text description
* `highlights`: Bullet points highlighting key room features
* `tax_percentage`: VAT rate (default: `13.00%`)
* `room_size`: Room area in sq. ft. or sq. meters
* `total_rooms`: Total physical inventory count available for this specific room listing
* `max_adults` / `max_children`: Guest capacity thresholds
* `bed_type`: Bed configuration (e.g. "King Bed", "Two Twin Beds")
* `facilities`: ManyToMany relation to `RoomFacility`
* `included_addons`: ManyToMany to `booking.Addon` — complimentary included services (e.g. Complimentary Breakfast, Airport Shuttle, Welcome Drink) rendered with icons on the public detail page
* `allow_custom_addons`: Boolean toggle determining whether guests can select optional paid add-ons during room reservation checkout
* `virtual_tour_url`: 360-degree interactive 3D virtual tour embed link
* `video_url`: YouTube/Vimeo video walkthrough link
* `is_featured`: Pins room to the homepage showcase slider
* `is_published`: Controls public listing visibility

#### 2. Multi-Currency Base Rates (`RoomBasePrice`)
* `currency`: Linked `Currency` record (USD, NPR, EUR, GBP)
* `base_price`: Standard nightly rate in that currency
* `discount_price`: Optional discounted promotional rate

#### 3. Seasonal Overrides (`RoomSeasonalPrice`)
* `name`: Promotional campaign title (e.g. "Festival Festive Season", "Summer Getaway")
* `currency`: Optional currency override. When left blank, acts as a **wildcard** for all currencies
* `start_date` / `end_date`: Calendar validity window
* `price_override`: Special promotional nightly rate during this period
* `is_active`: Toggle campaign status

#### 4. Room Multi-Image Gallery (`RoomImage`)
* `image`: Uploaded photograph (with thumbnail generation)
* `is_primary`: Designates primary card cover image
* `alt_text`: Accessibility description

#### 5. Room Policies (`RoomPolicy`)
* `title`: Policy name (e.g. "Cancellation Policy", "Child & Extra Bed Policy")
* `description`: Full legal policy terms

#### 6. Room Availability Calendar (`RoomAvailability`)
* `room`: Linked `Room` record
* `date`: Calendar date
* `is_available`: Boolean toggle (`True` = Available, `False` = Blocked/Reserved)
* `booking`: Linked `Booking` record (auto-assigned upon reservation confirmation)

#### 7. Room Duplication Action
* In `/admin/rooms/`, administrators can click **Duplicate Room** to instantly clone a room record with all associated base prices, facilities, and policy rules for fast onboarding of similar room types.

#### 8. Complimentary Inclusions vs. Optional Paid Add-ons
* **Public Room Detail**: Renders a dedicated "Complimentary Inclusions" card displaying all linked `included_addons` with their respective FontAwesome icons.
* **Checkout Pipeline**: When `allow_custom_addons` is enabled, guests can browse and attach optional paid services (`Addon`) to their reservation. Any services already provided as complimentary inclusions are automatically excluded from the paid add-on selection to prevent double charging.

---

### 2.12 Booking Add-on Services
* **Admin Path:** `Marketing / Services -> Add-on Services` (`/admin/addons/`)
* **Models:** `booking/models/addon.py` (`Addon`, `AddonPrice`)
* **Description:** Unified ancillary services offered to guests during room booking checkouts or banquet inquiry submissions.

| Field | Type | Description |
|---|---|---|
| `name` | String | Service name (e.g. "Airport Private Pick-up", "Candlelight Dinner Setup", "Audio Visual Package") |
| `description` | Text | Description shown to guests during checkout or venue inquiry |
| `icon` | String | FontAwesome icon class (e.g. `fa-car`, `fa-utensils`, `fa-bed`, `fa-video`, `fa-microphone`) |
| `applies_to` | Choice | Applicable domain: `room` (Room stays only), `events` (Event & banquet halls only), or `both` (Universal) |
| `price_type` | Choice | Billing type: `per_night`, `per_person`, `per_person_per_night`, `per_booking` |
| `is_active` | Boolean | Toggle add-on availability |
| `order` | Integer | Display sequence during selection |
| `prices` (Inline) | FK | Multi-currency pricing (`AddonPrice`) in USD, NPR, EUR, GBP |

#### Admin Add-on Dashboard Features:
* **Scope Filtering**: Filter tabs for **All Services**, **Room Stay Add-ons**, and **Event & Banquet Add-ons** with luxury gold active states.
* **Venue Association**: Event venues can selectively enable/disable custom add-ons via `venue.allow_custom_addons` and choose allowed items via `venue.available_addons`.

---

### 2.13 Booking Discount Coupons & Currency Thresholds
* **Admin Path:** `Marketing -> Coupons` (`/admin/coupons/`)
* **Models:** `booking/models/coupon.py` (`Coupon`, `CouponMinSpend`)
* **Description:** Promo codes that calculate percentage or fixed discounts during checkout.

| Field | Type | Description |
|---|---|---|
| `code` | String | Unique promo code string (e.g. `ICHCHHA25`, `FESTIVE10`) |
| `description` | String | Internal notes for staff |
| `discount_type` | Choice | `percentage` (e.g. 15%) or `fixed` (e.g. 2000 in guest currency) |
| `discount_value` | Decimal | Discount rate or fixed deduction |
| `applicable_to` | Choice | `all` (Rooms & Services) or `room` (Room stays only) |
| `min_spend` | Decimal | Fallback minimum booking amount |
| `max_uses` | Integer | Maximum lifetime redemptions allowed (leave blank for unlimited) |
| `use_count` | Integer | Real-time counter of total redemptions completed |
| `valid_from / valid_to`| DateTime | Active promotional window |
| `is_active` | Boolean | Enable/disable promo code instantly |
| `min_spends` (Inline)| FK | Multi-currency minimum order thresholds (`CouponMinSpend`) |

---

### 2.14 Dining Venues, PDF Menus & Multi-Image Galleries
* **Admin Path:** `Dining -> Dining Venues` (`/admin/dining/`)
* **Models:** `dining/models/venue.py`, `dining/models/venue_image.py`
* **Description:** Manages restaurant and bar profiles, signature dishes, menus, and photo sliders.

| Field | Type | Description |
|---|---|---|
| `name` | String | Restaurant/bar name (e.g. "The Royal Kitchen", "Poolside Bistro") |
| `category` | Choice | Restaurant, Bar & Lounge, Cafe, Rooftop, Pool Bar, Fine Dining |
| `description` | Text | Detailed venue ambiance and culinary concept |
| `timings` | String | Operating hours (e.g. "6:30 AM - 11:00 PM Daily") |
| `menu_pdf` | File (PDF) | Downloadable food & beverage PDF menu |
| `chef_name / chef_bio / chef_image` | Various | Executive chef profile, biography, and portrait |
| `capacity` | Integer | Seating capacity |
| `featured_dishes` | Text | Comma-separated signature dishes |
| `video_url` | URL | Video walkthrough |
| `image` | Image | Primary cover photo (with `display_image_url` fallback) |
| `images` (Inline)| FK | Multi-image gallery (`DiningVenueImage`) with primary selection |
| `is_featured` | Boolean | Featured in homepage dining slider |
| `is_published` | Boolean | Toggle public visibility |

---

### 2.15 Recreation, Spa & Wellness Activities
* **Admin Path:** `Recreation -> Recreation & Activities` (`/admin/recreation/`)
* **Models:** `recreation/models/activity.py`, `recreation/models/activity_image.py`
* **Description:** Manages resort activities, wellness treatments, and recreational amenities.

| Field | Type | Description |
|---|---|---|
| `name` | String | Activity title (e.g. "Ayurvedic Rejuvenation Spa", "Infinity Swimming Pool") |
| `category` | Choice | Spa, Pool, Gym, Kids Zone, Casino, Adventure, Safari, Games |
| `description` | Text | Full activity overview |
| `timings` | String | Hours of operation (e.g. "7:00 AM - 9:00 PM") |
| `price_info` | String | Pricing badge (e.g. "Complimentary for Guests", "From $40/hr") |
| `capacity` | Integer | Max participants per session |
| `image` | Image | Primary cover image |
| `images` (Inline)| FK | Multi-image gallery (`RecreationActivityImage`) with zero-crop lightbox |
| `is_featured` | Boolean | Featured on homepage |
| `is_active` | Boolean | Toggle public visibility |

---

### 2.16 Conference, Banquet & Event Venues
* **Admin Path:** `Conference -> Events & Hall` (`/admin/conference/`)
* **Models:** `conference/models/venue.py`, `conference/models/event_type.py`, `conference/models/venue_layout.py`, `conference/models/venue_base_price.py`, `conference/models/venue_image.py`
* **Description:** Manages convention halls, banquet spaces, meeting rooms, occasion categories, and seating arrangements.

#### 1. Event Venue Record (`EventVenue`)
| Field | Type | Description |
|---|---|---|
| `name` | String | Hall name (e.g. "Grand Ichchha Ballroom", "Summit Meeting Hall") |
| `description` | Text | Detailed venue features, audio-visual capabilities, and lighting |
| `capacity` | Integer | Max theater/floating capacity (e.g. 1000) |
| `event_types` | M2M | Linked occasion categories (`EventType`) suitable for this hall |
| `layouts` | M2M | Linked seating layouts (`VenueLayout`) supported by this hall |
| `allow_custom_addons` | Boolean | Toggles whether guests can select optional add-ons during inquiry |
| `available_addons` | M2M | Specific add-on services (`booking.Addon`) available for this hall |
| `base_prices` (Inline)| FK | Multi-currency starting rental rates (`VenueBasePrice`) |
| `image` | Image | Primary cover photograph |
| `images` (Inline)| FK | Multi-image gallery (`EventVenueImage`) with zero-crop lightbox zoom |
| `is_featured` | Boolean | Featured on homepage events carousel |
| `is_active` | Boolean | Toggle public listing visibility |

#### 2. Event Occasion Categories (`EventType`)
* **Path:** `/admin/conference/?tab=event_types`
* Manages occasion types (Weddings & Receptions, Corporate Conferences, Gala Dinners, Seminars & Workshops, Executive Board Meetings, Social Celebrations) with hero imagery, descriptions, display order, and active toggles.
* **Public Form Filter**: The public inquiry form dynamically filters occasion options to display *only* those categories linked to the selected venue.

#### 3. Venue Seating Layouts (`VenueLayout`)
* Manages seating arrangements (Theatre, Banquet, Classroom, Boardroom, U-Shape, Reception) with icons and display ordering.

---

### 2.17 Resort Photo & Video Gallery
* **Admin Path:** `CMS -> Gallery Items & Categories` (`/admin/cms/gallery/`)
* **Models:** `gallery/models/category.py`, `gallery/models/item.py`
* **Description:** Media showcase categorized into filterable tabs with video and drone tags.

| Model | Key Fields | Description |
|---|---|---|
| **GalleryCategory** | `name`, `slug`, `order`, `is_published` | Tab categories (e.g. Rooms, Dining, Pool & Spa, Events, Aerial) |
| **GalleryItem** | `category`, `image`, `caption`, `is_video`, `is_drone`, `video_url`, `virtual_tour_url`, `order`, `is_published` | Individual media item with `imagekit` thumbnail, 360 tour embed, and drone tags |

---

### 2.18 Contact Branches & Maps
* **Admin Path:** `Contact -> Branches & Messages` (`/admin/contact/`)
* **Models:** `contact/models/branch.py` (`HotelBranch`), `contact/models/inquiry_category.py` (`InquiryCategory`)
* **Description:** Manages contact cards for the main hotel, regional sales offices, and dynamic inquiry categories.

#### 1. Hotel Branch Record (`HotelBranch`)
| Field | Type | Description |
|---|---|---|
| `name` | String | Office name (e.g. "Hotel Ichchha — Main Resort", "Kathmandu Sales Office") |
| `address` | String | Complete address |
| `phone` | String | Office direct telephone number |
| `email` | Email | Office contact email |
| `maps_iframe` | Text | Google Maps iframe embed code for interactive map display |
| `is_main` | Boolean | Highlights as the primary resort location |
| `is_published` | Boolean | Toggle visibility on the contact page |

#### 2. Inquiry Categories (`InquiryCategory`)
* **Admin Path:** `/admin/contact/?tab=inquiries`
* Dynamically manages category classifications for guest inquiries (General Inquiries, Room Booking & Rates, Dining & Table Reservations, Conference & Event Planning, Spa & Wellness, Career & Employment).
* Fields: `name`, `slug`, `description`, `display_order`, `is_active`.
* Public contact form renders active categories dynamically; admin dashboard filters messages using categorized pill tabs.

---

### 2.19 Blog Posts & Editorial Articles
* **Admin Path:** `CMS -> Blog Posts` (`/admin/cms/blogs/`)
* **Model:** `blogs/models/post.py` (`BlogPost`)
* **Description:** Publishing platform for hotel news, travel guides, and press releases.

| Field | Type | Description |
|---|---|---|
| `title` | String | Article headline |
| `slug` | Slug | SEO-friendly URL slug (auto-generated) |
| `content` | Text | Full article body content |
| `featured_image`| Image | High-resolution cover photo |
| `author` | FK (User)| Author attribution |
| `is_active` | Boolean | Toggle article publication |

---

### 2.20 Nearby Places & Tourist Attractions
* **Admin Path:** `CMS -> Attractions` (`/admin/cms/attractions/`)
* **Model:** `nearby_places/models/attraction.py` (`Attraction`)
* **Description:** Guide to regional landmarks, national parks, and transit hubs.

| Field | Type | Description |
|---|---|---|
| `name` | String | Landmark title (e.g. "Chitwan National Park", "Gadhimai Temple", "Simara Airport") |
| `category` | Choice | Airport, National Park, Religious Site, Tourist Attraction, Border, City |
| `distance` | String | Approximate distance (e.g. "15 km", "5 mins drive") |
| `travel_time` | String | Travel duration (e.g. "25 minutes by car") |
| `maps_url` | URL | External Google Maps directions URL |
| `image` | Image | Attraction photograph |
| `description` | Text | Summary of why guests should visit |
| `order` | Integer | Display sequence |
| `is_active` | Boolean | Toggle public visibility |

---

### 2.21 Guest Testimonials & Reviews
* **Admin Path:** `CMS -> Testimonials` (`/admin/cms/testimonials/`)
* **Model:** `testimonials/models/testimonial.py` (`Testimonial`)
* **Description:** Curated guest reviews displayed on the homepage and about page.

| Field | Type | Description |
|---|---|---|
| `guest_name` | String | Reviewer full name |
| `guest_image` | Image | Reviewer photo (optional) |
| `country` | String | Guest origin country (e.g. "United Kingdom", "India", "Nepal") |
| `source` | Choice | Platform tag: Google, Booking.com, Agoda, Tripadvisor, Direct |
| `rating` | Integer | Star rating (1 to 5) |
| `review_text` | Text | Guest review quote |
| `is_featured` | Boolean | Display in the homepage testimonials carousel |
| `is_published`| Boolean | Toggle global visibility |

---

### 2.22 SEO Engine & Dynamic Page Hero Banners
* **Admin Path:** `CMS -> SEO Page Data` (`/admin/cms/seo/`)
* **Model:** `seo/models/seo_data.py` (`SEOData`)
* **Description:** Manages page-specific metadata and hero banners for any URL on the site.

| Group | Field | Description |
|---|---|---|
| **Page Matching** | `path` | Exact URL path to match (e.g. `/rooms/`, `/dining/`, `/about/`, `/contact/`) |
| **Meta Information**| `meta_title`, `meta_description`, `canonical_url` | Browser tab title, search engine description snippet, and canonical link |
| **Hero Banner Header**| `header_subtitle`, `header_title`, `header_description`, `header_image` | Small uppercase subtitle, main large heading, intro description, and custom background photo |
| **Social Sharing (OG)**| `og_title`, `og_description`, `og_image` | OpenGraph tags rendered when links are shared on Facebook, WhatsApp, or LinkedIn |
| **Twitter Card** | `twitter_card` | Summary or Summary Large Image card type |
| **Structured Data**| `structured_data` | Custom JSON-LD schema markup for Google Rich Snippets |

---

### 2.23 User Accounts & Role Permissions
* **Admin Path:** `Accounts -> Users` (`/admin/users/`)
* **Model:** `accounts/models/user.py` (`User`)
* **Description:** Manages guest accounts, reception staff, managers, and superusers.

| Field | Type | Description |
|---|---|---|
| `username` | String | Unique login username |
| `email` | Email | User email address |
| `role` | Choice | Account role (`guest`, `staff`, `admin`, `superuser`) |
| `phone_number` | String | Contact telephone number |
| `avatar` | Image | Profile photo |
| `is_active` | Boolean | Account activation status |
| `is_staff` | Boolean | Grants access to `/admin/` portal |
| `is_superuser` | Boolean | Grants all administrative permissions |

---

## 3. Guest-Submitted Data & Staff Workflows

Guest-submitted records are generated through frontend guest interactions and reviewed/managed by staff within the custom admin dashboard:

```
┌─────────────────────────┐         ┌─────────────────────────┐         ┌─────────────────────────┐
│   Guest Submits Form    │         │ Admin Receives Alert    │         │ Staff Action / Workflow │
│ (Booking/Inquiry/Table) ├────────►│ (Navbar Notification)   ├────────►│ (Confirm/Invoice/Reply) │
└─────────────────────────┘         └─────────────────────────┘         └─────────────────────────┘
```

### 3.1 Room Reservations & Invoicing
* **Admin Path:** `Bookings -> All Bookings` (`/admin/bookings/`)
* **Model:** `booking/models/booking.py` (`Booking`)
* **Workflow & Status Machine:**
  1. **Draft / Pending Payment**: Created during checkout before payment is completed.
  2. **Confirmed**: Set automatically upon payment gateway callback or manually by front desk.
  3. **Checked In**: Guest has arrived and checked into their room.
  4. **Checked Out**: Guest has departed.
  5. **Cancelled**: Reservation cancelled; dates released in `RoomAvailability`.
* **Printable Invoice (`/admin/bookings/<id>/invoice/`)**:
  - Itemized room stay breakdown (room title, nightly rates, night tallies, subtotal).
  - Selected add-on services and coupon deductions.
  - 13% VAT tax line and final total with explicit currency symbol and ISO code.
  - Direct print action (`window.print()`).

---

### 3.2 Payment Transactions
* **Admin Path:** `Payments -> Payment Transactions` (`/admin/payments/`)
* **Model:** `payments/models/payment.py` (`Payment`)
* **Workflow & Email Dispatch:**
  - Records gateway name (`esewa`, `khalti`, `stripe`, `bank_transfer`, `cash`), transaction UUID, amount paid, tax amount, currency, and raw JSON gateway response.
  - Automatically marks linked `Booking` as `confirmed` upon successful transaction verification.
  - Dispatches automated branded HTML invoice email to the guest via `core.services.email_service.send_booking_invoice_email`.
  - Concurrently dispatches an instant booking alert email to the hotel's inbox via `core.services.email_service.send_hotel_booking_notification_email` (`templates/emails/booking_notification_hotel_email.html`), providing staff with guest contact info, room details, payment total, and a direct link to the booking in the admin dashboard.

---

### 3.3 Dining Table Reservations
* **Admin Path:** `Dining -> Table Reservations` (`/admin/dining/?tab=reservations` or `/admin/dining/reservations/`)
* **Model:** `dining/models/reservation.py` (`DiningReservation`)
* **Workflow & Administrative Enhancements:**
  - **Public Form & Validation**: Captures guest name, email, phone, venue, date, time slot, party size, and special requests. Public dining detail page features an interactive booking modal with capacity validation (guest count cannot exceed venue capacity).
  - **Direct Notification Routing**: Clicking a dining reservation alert in the admin notification dropdown routes directly to `/admin/dining/?tab=reservations` with the tab automatically activated.
  - **5 Live KPI Summary Cards**:
    1. *Total Reservations* (Lifetime volume)
    2. *Pending Action* (Prominent amber alert badge requiring front-desk confirmation)
    3. *Today's Bookings* (Guests scheduled for arrival today)
    4. *Upcoming Bookings* (Future reservations)
    5. *Cancelled / Archived* (Inactive reservations)
  - **Search & Filter Toolbar**: Search reservations by guest name, contact email, phone number, or notes. Filter by confirmation status (`pending`, `confirmed`, `cancelled`) or dining venue.
  - **Guest Special Requests Callout**: Guest dietary notes and special requirements are highlighted with gold icon indicators directly on the table row.
  - **Reservation Dossier Modal**: Quick-view AJAX dossier modal (`/admin/dining/reservations/<id>/detail-json/`) rendered via Alpine.js displaying full guest info, venue, seating time, and staff notes without page reloads.
  - **"Clear All" Batch Action**: Safe, modal-confirmed batch purge action (`/admin/dining/reservations/clear-all/`) allowing staff to clear test or historical reservations with a single click.

---

### 3.4 Conference & Banquet Inquiries
* **Admin Path:** `Conference -> Event Inquiries` (`/admin/conference/?tab=inquiries` or `/admin/conference/inquiries/`)
* **Model:** `conference/models/inquiry.py` (`EventInquiry`)
* **Workflow & Administrative Enhancements:**
  - **Inquiry Submission & Filtering**: Captures event organizer details, chosen venue, event type (`EventType`), seating layout (`VenueLayout`), expected event date, guest count, catering needs, selected add-ons, and custom requirements. Dynamic JavaScript filtering on the public venue detail form restricts occasion options to *only* those toggled for the specific venue.
  - **Submission Loading State**: Form submission button automatically displays an animated SVG spinner and disables itself to prevent duplicate submissions.
  - **Direct Notification Routing**: Clicking an event inquiry notification in the navbar dropdown routes directly to `/admin/conference/?tab=inquiries`.
  - **Schedule Conflict Detection (`has_conflict`)**: Automated scheduling analysis cross-references the requested event date against other inquiries and confirmed bookings for the same hall, displaying a high-visibility amber warning pill for overlapping dates.
  - **6 Live KPI Summary Cards**: Total Inquiries, Pending Action (red alert badge), In Negotiation, Confirmed Events, Date Conflicts (amber badge), and Cancelled.
  - **Upcoming Schedule Preview**: Sidebar preview widget outlining upcoming banquet dates and hall occupancy at a glance.
  - **Interactive Dossier Modal**: Quick-view modal (`/admin/conference/inquiries/<id>/detail-json/`) showing complete organizer contact info, guest counts, catering selections, layout diagram, and custom requirements.
  - **"Clear All" Batch Action**: Protected batch purge action with modal confirmation (`/admin/conference/inquiries/clear-all/`).

---

### 3.5 Contact Inquiries & SMTP Email Reply Modal
* **Admin Path:** `Contact -> Inquiries` (`/admin/contact/?tab=inquiries` or `/admin/contact/inquiries/`)
* **Model:** `contact/models/inquiry.py` (`ContactInquiry`), `contact/models/inquiry_category.py` (`InquiryCategory`)
* **Workflow & Administrative Enhancements:**
  - **Dynamic Classification**: Guest inquiries are categorized dynamically via `InquiryCategory` models (`General Inquiries`, `Room & Suites Reservations`, `Dining & Table Bookings`, `Conference & Banquets`, `Spa & Recreation`, `Careers & Press`).
  - **Interactive Category Filter Tabs**: Admin contact dashboard provides filter pills with live count badges for each inquiry category.
  - **Form Usability Improvements**: Input fields use standard text cursors, and the submit button triggers an animated loading spinner to confirm submission.
  - **Instant Staff Email Notification**: Dispatches an instant email alert (`templates/emails/contact_inquiry_hotel_email.html`) via `core.services.email_service.send_contact_inquiry_emails` to `hotel_settings.inquiry_notification_email` (or `contact_email`) with direct reply-to headers and link to the admin inquiry dossier.
  - **Integrated SMTP Email Reply Modal**: Admin can click "Reply" to open a modal and send custom HTML responses directly to the guest's email via SMTP without leaving the dashboard (`/admin/contact/inquiries/<id>/reply/`).
  - **"Clear All" Batch Action**: Protected batch purge action with modal confirmation (`/admin/contact/inquiries/clear-all/`).

---

### 3.6 Newsletter Subscriptions, Verification & Bulk Broadcast
* **Admin Path:** `Contact -> Subscribers & Broadcast` (`/admin/contact/subscribers/`, `/admin/contact/broadcast/`)
* **Model:** `contact/models/newsletter.py` (`NewsletterSubscriber`)
* **Workflow:**
  - Guest enters email on frontend -> receives double opt-in verification email with secure token.
  - Guest clicks verification link -> status set to `is_verified=True` and receives automated welcome greeting.
  - Admin can navigate to `/admin/contact/broadcast/` to compose HTML marketing campaigns and send them to all verified subscribers.

---

## 4. Static, Hardcoded & Architectural Elements

The following elements are managed at the codebase and template level:

| Component | Code Location | Architectural Rationale |
|---|---|---|
| **Payment Gateway Drivers** | `payments/views/`, `payments/services/` | Cryptographic signature algorithms (eSewa HMAC-SHA256, Khalti API v2, Stripe webhooks) require code-level execution |
| **Tax Formula (13% VAT)** | `rooms/models/room.py`, `booking/models/booking.py` | Standardized formula: `total = (subtotal - discount) * (1 + tax_rate / 100)` |
| **Seasonal Overlap Algorithm** | `booking/views/public.py` | Iterates over each night of a reservation to match specific or wildcard seasonal pricing rules |
| **Zero-Crop Lightbox Logic** | `templates/base.html`, listing & detail templates | Alpine.js reactive state (`x-data="{ lightbox: false, currentImg: '' }"`) |
| **URL Namespacing & Routing** | `config/urls.py`, individual app `urls.py` | Standardized Django URL routing |
| **TailwindCSS Design System** | `tailwind.config.js`, `static/` | Luxury typography, slate/gold color palette, responsive breakpoints |
| **Image Fallback Hierarchy** | Model properties (`display_image_url`) | Automatically falls back from primary gallery image to first gallery item, to local static fallback, preventing missing images |

---

## 5. Database Seeding & YAML Records Catalog

The platform database can be seeded from 21 structured YAML files in `core/records/` via `python manage.py seed_data`:

| YAML File | Target Model(s) | Records Imported |
|---|---|---|
| `01_hotel_settings.yaml` | `HotelSettings` | Site name, contacts, logos, theme, social links |
| `02_currencies.yaml` | `Currency` | USD ($), NPR (Rs.), EUR (€), GBP (£) |
| `03_navigation_menus.yaml` | `Navigation` | Header, Quick Links, Services, OTA Partner menus |
| `04_about_preview.yaml` | `AboutPreview` | Homepage about section narrative and counters |
| `05_hero_slides.yaml` | `HeroSlide` | 3 full-screen homepage carousel slides |
| `06_room_categories.yaml` | `RoomCategory` | Suites, Deluxe Rooms, Executive Rooms |
| `07_room_facilities.yaml` | `RoomFacility` | Free Wi-Fi, Swimming Pool, Spa, Smart TV, Air Conditioning |
| `08_rooms.yaml` | `Room`, `RoomBasePrice`, `RoomImage`, `RoomFacility`, `RoomPolicy` | 6 complete room types with multi-currency pricing and galleries |
| `09_dining_venues.yaml` | `DiningVenue` | Restaurants, lounges, chef bios, timings, menus |
| `10_recreation_activities.yaml`| `RecreationActivity` | Spa, gym, pool, casino activities |
| `11_event_venues.yaml` | `EventVenue`, `VenueBasePrice` | Ballrooms and conference halls with multi-currency rates |
| `12_attractions.yaml` | `Attraction` | Chitwan National Park, Gadhimai Temple, Simara Airport |
| `13_testimonials.yaml` | `Testimonial` | Verified guest reviews with star ratings |
| `14_seo_banners.yaml` | `SEOData` | Dynamic hero banners and metadata for all listing routes |
| `15_coupons.yaml` | `Coupon`, `CouponMinSpend` | Promo codes with currency-specific minimum spends |
| `16_branches.yaml` | `HotelBranch` | Main Simara Resort and Kathmandu Sales Office |
| `17_payment_processors.yaml` | `PaymentProcessor`, `PaymentProcessorCurrency` | eSewa, Khalti, Stripe, Bank Transfer, Cash gateways |
| `18_about_page.yaml` | `AboutPage`, `TeamMember`, `AboutFacility` | Complete About page CMS, CEO message, leadership profiles |
| `19_event_types.yaml` | `EventType` | 6 banquet occasion categories with cover images and Lucide icons |
| `20_addons.yaml` | `Addon`, `AddonPrice` | Scoped add-on services (`room`, `events`, `both`) with multi-currency prices |
| `21_inquiry_categories.yaml` | `InquiryCategory` | 6 dynamic contact inquiry categories for concierge and booking desks |

> **Relational Cross-Reconciliation (`_reconcile_cross_relationships`)**:
> In addition to importing records in sequential order, the `seed_data` engine executes an automated second-pass cross-reconciliation phase. This binds many-to-many relationships (e.g. associating `EventVenue` instances with their permissible `EventType` occasions and `Addon` packages) after all parent models exist in the database, ensuring zero relational or foreign-key errors.

---

## 6. Master CMS & Model Control Matrix

| Domain / Section | Primary Model(s) | Admin Management Route | Admin Controlled | Guest Submitted | Code / Static Logic |
|---|---|---|:---:|:---:|:---:|
| **Hotel Site Identity & Theme** | `HotelSettings` | `/admin/settings/` | ✅ | ❌ | Context Processor |
| **Navigation Headers & Footers** | `Navigation` | `/admin/settings/navigation/` | ✅ | ❌ | Recursive Hierarchy |
| **Supported Currencies** | `Currency` | `/admin/settings/currencies/` | ✅ | ❌ | Cookie Switcher |
| **Payment Gateways Config** | `PaymentProcessor` | `/admin/payments/processors/` | ✅ | ❌ | Driver Handlers |
| **Staff Notifications** | `Notification` | `/admin/notifications/` | ✅ | Auto-generated | Bell Badge Context |
| **Homepage Hero Carousel** | `HeroSlide` | `/admin/cms/hero-slides/` | ✅ | ❌ | CSS Animations |
| **Homepage About Preview** | `AboutPreview` | `/admin/cms/about-preview/` | ✅ | ❌ | Video Player |
| **About Page CMS Settings** | `AboutPage` | `/admin/cms/about-page/` | ✅ | ❌ | Layout Structure |
| **Leadership Team** | `TeamMember` | `/admin/cms/team-members/` | ✅ | ❌ | Social Icon Maps |
| **5-Star Facility Highlights** | `AboutFacility` | `/admin/cms/facility-highlights/` | ✅ | ❌ | FontAwesome Icons |
| **Rooms & Suites** | `Room`, `RoomBasePrice` | `/admin/rooms/` | ✅ | ❌ | Multi-Currency Rate |
| **Seasonal Room Discounts** | `RoomSeasonalPrice` | `/admin/rooms/` (Inline) | ✅ | ❌ | Overlap Algorithm |
| **Room Availability Blocks** | `RoomAvailability` | `/admin/rooms/calendar/` | ✅ | Auto-created | Date Conflict Check |
| **Booking & Event Add-on Services**| `Addon`, `AddonPrice` | `/admin/addons/` | ✅ | ❌ | Scoped (`room`/`events`/`both`) |
| **Discount Coupons** | `Coupon`, `CouponMinSpend` | `/admin/coupons/` | ✅ | ❌ | Validation Engine |
| **Dining Venues & Menus** | `DiningVenue`, `DiningVenueImage` | `/admin/dining/` | ✅ | ❌ | Zero-crop Lightbox |
| **Recreation & Spa** | `RecreationActivity` | `/admin/recreation/` | ✅ | ❌ | Category Filter |
| **Conference Venues** | `EventVenue`, `VenueBasePrice` | `/admin/conference/` | ✅ | ❌ | Dynamic Layouts & Occasions |
| **Occasion Categories (Event Types)**| `EventType` | `/admin/conference/?tab=event_types` | ✅ | ❌ | Lucide Icons & Venue M2M |
| **Venue Seating Layouts** | `VenueLayout` | `/admin/conference/` | ✅ | ❌ | Capacity Multipliers |
| **Resort Gallery** | `GalleryItem`, `GalleryCategory`| `/admin/cms/gallery/` | ✅ | ❌ | ImageKit Thumbnails |
| **Branch Offices & Maps** | `HotelBranch` | `/admin/contact/branches/` | ✅ | ❌ | Google Maps Embed |
| **Contact Inquiry Categories** | `InquiryCategory` | `/admin/contact/?tab=inquiries` | ✅ | ❌ | Dynamic Category Pills |
| **Blog & News Articles** | `BlogPost` | `/admin/cms/blogs/` | ✅ | ❌ | Slugify Routing |
| **Nearby Attractions** | `Attraction` | `/admin/cms/attractions/` | ✅ | ❌ | Category Badges |
| **Guest Testimonials** | `Testimonial` | `/admin/cms/testimonials/` | ✅ | ❌ | Source Platform Badges |
| **SEO & Hero Page Banners** | `SEOData` | `/admin/cms/seo/` | ✅ | ❌ | Path Regex Matcher |
| **User & Staff Accounts** | `User` | `/admin/users/` | ✅ | Registration | Django Auth Engine |
| **Room Reservations** | `Booking` | `/admin/bookings/` | Status / Invoice | ✅ | Pricing State Machine |
| **Payment Transactions** | `Payment` | `/admin/payments/` | Verification | ✅ | Gateway API Verification |
| **Dining Reservations** | `DiningReservation` | `/admin/dining/?tab=reservations` | 5 KPIs, Status, Dossier, Clear All | ✅ | Capacity Validation & Direct Alert Link |
| **Conference Inquiries** | `EventInquiry` | `/admin/conference/?tab=inquiries` | 6 KPIs, Dossier, Conflicts, Clear All | ✅ | Conflict Detection & Direct Alert Link |
| **Contact Form Inquiries** | `ContactInquiry` | `/admin/contact/?tab=inquiries` | Status, Email Reply, Clear All | ✅ | Dynamic Category Tabs & Direct Alert Link |
| **Newsletter Subscribers** | `NewsletterSubscriber` | `/admin/contact/subscribers/` | Broadcast Engine | ✅ | Double Opt-in Token |

---

*Hotel Ichchha Platform Architecture & CMS Specification • Version 2.0 • Updated September 2026*
