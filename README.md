# 🏨 Hotel Ichchha Platform

A modern, high-performance Django-based hospitality and booking management platform designed for luxury 5-star hotels and resorts. Built with a modular domain-driven architecture, bespoke administrative dashboard, multi-currency pricing, dynamic white-label branding, automated email dispatch, and integrated payment gateways.

---

## 📑 Table of Contents

- [Overview](#-overview)
- [Key Features](#-key-features)
- [Architecture & Tech Stack](#-architecture--tech-stack)
- [Project Directory Structure](#-project-directory-structure)
- [Modular Apps Overview](#-modular-apps-overview)
- [Quick Start & Installation](#-quick-start--installation)
  - [Option A: One-Step Setup with Makefile (Recommended)](#option-a-one-step-setup-with-makefile-recommended)
  - [Option B: Manual Setup with `uv`](#option-b-manual-setup-with-uv)
- [Database Seeding & YAML Records](#-database-seeding--yaml-records)
- [Database Backup & Automated Rotation](#-database-backup--automated-rotation)
- [Docker & Containerized Deployment](#-docker--containerized-deployment)
- [Custom Administrative Dashboard](#-custom-administrative-dashboard)
- [Dynamic Page Banners (SEO Admin)](#-dynamic-page-banners-seo-admin)
- [Payment Gateway Integration](#-payment-gateway-integration)
- [Email & Notification Services](#-email--notification-services)
- [Environment Configuration Reference](#-environment-configuration-reference)

---

## 🌟 Overview

**Hotel Ichchha** is Nepal's first 5-star luxury hotel in Simara, Bara. This platform provides an end-to-end digital ecosystem for guest reservations, dining bookings, conference inquiries, dynamic content management (CMS), multi-currency transactions, and staff administration.

Every aspect of the platform—from site identity, navigation menus, and room availability calendars to leadership team profiles, seasonal discounts, and SEO banners—can be managed dynamically through the custom admin portal without modifying code.

---

## 🚀 Key Features

### 🏢 Full White-Label & Dynamic Site Identity
* **Centralized Branding**: Configure site name, light/dark logos, admin panel logo, browser favicon (`.ico`, `.png`, `.svg`), admin browser tab title, admin sidebar brand label, footer story, contact details, and social media links directly from the Admin CMS (`Settings Manager -> Hotel Global Settings`).
* **Dynamic Context Injection**: Global context processor (`core.context_processors.global_settings`) injects site identity and active navigation menus into all templates with fallback defaults.

### 💱 Server-Side Multi-Currency Engine
* **Cookie-Driven Persistence**: Guests select their preferred currency (USD, NPR, EUR, GBP, etc.) via header dropdown or mobile menu; selection persists seamlessly across pages.
* **Non-Duplicated Multi-Currency Pricing**:
  - `RoomBasePrice`: Standard nightly base and discounted rates per currency.
  - `RoomSeasonalPrice`: Promotional overrides with optional currency restriction or wildcard fallback.
  - `VenueBasePrice`: Starting rental rates for event halls and conference venues per currency.
  - `AddonPrice`: Add-on service pricing per currency.
  - `CouponMinSpend`: Minimum spend thresholds per currency for coupon redemption.
* **Multi-Currency Analytics**: Administrative dashboard automatically categorizes daily and monthly revenues into isolated currency buckets (e.g., NPR and USD).

### 🏨 Rooms & Booking Engine
* **Interactive Datepicker & Real-Time Availability**: Powered by Air Datepicker with date restrictions, blocking reserved dates, and checking overlapping bookings before checkout.
* **Seasonal Price Overlap Algorithm**: High-fidelity date calculation ensures guests receive promotional rates for each individual qualifying night of their stay.
* **Room Duplication Tool**: One-click action in admin to duplicate existing rooms with full facility and image associations for rapid cataloging.
* **Standardized Invoicing Engine**: Print-ready, pixel-perfect invoice layout (`invoice.html`) accessible to both guests and administrators with itemized night breakdowns, tax calculations (13% VAT), discounts, and payment status badges.

### 👑 Dynamic About Page & Leadership CMS
* **Dedicated CMS App (`about`)**: Complete management of the About page including hero banners, hotel heritage narrative, 6 quick feature badges, statistics counters, CEO narrative (Rewanta Prasad Dhaubhadel / Rebu with Swiss Hotel Management School credentials), mission/vision/values, and bottom CTA banner.
* **Board & Executive Leadership Directory (`TeamMember`)**: Manage leadership team members with bio, portrait image, ordering sequence, and LinkedIn/social links.
* **5-Star Facility Highlights (`AboutFacility`)**: Manage key hotel amenities and features with FontAwesome icons and display ordering.

### 🖼️ Enhanced Media & Zero-Crop Lightbox Sliders
* **Multi-Image Galleries**: Dedicated gallery models for Conference (`EventVenueImage`), Dining (`DiningVenueImage`), Recreation (`RecreationActivityImage`), and Rooms (`RoomImage`).
* **Display Image Fallback**: Smart `display_image_url` property that automatically resolves images from primary flags, gallery records, or default fallbacks to prevent broken image cards.
* **Interactive Lightbox Sliders**: Zero-crop image carousels with full-screen zoom lightbox powered by Alpine.js on all detail pages.
* **Thumbnail Processing**: Automated thumbnail generation via `django-imagekit` for high-speed page loads.

### 🎁 Coupons, Add-ons & Marketing
* **Flexible Coupon System**: Percentage (%) or fixed amount discounts with minimum spend per currency, validity windows, maximum usage limits, and product applicability (rooms vs services).
* **Booking Add-ons (`Addon`)**: Manage airport transfers, extra beds, spa packages, or candlelight dinners charged per night, per guest, or per booking.
* **Double Opt-In Newsletter**: Secure newsletter subscription with email verification links and automated welcome emails.
* **Bulk Email Broadcast**: Admin tool to broadcast HTML promotional announcements to all verified subscribers with logging and error reporting.

### 💳 Comprehensive Payment Processing
* **Configurable Payment Processors (`PaymentProcessor`)**: Enable/disable payment gateways dynamically from Admin Settings Manager with currency associations.
* **Supported Gateways**:
  - **eSewa**: ePay v2 integration with secure HMAC-SHA256 signature verification.
  - **Khalti**: ePayment v2 API integration with verification endpoints.
  - **Stripe**: Hosted Checkout session creation and webhook listener.
  - **Offline Options**: Bank Transfer (with custom instructions) and Pay at Hotel / Cash on Arrival.

### 🔔 Staff Notifications & Contact Management
* **Real-Time Admin Notifications (`AdminNotification`)**: System-wide notifications on new bookings, successful payments, and contact inquiries with unread badges in the admin navbar.
* **Inquiry Reply Modal**: View guest inquiries by category (Room, Dining, Event, General) and reply directly via email from the admin dashboard using integrated SMTP.

---

## 🛠️ Architecture & Tech Stack

| Layer | Technologies |
|---|---|
| **Backend Framework** | Django 6.x, Python 3.14 |
| **Package Manager** | `uv` (Ultra-fast Python package and project manager) |
| **Database** | SQLite (Default development) / PostgreSQL 15 (Docker & Production) |
| **Caching & Broker** | Redis 7, Django LocMemCache / RedisCache |
| **Task Queue** | Celery (Asynchronous background processing) |
| **Frontend Styling** | TailwindCSS (v3 / Custom compiled), Vanilla CSS |
| **Frontend Interactivity** | Alpine.js, Air Datepicker, Chart.js, FontAwesome 6 |
| **Image Processing** | `django-imagekit`, Pillow |
| **Static & Media Files** | WhiteNoise (Compressed Manifest Storage), Django Staticfiles |
| **Email Service** | Django SMTP Backend, Mailpit (Local development container) |
| **Deployment & Containers** | Docker, Docker Compose, Gunicorn |

---

## 📁 Project Directory Structure

```text
Hotel-Ichha/
├── about/                  # About page CMS, leadership team & facility highlights
├── accounts/               # Custom User model (roles, avatars, profile data)
├── admin_dashboard/        # Bespoke Tailwind-based administrative portal & CMS
├── blogs/                  # News, press releases, and articles
├── booking/                # Reservation engine, checkout, coupons, addons
├── conference/             # Event halls, multi-currency pricing, venue galleries, inquiries
├── config/                 # Project settings, ASGI/WSGI, root URL routing, Celery config
├── contact/                # Branch offices, contact inquiries, newsletter subscribers
├── core/                   # Base models, seed_data command, records (YAML), email service, utils
│   ├── management/commands/# seed_data.py, db_backup.py
│   ├── records/            # 18 modular YAML data files for initial/demo content
│   └── services/           # email_service.py (invoices, verification, broadcasts)
├── dining/                 # Restaurants, bars, PDF menus, multi-image galleries, reservations
├── gallery/                # Resort photo & video gallery categorized by tabs, drone tags
├── homepage/               # Hero slides, about preview, search widget, section previews
├── media/                  # User & admin uploaded assets (images, PDFs, videos)
├── nearby_places/          # Tourist attractions, national parks, airports, maps
├── payments/               # Payment gateways (eSewa, Khalti, Stripe), processors, invoices
├── recreation/             # Spa, pool, gym, casino, multi-image galleries
├── rooms/                  # Room catalog, categories, multi-currency base/seasonal pricing, facilities
├── scripts/                # Utility scripts (backup.sh cron script)
├── seo/                    # SEO metadata, OpenGraph, JSON-LD, dynamic page hero banners
├── settings_manager/       # Hotel global settings, currencies, navigation menus, db backup
├── static/                 # Static assets (CSS, JS, fonts, brand images)
├── staticfiles/            # Collected static assets for WhiteNoise production serving
├── templates/              # Base templates, navigation headers, footers, email HTML layouts
├── Dockerfile              # Container definition for web and Celery workers
├── docker-compose.yml      # Multi-container stack (PostgreSQL, Redis, Web, Celery)
├── Makefile                # Command runner for common setup, build, and test tasks
├── pyproject.toml          # Project metadata and dependencies managed by uv
└── uv.lock                 # Pinned dependency lockfile
```

---

## 🧩 Modular Apps Overview

| App Name | Primary Models | Key Responsibilities |
|---|---|---|
| `about` | `AboutPage`, `TeamMember`, `AboutFacility` | Singleton About CMS, leadership directory, facility highlights, video showcase |
| `accounts` | `User` | Custom user accounts, guest profiles, staff role management |
| `admin_dashboard`| `Notification` | Bespoke admin dashboard, analytics, charts, CMS views, invoice generator |
| `blogs` | `BlogPost` | Articles, news, editorial categories, author attribution |
| `booking` | `Booking`, `Addon`, `AddonPrice`, `BookingAddon`, `Coupon`, `CouponMinSpend` | Reservation pipeline, dynamic pricing, promo validation, addons |
| `conference` | `EventVenue`, `VenueBasePrice`, `EventVenueImage`, `EventInquiry` | Event spaces, multi-currency rental rates, gallery sliders, inquiries |
| `contact` | `HotelBranch`, `ContactInquiry`, `NewsletterSubscriber` | Branch locations, contact submissions, newsletter verification & broadcasts |
| `core` | Abstract Base Models, Mixins | Base models, `seed_data` pipeline, YAML records, `email_service.py` |
| `dining` | `DiningVenue`, `DiningVenueImage`, `DiningReservation` | Restaurants, bars, chef profiles, PDF menus, table reservations |
| `gallery` | `GalleryCategory`, `GalleryItem` | Photo/video gallery, virtual tours, drone badges, imagekit thumbnails |
| `homepage` | `HeroSlide`, `AboutPreview` | Homepage hero carousel, animated banners, about preview video |
| `nearby_places` | `Attraction` | Local tourist attractions, distances, driving times, Google Maps links |
| `payments` | `Payment`, `PaymentProcessor`, `PaymentProcessorCurrency` | Payment transactions, gateway configurations (eSewa, Khalti, Stripe), invoices |
| `recreation` | `RecreationActivity`, `RecreationActivityImage` | Wellness, spa, pools, gym, operating hours, activity galleries |
| `rooms` | `Room`, `RoomCategory`, `RoomBasePrice`, `RoomSeasonalPrice`, `RoomImage`, `RoomFacility`, `RoomPolicy`, `RoomAvailability` | Room inventory, multi-currency rates, seasonal overrides, calendar blocks |
| `seo` | `SEOData` | Page-specific meta titles, OpenGraph, JSON-LD, dynamic hero banners |
| `settings_manager`| `HotelSettings`, `Currency`, `Navigation` | Singleton hotel branding, currency switcher, header/footer navigation |
| `testimonials`| `Testimonial` | Guest reviews, star ratings, verified source tags (Google, TripAdvisor, Agoda) |

---

## ⚙️ Quick Start & Installation

### Option A: One-Step Setup with Makefile (Recommended)

If you have `make` installed on your machine:

```bash
# 1. Complete workspace setup (syncs dependencies with uv, runs migrations, seeds all YAML records)
make setup

# 2. (Optional) Create an administrative superuser
make superuser

# 3. Start local development server (runs on 0.0.0.0:8000)
make run
```

Other useful `make` commands:
```bash
make test          # Run test suite
make build-css     # Build minified production Tailwind CSS
make collectstatic # Collect static files for production
make backup        # Perform automated database backup
make mailpit       # Start local Mailpit test email server in Docker (Web UI: http://localhost:8025)
make clean         # Clean __pycache__ and bytecode files
```

---

### Option B: Manual Setup with `uv`

If `make` is not available, execute the following commands using `uv`:

```bash
# 1. Clone repository and navigate to root directory
cd Hotel-Ichha

# 2. Sync virtual environment and install all dependencies
uv sync

# 3. Apply database migrations
uv run python manage.py migrate

# 4. Seed all modular YAML records into the database
uv run python manage.py seed_data

# 5. Create administrative superuser account
uv run python manage.py createsuperuser

# 6. Start development server
uv run python manage.py runserver 0.0.0.0:8000
```

Access the application:
* **Public Guest Website**: `http://127.0.0.1:8000/`
* **Custom Admin Portal**: `http://127.0.0.1:8000/admin/`
* **Native Django Admin**: `http://127.0.0.1:8000/django-admin/`

---

## 💾 Database Seeding & YAML Records

The database seeding mechanism uses a modular, robust command located at `core/management/commands/seed_data.py`. It imports records in strict dependency order from 18 structured YAML files located in `core/records/`:

```text
core/records/
├── 01_hotel_settings.yaml       # Site name, logos, contacts, theme, social links
├── 02_currencies.yaml           # USD, NPR, EUR, GBP definitions
├── 03_navigation_menus.yaml     # Header & footer menus, positioning, hierarchy
├── 04_about_preview.yaml        # Homepage about preview section & counters
├── 05_hero_slides.yaml          # Homepage hero carousel slides & animations
├── 06_room_categories.yaml      # Room categories (Suites, Deluxe, Executive)
├── 07_room_facilities.yaml      # Room amenities & FontAwesome icons
├── 08_rooms.yaml                # Rooms, multi-currency base/seasonal prices, galleries
├── 09_dining_venues.yaml        # Dining outlets, timings, signature dishes
├── 10_recreation_activities.yaml# Spa, pool, gym, casino activities
├── 11_event_venues.yaml         # Banquet halls, multi-currency rates, layouts
├── 12_attractions.yaml          # Nearby attractions, distances, driving times
├── 13_testimonials.yaml         # Guest reviews, ratings, source platforms
├── 14_seo_banners.yaml          # SEO metadata and dynamic hero page banners
├── 15_coupons.yaml              # Promotional discount coupons & min spend per currency
├── 16_branches.yaml             # Branch offices & Google Maps iframe embeds
├── 17_payment_processors.yaml   # eSewa, Khalti, Stripe, Bank Transfer processors
└── 18_about_page.yaml           # About page CMS, CEO message, team members, facilities
```

To re-run the full seeding process at any time:
```bash
uv run python manage.py seed_data
# or
make seed-all
```

---

## 💾 Database Backup & Automated Rotation

The platform includes an automated database backup command supporting both **SQLite** and **PostgreSQL** databases (`settings_manager/management/commands/db_backup.py`). Backups are saved to the `backups/` directory with automatic retention pruning.

### Manual Backup
```bash
# Create a backup and retain only the 10 most recent backups
uv run python manage.py db_backup --keep 10
# or
make backup
```

### Cronjob Automation
A shell script is provided at `scripts/backup.sh`. To schedule daily backups at 2:00 AM:
```bash
crontab -e
```
Add the cron entry (adjust path to your project location):
```text
0 2 * * * /home/user/Workflow/Hotel\ Platform/Hotel-Ichha/scripts/backup.sh
```

---

## 🐳 Docker & Containerized Deployment

A production-ready multi-container deployment stack is included via `Dockerfile` and `docker-compose.yml`.

### Services in `docker-compose.yml`:
1. `db`: PostgreSQL 15 database container with persistent volume storage.
2. `redis`: Redis 7 cache and Celery broker.
3. `web`: Django web application served via Gunicorn (3 workers).
4. `celery_worker`: Background worker processing async tasks and emails.

### Running Docker Stack:
```bash
# Start all services in background
make docker-up
# or
docker compose up -d

# View live container logs
make docker-logs

# Stop services
make docker-down

# Clean volumes and containers
make docker-clean
```

---

## 🖥️ Custom Administrative Dashboard

The administrative dashboard (`/admin/`) is completely custom-built with **TailwindCSS**, **Alpine.js**, and **Chart.js** (no bloated third-party admin wrappers).

### Key Admin Modules:
* **Analytics Overview (`/admin/`)**:
  - Live occupancy metrics, today's check-ins and check-outs.
  - Multi-currency daily and monthly revenue cards (e.g., NPR & USD).
  - 7-day revenue trend chart grouped by currency.
  - Real-time activity feeds and quick-action links.
* **Booking Management (`/admin/bookings/`)**:
  - Filter bookings by status (Draft, Pending, Confirmed, Checked In, Checked Out, Cancelled).
  - Status updater with automatic notification triggers.
  - View and print official HTML invoices.
* **Room Management (`/admin/rooms/`)**:
  - Room CRUD with multi-currency base rates and seasonal date override inlines.
  - Room availability calendar with interactive date-blocking.
  - Room duplication action to clone existing rooms with all facilities and settings.
* **CMS Management (`/admin/cms/`)**:
  - Direct control over Hero Slides, About Preview, About Page CMS, Team Members, Facility Highlights, Dining Venues, Recreation Activities, Gallery Items, Testimonials, Attractions, and Blog Posts.
* **Marketing & Communications**:
  - `/admin/coupons/`: Discount coupon manager with currency minimum spend rules.
  - `/admin/addons/`: Room and service add-ons manager.
  - `/admin/contact/inquiries/`: View inquiries and reply directly via email modal.
  - `/admin/contact/broadcast/`: Send bulk promotional emails to verified subscribers.
* **Settings & Gateways (`/admin/settings/`)**:
  - Global hotel identity (logos, favicons, contacts, social links, theme).
  - Currency switcher manager.
  - Dynamic navigation menu manager.
  - Payment processors manager (`/admin/payments/processors/`).

---

## 🖼️ Dynamic Page Banners (SEO Admin)

Every public listing page features a **dynamic hero banner** (subtitle, title, description, and background image) that can be edited in real time from the Admin Portal (`SEO -> SEO Page Data`).

### Configurable Routes:

| Page | URL Path (exact) | Default Fallback Title |
|---|---|---|
| Rooms & Suites | `/rooms/` | Rooms & Accommodation |
| Gastronomy & Dining | `/dining/` | Gastronomy & Dining |
| Recreation & Wellness | `/recreation/` | Recreation & Wellness |
| Resort Gallery | `/gallery/` | Resort Photo Gallery |
| Conferences & Venues | `/conference/` | Conferences & Venues |
| Concierge & Contact | `/contact/` | Concierge & Contact |
| Stories & Blog | `/blogs/` | Stories & News |
| About Hotel Ichchha | `/about/` | About Hotel Ichchha |

> **Context Processor**: `seo.context_processors.seo_meta` automatically matches the current request path against `SEOData` records, injecting `seo_raw` and meta tags into the template.

---

## 💳 Payment Gateway Integration

### 1. eSewa (ePay v2)
* **Configuration**: `ESEWA_CLIENT_ID`, `ESEWA_CLIENT_SECRET`, `ESEWA_DEMO=True/False`.
* **Security**: Requests and callbacks verify HMAC-SHA256 signatures over `total_amount,transaction_uuid,product_code`.
* **Verification**: Server-side verification via eSewa transaction verification endpoint.

### 2. Khalti (ePayment v2)
* **Configuration**: `KHALTI_CLIENT_ID`, `KHALTI_CLIENT_SECRET`, `KHALTI_DEMO=True/False`.
* **Flow**: Initiates payment via Khalti ePayment API, redirects guest to Khalti payment portal, and verifies response on callback.

### 3. Stripe Checkout
* **Configuration**: `STRIPE_PUBLIC_KEY`, `STRIPE_SECRET_KEY`, `STRIPE_WEBHOOK_SECRET`.
* **Flow**: Generates Stripe Checkout sessions and processes webhook events for completed sessions.

### 4. Offline / Pay Later
* **Options**: Bank Transfer (custom bank account details shown on invoice) and Cash on Arrival.

---

## 📧 Email & Notification Services

The platform features an email service (`core/services/email_service.py`) supporting both production SMTP and local testing via Mailpit:

1. **Booking Invoices**: Dispatches branded HTML invoice emails (`templates/emails/booking_invoice_email.html`) upon payment confirmation with direct link to online printable receipt.
2. **Newsletter Verification**: Double opt-in confirmation emails (`templates/emails/newsletter_verification_email.html`) with secure verification tokens.
3. **Newsletter Welcome**: Automated welcome greeting (`templates/emails/newsletter_welcome_email.html`) sent upon successful verification.
4. **Subscriber Broadcasts**: Bulk broadcast engine (`templates/emails/newsletter_broadcast_email.html`) sent from `/admin/contact/broadcast/`.
5. **Inquiry Replies**: Direct email replies sent from `/admin/contact/inquiries/<id>/`.

---

## 🔒 Environment Configuration Reference

The application reads configuration from environment variables or a `.env` file in the root directory:

| Variable | Type | Default | Description |
|---|---|---|---|
| `DEBUG` | Boolean | `True` | Django debug mode (set to `False` in production) |
| `SECRET_KEY` | String | *Insecure fallback* | Unique cryptographic secret key |
| `ALLOWED_HOSTS` | List | `*` | Comma-separated list of allowed host header domains |
| `DATABASE_URL` | String | `sqlite:///db.sqlite3` | Database URI (`postgres://user:pass@host:5432/dbname`) |
| `REDIS_URL` | String | `""` | Redis URI (`redis://localhost:6379/0`) |
| `CELERY_BROKER_URL`| String | `redis://localhost:6379/1` | Celery broker URL |
| `SITE_DOMAIN` | String | `127.0.0.1:8000` | Domain name used in absolute email URLs |
| `EMAIL_BACKEND` | String | `django.core.mail.backends.smtp.EmailBackend` | Email backend |
| `EMAIL_HOST` | String | `""` | SMTP Host (e.g., `smtp.sendgrid.net` or `localhost` for Mailpit) |
| `EMAIL_PORT` | Integer | `1025` | SMTP Port (`1025` for Mailpit, `587` for TLS) |
| `EMAIL_HOST_USER` | String | `""` | SMTP Username |
| `EMAIL_HOST_PASSWORD`| String | `""` | SMTP Password / API Key |
| `EMAIL_USE_TLS` | Boolean | `False` | Enable TLS encryption |
| `DEFAULT_FROM_EMAIL`| String | `Hotel Ichchha <noreply@hotelichchha.com>` | Default sender address |
| `ESEWA_CLIENT_ID` | String | `EPAYTEST` | eSewa merchant/product code |
| `ESEWA_CLIENT_SECRET`| String | *Test secret* | eSewa secret key for HMAC signature |
| `ESEWA_DEMO` | Boolean | `True` | Toggle eSewa sandbox mode |
| `KHALTI_CLIENT_SECRET`| String | *Test secret* | Khalti secret live/test key |
| `KHALTI_DEMO` | Boolean | `True` | Toggle Khalti sandbox mode |

---

*Hotel Ichchha Hospitality Management Platform • Documentation Updated August 2026*
