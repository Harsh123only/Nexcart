"""
URL configuration for nexcart_core project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.views.generic import TemplateView
from django.conf import settings
from django.conf.urls.static import static
from accounts.views import request_email_otp, verify_email_otp, password_login, get_profile
from store.views import (
    list_categories, search_products, get_cart, update_cart, checkout_order, my_orders
)

admin.site.site_header = "NexCart Seller & Admin Command Center"
admin.site.site_title = "NexCart Admin"

urlpatterns = [
    path('', TemplateView.as_view(template_name='index.html'), name='home'),
    path('admin/', admin.site.urls),

    # Email OTP & JWT Authentication Endpoints
    path('api/auth/request-otp/', request_email_otp),
    path('api/auth/verify-otp/', verify_email_otp),
    path('api/auth/login/', password_login),
    path('api/auth/me/', get_profile),

    # Store Catalog, Live Search, Cart & Multi-Payment Checkout Endpoints
    path('api/store/categories/', list_categories),
    path('api/store/products/', search_products),
    path('api/store/cart/', get_cart),
    path('api/store/cart/update/', update_cart),
    path('api/store/checkout/', checkout_order),
    path('api/store/orders/', my_orders),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)