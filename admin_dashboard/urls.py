from django.urls import path
from .views import auth, home, settings, rooms, bookings, payments, dining, recreation, conference, contact, cms, users

app_name = 'admin_dashboard'

urlpatterns = [
    # Auth
    path('login/', auth.DashboardLoginView.as_view(), name='login'),
    path('logout/', auth.DashboardLogoutView.as_view(), name='logout'),
    
    # Dashboard Home
    path('', home.DashboardHomeView.as_view(), name='home'),
    
    # Bookings
    path('bookings/', bookings.BookingListView.as_view(), name='booking_list'),
    path('bookings/<int:pk>/', bookings.BookingDetailView.as_view(), name='booking_detail'),
    path('bookings/<int:pk>/update-status/', bookings.BookingUpdateStatusView.as_view(), name='booking_update_status'),
    path('bookings/<int:pk>/invoice/', bookings.BookingInvoiceView.as_view(), name='booking_invoice'),
    
    # Rooms
    path('rooms/', rooms.RoomDashboardView.as_view(), name='room_dashboard'),
    path('rooms/add/', rooms.RoomCreateView.as_view(), name='room_create'),
    path('rooms/<int:pk>/edit/', rooms.RoomUpdateView.as_view(), name='room_edit'),
    path('rooms/<int:pk>/delete/', rooms.RoomDeleteView.as_view(), name='room_delete'),
    
    path('rooms/category/add/', rooms.RoomCategoryCreateView.as_view(), name='room_category_create'),
    path('rooms/category/<int:pk>/edit/', rooms.RoomCategoryUpdateView.as_view(), name='room_category_edit'),
    path('rooms/category/<int:pk>/delete/', rooms.RoomCategoryDeleteView.as_view(), name='room_category_delete'),
    
    path('rooms/facility/add/', rooms.RoomFacilityCreateView.as_view(), name='room_facility_create'),
    path('rooms/facility/<int:pk>/edit/', rooms.RoomFacilityUpdateView.as_view(), name='room_facility_edit'),
    path('rooms/facility/<int:pk>/delete/', rooms.RoomFacilityDeleteView.as_view(), name='room_facility_delete'),
    
    path('rooms/price/add/', rooms.RoomPriceCreateView.as_view(), name='room_price_create'),
    path('rooms/price/<int:pk>/edit/', rooms.RoomPriceUpdateView.as_view(), name='room_price_edit'),
    path('rooms/price/<int:pk>/delete/', rooms.RoomPriceDeleteView.as_view(), name='room_price_delete'),
    
    path('rooms/availability/', rooms.RoomAvailabilityCalendarView.as_view(), name='room_availability_calendar'),
    path('rooms/bulk-price/', rooms.RoomBulkPriceUpdateView.as_view(), name='room_bulk_price'),
    path('rooms/bulk-publish/', rooms.RoomBulkPublishView.as_view(), name='room_bulk_publish'),
    
    # Payments
    path('payments/', payments.PaymentListView.as_view(), name='payment_list'),
    path('payments/<int:pk>/', payments.PaymentDetailView.as_view(), name='payment_detail'),
    
    # Dining
    path('dining/', dining.DiningDashboardView.as_view(), name='dining_dashboard'),
    path('dining/venue/add/', dining.DiningVenueCreateView.as_view(), name='dining_venue_create'),
    path('dining/venue/<int:pk>/edit/', dining.DiningVenueUpdateView.as_view(), name='dining_venue_edit'),
    path('dining/venue/<int:pk>/delete/', dining.DiningVenueDeleteView.as_view(), name='dining_venue_delete'),
    path('dining/reservation/<int:pk>/update-status/', dining.DiningReservationUpdateStatusView.as_view(), name='dining_reservation_update_status'),
    
    # Recreation
    path('recreation/', recreation.RecreationDashboardView.as_view(), name='recreation_dashboard'),
    path('recreation/add/', recreation.RecreationCreateView.as_view(), name='recreation_create'),
    path('recreation/<int:pk>/edit/', recreation.RecreationUpdateView.as_view(), name='recreation_edit'),
    path('recreation/<int:pk>/delete/', recreation.RecreationDeleteView.as_view(), name='recreation_delete'),
    
    # Conference / Events
    path('conference/', conference.ConferenceDashboardView.as_view(), name='conference_dashboard'),
    path('conference/venue/add/', conference.EventVenueCreateView.as_view(), name='event_venue_create'),
    path('conference/venue/<int:pk>/edit/', conference.EventVenueUpdateView.as_view(), name='event_venue_edit'),
    path('conference/venue/<int:pk>/delete/', conference.EventVenueDeleteView.as_view(), name='event_venue_delete'),
    path('conference/inquiry/<int:pk>/update-status/', conference.EventInquiryUpdateStatusView.as_view(), name='event_inquiry_update_status'),
    
    # Contact
    path('contact/', contact.ContactDashboardView.as_view(), name='contact_dashboard'),
    path('contact/branch/add/', contact.BranchCreateView.as_view(), name='branch_create'),
    path('contact/branch/<int:pk>/edit/', contact.BranchUpdateView.as_view(), name='branch_edit'),
    path('contact/branch/<int:pk>/delete/', contact.BranchDeleteView.as_view(), name='branch_delete'),
    path('contact/inquiry/<int:pk>/', contact.ContactInquiryDetailView.as_view(), name='contact_inquiry_detail'),
    
    # CMS Content
    path('cms/', cms.CmsDashboardView.as_view(), name='cms_dashboard'),
    path('cms/hero/add/', cms.HeroSlideCreateView.as_view(), name='hero_create'),
    path('cms/hero/<int:pk>/edit/', cms.HeroSlideUpdateView.as_view(), name='hero_edit'),
    path('cms/hero/<int:pk>/delete/', cms.HeroSlideDeleteView.as_view(), name='hero_delete'),
    path('cms/about/', cms.AboutPreviewUpdateView.as_view(), name='about_update'),
    
    path('cms/blog/add/', cms.BlogPostCreateView.as_view(), name='blog_create'),
    path('cms/blog/<int:pk>/edit/', cms.BlogPostUpdateView.as_view(), name='blog_edit'),
    path('cms/blog/<int:pk>/delete/', cms.BlogPostDeleteView.as_view(), name='blog_delete'),
    
    path('cms/testimonial/add/', cms.TestimonialCreateView.as_view(), name='testimonial_create'),
    path('cms/testimonial/<int:pk>/edit/', cms.TestimonialUpdateView.as_view(), name='testimonial_edit'),
    path('cms/testimonial/<int:pk>/delete/', cms.TestimonialDeleteView.as_view(), name='testimonial_delete'),
    
    path('cms/attraction/add/', cms.AttractionCreateView.as_view(), name='attraction_create'),
    path('cms/attraction/<int:pk>/edit/', cms.AttractionUpdateView.as_view(), name='attraction_edit'),
    path('cms/attraction/<int:pk>/delete/', cms.AttractionDeleteView.as_view(), name='attraction_delete'),
    
    path('cms/gallery/category/add/', cms.GalleryCategoryCreateView.as_view(), name='gallery_category_create'),
    path('cms/gallery/category/<int:pk>/edit/', cms.GalleryCategoryUpdateView.as_view(), name='gallery_category_edit'),
    path('cms/gallery/category/<int:pk>/delete/', cms.GalleryCategoryDeleteView.as_view(), name='gallery_category_delete'),
    
    path('cms/gallery/add/', cms.GalleryItemCreateView.as_view(), name='gallery_create'),
    path('cms/gallery/bulk/', cms.GalleryItemBulkUploadView.as_view(), name='gallery_bulk_upload'),
    path('cms/gallery/<int:pk>/delete/', cms.GalleryItemDeleteView.as_view(), name='gallery_delete'),
    
    path('cms/seo/add/', cms.SeoCreateView.as_view(), name='seo_create'),
    path('cms/seo/<int:pk>/edit/', cms.SeoUpdateView.as_view(), name='seo_edit'),
    path('cms/seo/<int:pk>/delete/', cms.SeoDeleteView.as_view(), name='seo_delete'),
    
    # Users
    path('users/', users.UserListView.as_view(), name='user_list'),
    path('users/add/', users.UserCreateView.as_view(), name='user_create'),
    path('users/<int:pk>/edit/', users.UserUpdateView.as_view(), name='user_edit'),
    path('users/<int:pk>/delete/', users.UserDeleteView.as_view(), name='user_delete'),
    
    # Settings Manager
    path('settings/', settings.SettingsDashboardView.as_view(), name='settings_dashboard'),
    path('settings/currency/add/', settings.CurrencyCreateView.as_view(), name='currency_create'),
    path('settings/currency/<int:pk>/edit/', settings.CurrencyUpdateView.as_view(), name='currency_edit'),
    path('settings/currency/<int:pk>/delete/', settings.CurrencyDeleteView.as_view(), name='currency_delete'),
    path('settings/menu/add/', settings.NavigationMenuCreateView.as_view(), name='menu_create'),
    path('settings/menu/<int:pk>/edit/', settings.NavigationMenuUpdateView.as_view(), name='menu_edit'),
    path('settings/menu/<int:pk>/delete/', settings.NavigationMenuDeleteView.as_view(), name='menu_delete'),
]
