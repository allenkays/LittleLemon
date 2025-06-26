from django.test import TestCase
from django.contrib.auth.models import User
from .models import Category, MenuItem, Cart


class LittleLemonAPITests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser', password='testpass'
        )
        self.category = Category.objects.create(
            slug='test',
            title='Test Category'
        )
        self.menu_item = MenuItem.objects.create(
            title='Test Item',
            price=10.99,
            featured=True,
            category=self.category
        )

    def test_category_creation(self):
        self.assertEqual(
            self.category.title,
            'Test Category'
        )
        self.assertEqual(self.category.slug, 'test')

    def test_menu_item_creation(self):
        self.assertEqual(self.menu_item.title, 'Test Item')
        self.assertEqual(self.menu_item.price, 10.99)

    def test_cart_creation(self):
        cart = Cart.objects.create(
            user=self.user,
            menuitem=self.menu_item,
            quantity=2,
            unit_price=10.99,
            price=21.98
        )
        self.assertEqual(cart.quantity, 2)
        self.assertEqual(cart.price, 21.98)
