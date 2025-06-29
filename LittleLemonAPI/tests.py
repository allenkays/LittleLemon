from django.test import TestCase
from django.contrib.auth.models import User, Group
from rest_framework.test import APIClient
from rest_framework import status
from .models import Category, MenuItem, Cart, Order, OrderItem
from django.urls import reverse


class LittleLemonAPITests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(
            username='testuser',
            password='testpass'
        )
        cls.manager_group = Group.objects.create(name='Manager')
        cls.delivery_crew_group = Group.objects.create(name='Delivery crew')
        cls.category = Category.objects.create(
            slug='test',
            title='Test Category'
        )
        cls.menu_item = MenuItem.objects.create(
            title='Test Item',
            price=10.99,
            featured=True,
            category=cls.category
        )
        cls.menu_item2 = MenuItem.objects.create(
            title='Test Item 2',
            price=15.99,
            featured=False,
            category=cls.category
        )

    def setUp(self):
        self.client = APIClient()
        self.cart = Cart.objects.create(
            user=self.user,
            menuitem=self.menu_item,
            quantity=2,
            unit_price=10.99,
            price=21.98
        )

    def tearDown(self):
        MenuItem.objects.all().delete()
        Cart.objects.all().delete()
        Order.objects.all().delete()

    # Model Tests
    def test_category_creation(self):
        self.assertEqual(self.category.title, 'Test Category')
        self.assertEqual(self.category.slug, 'test')

    def test_menu_item_creation(self):
        self.assertEqual(self.menu_item.title, 'Test Item')
        self.assertEqual(self.menu_item.price, 10.99)
        self.assertEqual(self.menu_item.category, self.category)

    def test_cart_creation(self):
        self.assertEqual(self.cart.user, self.user)
        self.assertEqual(self.cart.menuitem, self.menu_item)
        self.assertEqual(self.cart.quantity, 2)
        self.assertEqual(self.cart.price, 21.98)

    def test_order_creation(self):
        order = Order.objects.create(
            user=self.user,
            delivery_crew=None,
            status='pending',
            total=21.98,
            date='2025-06-26'
        )
        self.assertEqual(order.user, self.user)
        self.assertEqual(order.status, 'pending')
        self.assertEqual(order.total, 21.98)

    def test_order_item_creation(self):
        order = Order.objects.create(
            user=self.user,
            delivery_crew=None,
            status='pending',
            total=21.98,
            date='2025-06-26'
        )
        order_item = OrderItem.objects.create(
            order=order,
            menuitem=self.menu_item,
            quantity=2,
            unit_price=10.99,
            price=21.98
        )
        self.assertEqual(order_item.order, order)
        self.assertEqual(order_item.menuitem, self.menu_item)
        self.assertEqual(order_item.quantity, 2)
        self.assertEqual(order_item.price, 21.98)

    # View Tests
    def test_cart_view_permissions(self):
        response = self.client.get(reverse('LittleLemonAPI:cart'))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        self.client.force_authenticate(user=self.user)
        response = self.client.get(reverse('LittleLemonAPI:cart'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_orders_view_create(self):
        self.client.force_authenticate(user=self.user)
        data = {
            'status': 'pending',
            'delivery_crew': None,
            'total': 21.98,
            'date': '2025-06-26'
        }
        response = self.client.post(
            reverse('LittleLemonAPI:orders-list'),
            data,
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['status'], 'pending')

    # API Endpoint Tests
    def test_menu_items_endpoint(self):
        # Debug: Check MenuItem count before authenticated request
        print("MenuItem count:", MenuItem.objects.count())
        response = self.client.get(reverse('LittleLemonAPI:menu-items-list'))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        self.client.force_authenticate(user=self.user)
        response = self.client.get(reverse('LittleLemonAPI:menu-items-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)  # Expect 2 items
        self.assertEqual(response.data[0]['title'], 'Test Item')

    def test_cart_endpoint_create(self):
        self.client.force_authenticate(user=self.user)
        data = {
            # Use menu_item2 to avoid unique constraint
            'menuitem_id': self.menu_item2.id,
            'quantity': 3
            # 'unit_price': 10.99,
            # 'price': 32.97
        }
        response = self.client.post(
            reverse('LittleLemonAPI:cart'),
            data,
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['quantity'], 3)
        self.assertEqual(response.data['user'], self.user.id)
        self.assertEqual(
            response.data['unit_price'],
            str(self.menu_item2.price)
        )
        self.assertEqual(
            response.data['price'],
            str(self.menu_item2.price * 3)
        )

    def test_orders_endpoint_list(self):
        # Debug: Check Order count before authenticated request
        print("Order count:", Order.objects.count())
        Order.objects.create(
            user=self.user,
            delivery_crew=None,
            status='pending',
            total=21.98,
            date='2025-06-26'
        )
        self.client.force_authenticate(user=self.user)
        response = self.client.get(reverse('LittleLemonAPI:orders-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['status'], 'pending')
