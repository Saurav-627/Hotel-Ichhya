from django.db.utils import ProgrammingError, OperationalError
from apps.settings_manager.models.hotel_settings import HotelSettings
from apps.settings_manager.models.navigation import NavigationMenu

def global_settings(request):
    # Safe defaults to prevent migration crashes
    settings_data = {
        'site_name': 'Hotel Ichha',
        'theme': 'luxury',
        'contact_phone': '+977-1-4XXXXXX',
        'contact_email': 'info@hotelichha.com',
        'address': 'Bara, Nepal',
        'about_text': 'A premium 5-star experience of hospitality and luxury.',
        'copyright_text': '&copy; 2026 Hotel Ichha. All Rights Reserved.',
    }
    
    header_menu = []
    footer_quick_links = []
    footer_services = []
    footer_ota_links = []

    try:
        settings_obj = HotelSettings.objects.first()
        if settings_obj:
            settings_data = settings_obj
        else:
            # Create a default settings object if database is ready but empty
            settings_data = HotelSettings(
                site_name='Hotel Ichha',
                theme='luxury',
                contact_phone='+977-1-4XXXXXX',
                contact_email='info@hotelichha.com',
                address='Bara, Nepal',
                about_text='A premium 5-star experience of hospitality and luxury.'
            )

        # Retrieve menus
        menus = NavigationMenu.objects.filter(parent__isnull=True).prefetch_related('children')
        header_menu = menus.filter(position='header')
        footer_quick_links = NavigationMenu.objects.filter(position='footer_links')
        footer_services = NavigationMenu.objects.filter(position='footer_services')
        footer_ota_links = NavigationMenu.objects.filter(position='footer_ota')
        
    except (ProgrammingError, OperationalError):
        # Database tables do not exist yet (running migrations or setup)
        pass

    return {
        'hotel_settings': settings_data,
        'header_menu': header_menu,
        'footer_quick_links': footer_quick_links,
        'footer_services': footer_services,
        'footer_ota_links': footer_ota_links,
    }
