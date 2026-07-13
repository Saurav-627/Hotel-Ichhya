from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # Admin Interface
    path('admin/', admin.site.urls),
    
    # Modular Apps
    path('', include('apps.homepage.urls', namespace='homepage')),
    path('rooms/', include('apps.rooms.urls', namespace='rooms')),
    path('dining/', include('apps.dining.urls', namespace='dining')),
    path('recreation/', include('apps.recreation.urls', namespace='recreation')),
    path('gallery/', include('apps.gallery.urls', namespace='gallery')),
    path('booking/', include('apps.booking.urls', namespace='booking')),
    path('payments/', include('apps.payments.urls', namespace='payments')),
    path('contact/', include('apps.contact.urls', namespace='contact')),
    path('blogs/', include('apps.blogs.urls', namespace='blogs')),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
