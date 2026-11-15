from django.db import models
from django.conf import settings


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(unique=True)
    icon = models.CharField(max_length=50, default="🛍️")

    class Meta:
        verbose_name_plural = "Categories"

    def __str__(self):
        return self.name


class Product(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products')
    title = models.CharField(max_length=255)
    brand = models.CharField(max_length=100, default="NexCart Prime")
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    mrp_price = models.DecimalField(max_digits=10, decimal_places=2, help_text="Original strikethrough price")
    stock_qty = models.PositiveIntegerField(default=25)
    image = models.ImageField(upload_to='products/', blank=True, null=True)
    image_url = models.URLField(blank=True, help_text="Optional external image URL if not uploading a file")
    rating = models.FloatField(default=4.5)
    review_count = models.PositiveIntegerField(default=12)
    is_featured = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def discount_percent(self):
        if self.mrp_price and self.mrp_price > self.price:
            return int(round(((self.mrp_price - self.price) / self.mrp_price) * 100))
        return 0

    def __str__(self):
        return f"{self.title} (€{self.price})"


class CartItem(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='cart_items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'product')


class Order(models.Model):
    PAYMENT_CHOICES = [
        ('CARD', 'Credit / Debit Card (Stripe)'),
        ('PAYPAL', 'PayPal / Klarna Express'),
        ('COD', 'Cash on Delivery'),
    ]
    STATUS_CHOICES = [
        ('CONFIRMED', 'Confirmed'),
        ('PACKED', 'Packed at Warehouse'),
        ('SHIPPED', 'Out for Delivery'),
        ('DELIVERED', 'Delivered'),
    ]

    order_number = models.CharField(max_length=20, unique=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='orders')
    shipping_address = models.TextField()
    payment_method = models.CharField(max_length=20, choices=PAYMENT_CHOICES, default='CARD')
    payment_status = models.CharField(max_length=20, default='PAID')
    order_status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='CONFIRMED')
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.order_number} - {self.user.email}"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True)
    product_title = models.CharField(max_length=255)
    quantity = models.PositiveIntegerField()
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)