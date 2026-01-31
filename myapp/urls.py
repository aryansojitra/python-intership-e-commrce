from django.contrib import admin
from django.urls import path
from .views import *
urlpatterns = [
    path('', register, name='register'),
    path('login/', login, name='login'),
    path('home/', home, name='home'),
    path('products/', products, name='products'),
    path('add_to_cart/<int:product_id>/', add_to_cart, name='add_to_cart'),
    path('cart/', cart, name='cart'),
    path('increase_qty/<int:cart_id>/', increase_qty, name='increase_qty'),
    path('decrease_qty/<int:cart_id>/', decrease_qty, name='decrease_qty'),
    path('remove_item/<int:cart_id>/', remove_item, name='remove_item'),
    path('checkout/', checkout, name='checkout'),
    path('razorpay-callback/', razorpay_callback, name='razorpay_callback'),
    path('order-success/', order_success, name='order_success'),
    path('orders/', orders, name='orders'),
    path('profile/', profile, name='profile'),
    path('contact/', contact_us, name='contact'),
    path('about/', about, name='about'),
    path('faq/', faq, name='faq'),
    path('privacy/', privacy_policy, name='privacy'),
    path('logout/', logout, name='logout'),
]