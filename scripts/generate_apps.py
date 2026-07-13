import os

apps = [
    "core", "accounts", "homepage", "about", "rooms", "dining", "recreation", 
    "gallery", "testimonials", "nearby_places", "conference", "booking", 
    "payments", "contact", "blogs", "seo", "settings_manager", "notifications", 
    "analytics", "admin_dashboard", "api"
]

base_dir = "apps"

os.makedirs(base_dir, exist_ok=True)
with open(os.path.join(base_dir, "__init__.py"), "w") as f:
    f.write("")

for app in apps:
    app_dir = os.path.join(base_dir, app)
    os.makedirs(app_dir, exist_ok=True)
    
    # Create __init__.py for app
    with open(os.path.join(app_dir, "__init__.py"), "w") as f:
        f.write("")
        
    # Create apps.py
    class_name = "".join([part.capitalize() for part in app.split("_")])
    apps_content = f"""from django.apps import AppConfig

class {class_name}Config(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.{app}'
    label = '{app}'
"""
    with open(os.path.join(app_dir, "apps.py"), "w") as f:
        f.write(apps_content)

    # Subdirectories
    subdirs = [
        "admin", "models", "views", "services", "forms", "serializers", 
        "managers", "selectors", "urls", "tests", "utils", "permissions", "signals"
    ]
    
    for subdir in subdirs:
        subdir_path = os.path.join(app_dir, subdir)
        os.makedirs(subdir_path, exist_ok=True)
        with open(os.path.join(subdir_path, "__init__.py"), "w") as f:
            f.write("")
            
    # Specialized files for views
    views_path = os.path.join(app_dir, "views")
    view_files = ["public.py", "admin.py", "ajax.py", "booking.py", "api.py"]
    for vf in view_files:
        with open(os.path.join(views_path, vf), "w") as f:
            f.write(f"# Views for {app} - {vf.replace('.py', '')}\n")
            
    # Templates and static structures
    templates_path = os.path.join(app_dir, "templates", app)
    os.makedirs(templates_path, exist_ok=True)
    with open(os.path.join(templates_path, ".gitkeep"), "w") as f:
        f.write("")
        
    static_path = os.path.join(app_dir, "static", app)
    os.makedirs(static_path, exist_ok=True)
    with open(os.path.join(static_path, ".gitkeep"), "w") as f:
        f.write("")

print("Successfully generated all apps and structures.")
