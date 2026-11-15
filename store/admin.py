from django.contrib import admin
from .models import Category, Product, CartItem, Order, OrderItem


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'icon']
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['title', 'category', 'brand', 'price', 'mrp_price', 'stock_qty', 'rating', 'is_featured']
    list_filter = ['category', 'is_featured', 'brand']
    search_fields = ['title', 'brand', 'description']
    list_editable = ['price', 'stock_qty', 'is_featured']


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ['product_title', 'quantity', 'unit_price']


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['order_number', 'user', 'total_amount', 'payment_method', 'payment_status', 'order_status', 'created_at']
    list_filter = ['order_status', 'payment_method', 'payment_status']
    search_fields = ['order_number', 'user__email']
    list_editable = ['order_status']
    inlines = [OrderItemInline]


admin.site.register(CartItem)