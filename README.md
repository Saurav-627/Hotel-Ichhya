# Hotel Ichha Platform

A premium, high-performance Django-based hospitality and booking management platform designed for luxury hotels and resorts.

---

## 🚀 Key Features

*   **Server-Side Currency Persistence**: Persistent cookie-driven currency switcher (desktop dropdown, mobile sidebar native select) that filters room listings and payment flows dynamically.
*   **Dynamic Theme System**: Dynamic theme-aware layout styling supporting Light, Dark, Luxury Gold, and Festival modes without client-side render flickering.
*   **Django Unfold Admin CMS**: Custom-branded administrative dashboard for managing rooms, facilities, nearby attractions, navigation menus, and global configurations.
*   **Responsive Booking Engine**: Full booking initiation flow complete with a dynamic reservation calculator, checkout page, and gateway integrations (Stripe, eSewa, Khalti).
*   **Optimized Performance**: Packaged with `uv` for lightning-fast Python dependency management and compilation.

---

## 🛠️ Tech Stack

*   **Backend**: Django 6, Python 3.14
*   **Frontend**: TailwindCSS, Alpine.js, FontAwesome Icons
*   **Database**: SQLite (default local) / PostgreSQL support
*   **Package Manager**: `uv`

---

## ⚙️ Quick Start & Installation

### 1. Clone & Prepare Environment
Ensure you have Python and `uv` installed. Run:
```bash
# Sync virtual environment and install dependencies
uv sync
```

### 2. Database Migrations
Run the migrations to create the database schema:
```bash
uv run python manage.py migrate
```

### 3. Load Initial Configuration Data
Load standard default currencies, global settings, and header menu layouts from the YAML file:
```bash
uv run python manage.py import_initial_data
```

### 4. Create Administrative User
Create a superuser to access the Unfold admin dashboard:
```bash
uv run python manage.py createsuperuser
```

### 5. Start Development Server
Run the local server:
```bash
uv run python manage.py runserver
```
Visit the homepage at `http://127.0.0.1:8000/` and the admin portal at `http://127.0.0.1:8000/admin/`.

---

## 📁 Repository Structure & Data Loading

*   `initial_data.yaml`: Stores essential currencies (USD, NPR, EUR, GBP), header navigation paths, and initial branding metadata.
*   `settings_manager/`: Contains models for Currency, Navigation menus, and Global Hotel Settings, along with the command line import utilities.
*   `templates/base.html`: Core base template containing dynamic navigation headers, mobile responsive menus, and general assets.

---

## 💾 Database Backup & Cronjob Setup

The project includes an automatic database backup command supporting both SQLite and PostgreSQL. It automatically creates backup files under `backups/` and keeps only the most recent backups to prevent the disk from filling up.

### Manual Execution
To create a backup and keep the last 10 backups:
```bash
uv run python manage.py db_backup --keep 10
```

### Automation via Cronjob
A helper shell script `scripts/backup.sh` is provided in the repository root. To schedule backups daily at 2:00 AM:

1. Open your system's crontab editor:
   ```bash
   crontab -e
   ```
2. Add the following entry (updating the directory path to your project's absolute path):
   ```text
   0 2 * * * /home/user/Workflow/Hotel\ Platform/Hotel-Ichha/scripts/backup.sh
   ```

