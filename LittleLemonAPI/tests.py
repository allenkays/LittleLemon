from django.test import TestCase
from .models import Category, MenuItem


# Create your tests here.
class MenuItemTests(TestCase):
    def setUp(self):
        self.category = Category.objects.create(slug="test", title="Test Category")
        self.menu_item = MenuItem.objects.create(
            title="Test Item", price=10.99, featured=True, category=self.category
        )

    def test_menu_item_creation(self):
        self.assertEqual(self.menu_item.title, "Test Item")
        self.assertEqual(self.menu_item.price, 10.99)