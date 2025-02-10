from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', views.home, name='home'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('customer/register/', views.customer_register, name='customer_register'),
    path('store-owner/register/', views.store_owner_register, name='store_owner_register'),
    path('customer/dashboard/', views.customer_dashboard, name='customer_dashboard'),
    path('store-owner/dashboard/', views.store_owner_dashboard, name='store_owner_dashboard'),
    path('restaurant/<int:restaurant_id>/', views.restaurant_menu, name='restaurant_menu'),
    path('add-to-cart/<int:food_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/', views.cart, name='cart'),
    path('checkout/', views.checkout, name='checkout'),
    path('order-confirmation/<int:order_id>/', views.order_confirmation, name='order_confirmation'),

    path('customer/categories/', views.food_categories, name='food_categories'),
    path('customer/restaurant/<int:restaurant_id>/', views.restaurant_menu, name='restaurant_menu'),
    path('customer/order-now/<int:food_id>/', views.order_now, name='order_now'),
    path('customer/cart/add/<int:food_id>/', views.add_to_cart, name='add_to_cart'),
    path('customer/cart/', views.cart, name='cart'),
    path('customer/orders/', views.order_history, name='order_history'),
    path('customer/cart/remove/<int:food_id>/', views.remove_from_cart, name='remove_from_cart'),

]

