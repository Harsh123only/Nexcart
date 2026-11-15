from django.contrib import admin
from .models import CustomUser, EmailOTP


@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ['email', 'full_name', 'is_verified', 'is_staff', 'date_joined']
    search_fields = ['email', 'full_name']


@admin.register(EmailOTP)
class EmailOTPAdmin(admin.ModelAdmin):
    list_display = ['email', 'code', 'purpose', 'is_used', 'created_at']