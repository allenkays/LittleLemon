from django.shortcuts import render

# Create your views here.
    
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from django.contrib.auth.models import User, Group
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter
from .models import Category, MenuItem, Cart, Order, OrderItem
from .serializers import (
    CategorySerializer, MenuItemSerializer, CartSerializer,
    OrderSerializer, OrderItemSerializer, UserSerializer
)
from .permissions import IsManager, IsDeliveryCrew, IsCustomer


# Menu Items Views
class MenuItemsListCreateView(generics.ListCreateAPIView):
    queryset = MenuItem.objects.all()
    serializer_class = MenuItemSerializer
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['category', 'price', 'featured']
    ordering_fields = ['price', 'title']
    ordering = ['title']

    def get_permissions(self):
        if self.request.method in ['POST']:
            return [IsManager()]
        return [IsAuthenticated()]

    def create(self, request, *args, **kwargs):
        # Ensure only Managers can create
        if not IsManager().has_permission(request, self):
            return Response({"detail": "Unauthorized"}, status=status.HTTP_403_FORBIDDEN)
        return super().create(request, *args, **kwargs)


class MenuItemDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = MenuItem.objects.all()
    serializer_class = MenuItemSerializer

    def get_permissions(self):
        if self.request.method in ['GET']:
            return [IsAuthenticated()]
        return [IsManager()]

    def update(self, request, *args, **kwargs):
        if not IsManager().has_permission(request, self):
            return Response({"detail": "Unauthorized"}, status=status.HTTP_403_FORBIDDEN)
        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        if not IsManager().has_permission(request, self):
            return Response({"detail": "Unauthorized"}, status=status.HTTP_403_FORBIDDEN)
        return super().destroy(request, *args, **kwargs)


# User Group Management Views
class ManagerGroupView(generics.ListCreateAPIView):
    serializer_class = UserSerializer
    permission_classes = [IsManager]

    def get_queryset(self):
        return User.objects.filter(groups__name='Manager')

    def create(self, request, *args, **kwargs):
        user_id = request.data.get('id')
        user = get_object_or_404(User, id=user_id)
        manager_group = Group.objects.get(name='Manager')
        manager_group.user_set.add(user)
        return Response(status=status.HTTP_201_CREATED)


class ManagerGroupRemoveView(generics.DestroyAPIView):
    permission_classes = [IsManager]

    def delete(self, request, *args, **kwargs):
        user_id = kwargs.get('pk')
        user = get_object_or_404(User, id=user_id)
        manager_group = Group.objects.get(name='Manager')
        if user.groups.filter(name='Manager').exists():
            manager_group.user_set.remove(user)
            return Response(status=status.HTTP_200)
        return Response({"detail": "User not found in Manager group"}, status=status.HTTP_404_NOT_FOUND)


class DeliveryCrewGroupView(generics.ListCreateAPIView):
    serializer_class = UserSerializer
    permission_classes = [IsManager]

    def get_queryset(self):
        return User.objects.filter(groups__name='Delivery crew')

    def create(self, request, *args, **kwargs):
        user_id = request.data.get('id')
        user = get_object_or_404(User, id=user_id)
        delivery_group = Group.objects.get(name='Delivery crew')
        delivery_group.user_set.add(user)
        return Response(status=status.HTTP_201_CREATED)


class DeliveryCrewGroupRemoveView(generics.DestroyAPIView):
    permission_classes = [IsManager]

    def delete(self, request, *args, **kwargs):
        user_id = kwargs.get('pk')
        user = get_object_or_404(User, id=user_id)
        delivery_group = Group.objects.get(name='Delivery crew')
        if user.groups.filter(name='Delivery crew').exists():
            delivery_group.user_set.remove(user)
            return Response(status=status.HTTP_200_OK)
        return Response({"detail": "User not found in Delivery crew group"}, status=status.HTTP_404_NOT_FOUND)


# Cart Management Views
class CartView(generics.ListCreateAPIView, generics.DestroyAPIView):
    serializer_class = CartSerializer
    permission_classes = [IsCustomer]

    def get_queryset(self):
        return Cart.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def delete(self, request, *args, **kwargs):
        Cart.objects.filter(user=request.user).delete()
        return Response(status=status.HTTP_200_OK)


# Order Management Views
class OrdersListCreateView(generics.ListCreateAPIView):
    serializer_class = OrderSerializer
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['status', 'date']
    ordering_fields = ['total', 'date']
    ordering = ['date']

    def get_permissions(self):
        if self.request.method == 'GET' and IsManager().has_permission(self.request, self):
            return [IsManager()]
        return [IsCustomer()]

    def get_queryset(self):
        if IsManager().has_permission(self.request, self):
            return Order.objects.all()
        elif IsDeliveryCrew().has_permission(self.request, self):
            return Order.objects.filter(delivery_crew=self.request.user)
        return Order.objects.filter(user=self.request.user)

    def create(self, request, *args, **kwargs):
        # Only Customers can create orders
        if not IsCustomer().has_permission(request, self):
            return Response({"detail": "Unauthorized"}, status=status.HTTP_403_FORBIDDEN)

        # Get cart items for the user
        cart_items = Cart.objects.filter(user=request.user)
        if not cart_items.exists():
            return Response({"detail": "Cart is empty"}, status=status.HTTP_400_BAD_REQUEST)

        # Calculate total and create order
        total = sum(item.price for item in cart_items)
        order = Order.objects.create(user=request.user, total=total)

        # Create order items from cart items
        for cart_item in cart_items:
            OrderItem.objects.create(
                order=order,
                menuitem=cart_item.menuitem,
                quantity=cart_item.quantity,
                unit_price=cart_item.unit_price,
                price=cart_item.price
            )

        # Clear cart
        cart_items.delete()
        serializer = self.get_serializer(order)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class OrderDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = OrderSerializer
    queryset = Order.objects.all()

    def get_permissions(self):
        if self.request.method == 'GET':
            return [IsAuthenticated()]
        elif self.request.method in ['PUT', 'PATCH']:
            if IsDeliveryCrew().has_permission(self.request, self):
                return [IsDeliveryCrew()]
            return [IsManager()]
        return [IsManager()]

    def get_object(self):
        order = super().get_object()
        if IsCustomer().has_permission(self.request, self) and order.user != self.request.user:
            self.permission_denied(self.request, message="Not your order")
        return order

    def update(self, request, *args, **kwargs):
        order = self.get_object()
        if IsDeliveryCrew().has_permission(request, self):
            # Delivery crew can only update status
            if 'status' not in request.data or len(request.data) > 1:
                return Response({"detail": "Delivery crew can only update status"}, status=status.HTTP_400_BAD_REQUEST)
            serializer = self.get_serializer(order, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)
        elif IsManager().has_permission(request, self):
            # Managers can update delivery_crew and status
            serializer = self.get_serializer(order, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)
        return Response({"detail": "Unauthorized"}, status=status.HTTP_403_FORBIDDEN)

    def destroy(self, request, *args, **kwargs):
        if not IsManager().has_permission(request, self):
            return Response({"detail": "Unauthorized"}, status=status.HTTP_403_FORBIDDEN)
        return super().destroy(request, *args, **kwargs)