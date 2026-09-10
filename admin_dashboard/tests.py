from decimal import Decimal
from django.test import TestCase
from django.contrib.auth import get_user_model

from rooms.models.room import Room
from rooms.models.room_category import RoomCategory
from booking.models.addon import Addon, AddonPrice
from settings_manager.models.currency import Currency
from admin_dashboard.forms import RoomForm, RoomCategoryForm

User = get_user_model()

class AdminDashboardRoomFormTests(TestCase):
    def setUp(self):
        self.usd = Currency.objects.create(iso_code='USD', name='US Dollar', symbol='$', is_published=True)
        self.category = RoomCategory.objects.create(name="Executive Suite", order=1, is_published=True)
        
        self.addon_room = Addon.objects.create(
            name="Free Airport Pickup",
            applies_to="room",
            is_active=True
        )
        self.addon_general = Addon.objects.create(
            name="Welcome Fruit Basket",
            applies_to="both",
            is_active=True
        )
        self.addon_other = Addon.objects.create(
            name="Zipline Fast Pass",
            applies_to="package",
            is_active=True
        )

    def test_room_category_form_excludes_total_rooms(self):
        """RoomCategoryForm should not expose total_rooms."""
        form = RoomCategoryForm()
        self.assertNotIn('total_rooms', form.fields)

    def test_room_form_fields_and_addon_queryset(self):
        """RoomForm should include room_number, total_rooms, allow_custom_addons, and only room/both addons in included_addons queryset."""
        form = RoomForm()
        self.assertIn('room_number', form.fields)
        self.assertIn('total_rooms', form.fields)
        self.assertIn('allow_custom_addons', form.fields)
        self.assertIn('included_addons', form.fields)

        qs = form.fields['included_addons'].queryset
        self.assertIn(self.addon_room, qs)
        self.assertIn(self.addon_general, qs)
        self.assertNotIn(self.addon_other, qs)

    def test_room_form_save_with_room_number_and_inclusions(self):
        """RoomForm successfully saves room_number, total_rooms, and included_addons."""
        form_data = {
            'title': 'Grand Presidential Suite',
            'room_number': 'SUITE-501',
            'slug': 'grand-presidential-suite',
            'category': self.category.id,
            'description': 'Opulent living with butler service',
            'total_rooms': 2,
            'max_adults': 2,
            'max_children': 2,
            'bed_type': 'King Bed',
            'allow_custom_addons': True,
            'is_published': True,
            'included_addons': [self.addon_room.id, self.addon_general.id]
        }
        form = RoomForm(data=form_data)
        self.assertTrue(form.is_valid(), form.errors)
        room = form.save()

        self.assertEqual(room.room_number, 'SUITE-501')
        self.assertEqual(room.total_rooms, 2)
        self.assertEqual(room.included_addons.count(), 2)
