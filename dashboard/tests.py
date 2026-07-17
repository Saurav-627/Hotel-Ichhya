from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model

User = get_user_model()

class DashboardAccessTests(TestCase):
    def setUp(self):
        self.client = Client()
        # Create a standard user and a staff user
        self.user = User.objects.create_user(
            username='guestuser', 
            password='guestpassword',
            email='guest@example.com',
            is_staff=False,
            is_superuser=False
        )
        self.staff_user = User.objects.create_user(
            username='staffuser', 
            password='staffpassword',
            email='staff@example.com',
            is_staff=True,
            is_superuser=False
        )

    def test_anonymous_redirect(self):
        """Anonymous user trying to access /admin/ should redirect to login."""
        response = self.client.get(reverse('dashboard:home'))
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse('dashboard:login'), response.url)

    def test_non_staff_denied(self):
        """Non-staff authenticated user should get PermissionDenied (403)."""
        self.client.login(username='guestuser', password='guestpassword')
        response = self.client.get(reverse('dashboard:home'))
        self.assertEqual(response.status_code, 403)

    def test_staff_access_granted(self):
        """Staff/superuser authenticated user should access /admin/ home successfully (200)."""
        self.client.login(username='staffuser', password='staffpassword')
        response = self.client.get(reverse('dashboard:home'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'dashboard/home.html')

    def test_login_page_renders(self):
        """Login page should load successfully (200) for anonymous user."""
        response = self.client.get(reverse('dashboard:login'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'dashboard/login.html')
