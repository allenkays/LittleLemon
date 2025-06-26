from django.urls import path
from . import views

app_name = 'LittleLemonAPI'

urlpatterns = [
    path('', views.HomeView.as_view(), name='home'),
    # Menu Items
    path(
        'menu-items/',
        views.MenuItemsListCreateView.as_view(),
        name='menu-items-list'
    ),
    path(
        'menu-items/<int:pk>/',
        views.MenuItemDetailView.as_view(),
        name='menu-item-detail'
    ),

    # User Group Management
    path(
        'groups/manager/users/',
        views.ManagerGroupView.as_view(),
        name='manager-group'
    ),
    path(
        'groups/manager/users/<int:pk>/',
        views.ManagerGroupRemoveView.as_view(),
        name='manager-group-remove'),
    path(
        'groups/delivery-crew/users/',
        views.DeliveryCrewGroupView.as_view(),
        name='delivery-crew-group'
    ),
    path(
        'groups/delivery-crew/users/<int:pk>/',
        views.DeliveryCrewGroupRemoveView.as_view(),
        name='delivery-crew-group-remove'
    ),

    # Cart
    path('cart/menu-items/', views.CartView.as_view(), name='cart'),

    # Orders
    path('orders/', views.OrdersListCreateView.as_view(), name='orders-list'),
    path(
        'orders/<int:pk>/',
        views.OrderDetailView.as_view(),
        name='order-detail'
    ),
]
