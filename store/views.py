import uuid
from decimal import Decimal
from django.db import transaction
from django.db.models import Q
from django.core.mail import send_mail
from django.conf import settings
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from .models import Category, Product, CartItem, Order, OrderItem


def serialize_product(p, request=None):
    img = ""
    if p.image:
        img = request.build_absolute_uri(p.image.url) if request else p.image.url
    elif p.image_url:
        img = p.image_url

    return {
        "id": p.id,
        "title": p.title,
        "brand": p.brand,
        "category": p.category.name,
        "category_slug": p.category.slug,
        "description": p.description,
        "price": float(p.price),
        "mrp_price": float(p.mrp_price),
        "discount_percent": p.discount_percent,
        "stock_qty": p.stock_qty,
        "image": img,
        "rating": p.rating,
        "review_count": p.review_count,
        "is_featured": p.is_featured,
    }


@api_view(['GET'])
@permission_classes([AllowAny])
def list_categories(request):
    cats = Category.objects.all()
    return Response([{"id": c.id, "name": c.name, "slug": c.slug, "icon": c.icon} for c in cats])


@api_view(['GET'])
@permission_classes([AllowAny])
def search_products(request):
    """
    Supports live search bar queries (?q=...), category filtering (?category=electronics),
    and sorting (?sort=price_asc | price_desc | rating).
    """
    q = request.GET.get('q', '').strip()
    category_slug = request.GET.get('category', '').strip()
    sort_by = request.GET.get('sort', 'featured')

    qs = Product.objects.select_related('category').all()

    if q:
        qs = qs.filter(
            Q(title__icontains=q) |
            Q(brand__icontains=q) |
            Q(description__icontains=q) |
            Q(category__name__icontains=q)
        )
    if category_slug and category_slug != 'all':
        qs = qs.filter(category__slug=category_slug)

    if sort_by == 'price_asc':
        qs = qs.order_by('price')
    elif sort_by == 'price_desc':
        qs = qs.order_by('-price')
    elif sort_by == 'rating':
        qs = qs.order_by('-rating')
    else:
        qs = qs.order_by('-is_featured', '-created_at')

    return Response([serialize_product(p, request) for p in qs])


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_cart(request):
    items = CartItem.objects.select_related('product', 'product__category').filter(user=request.user)
    cart_data = []
    subtotal = Decimal('0.00')

    for item in items:
        line_total = item.product.price * item.quantity
        subtotal += line_total
        cart_data.append({
            "id": item.id,
            "product": serialize_product(item.product, request),
            "quantity": item.quantity,
            "line_total": float(line_total),
        })

    return Response({
        "items": cart_data,
        "total_items": sum(i.quantity for i in items),
        "subtotal": float(subtotal),
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def update_cart(request):
    product_id = request.data.get('product_id')
    action = request.data.get('action', 'add')  # 'add', 'decrease', 'remove'

    product = Product.objects.filter(id=product_id).first()
    if not product:
        return Response({"error": "Product not found"}, status=status.HTTP_404_NOT_FOUND)

    cart_item, created = CartItem.objects.get_or_create(user=request.user, product=product)

    if action == 'add':
        if not created:
            if cart_item.quantity + 1 > product.stock_qty:
                return Response({"error": "Maximum available stock reached."}, status=status.HTTP_400_BAD_REQUEST)
            cart_item.quantity += 1
            cart_item.save()
    elif action == 'decrease':
        if cart_item.quantity > 1:
            cart_item.quantity -= 1
            cart_item.save()
        else:
            cart_item.delete()
    elif action == 'remove':
        cart_item.delete()

    return Response({"message": "Cart updated"})


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def checkout_order(request):
    """
    Concurrency-safe checkout with row-level inventory locking (select_for_update),
    multi-payment method support, and automated order confirmation email.
    """
    shipping_address = request.data.get('shipping_address', '').strip()
    payment_method = request.data.get('payment_method', 'CARD').upper()

    if not shipping_address:
        return Response({"error": "Shipping address is required."}, status=status.HTTP_400_BAD_REQUEST)

    with transaction.atomic():
        cart_items = list(CartItem.objects.select_related('product').filter(user=request.user))
        if not cart_items:
            return Response({"error": "Your cart is empty."}, status=status.HTTP_400_BAD_REQUEST)

        total = Decimal('0.00')
        locked_products = {}

        for item in cart_items:
            prod = Product.objects.select_for_update().get(id=item.product.id)
            if prod.stock_qty < item.quantity:
                return Response(
                    {"error": f"Insufficient stock for {prod.title}. Only {prod.stock_qty} left."},
                    status=status.HTTP_400_BAD_REQUEST
                )
            locked_products[prod.id] = prod
            total += prod.price * item.quantity

        order_num = f"NX-{uuid.uuid4().hex[:8].upper()}"
        order = Order.objects.create(
            order_number=order_num,
            user=request.user,
            shipping_address=shipping_address,
            payment_method=payment_method,
            payment_status='PENDING' if payment_method == 'COD' else 'PAID',
            total_amount=total,
        )

        for item in cart_items:
            prod = locked_products[item.product.id]
            prod.stock_qty -= item.quantity
            prod.save(update_fields=['stock_qty'])

            OrderItem.objects.create(
                order=order,
                product=prod,
                product_title=prod.title,
                quantity=item.quantity,
                unit_price=prod.price,
            )

        CartItem.objects.filter(user=request.user).delete()

        # Save user's default address for future 1-click checkouts
        request.user.default_address = shipping_address
        request.user.save(update_fields=['default_address'])

    send_mail(
        subject=f"NexCart Order Confirmed: {order.order_number}",
        message=(
            f"Hi {request.user.full_name},\n\n"
            f"Thank you for shopping with NexCart! Your order {order.order_number} for €{order.total_amount} "
            f"({order.get_payment_method_display()}) is confirmed and being prepared for dispatch to:\n"
            f"{order.shipping_address}\n"
        ),
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[request.user.email],
        fail_silently=True,
    )

    return Response({
        "message": "Order placed successfully!",
        "order_number": order.order_number,
        "total_amount": float(order.total_amount),
        "payment_method": order.get_payment_method_display(),
    }, status=status.HTTP_201_CREATED)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def my_orders(request):
    orders = Order.objects.prefetch_related('items').filter(user=request.user).order_by('-created_at')
    data = []
    for o in orders:
        data.append({
            "order_number": o.order_number,
            "total_amount": float(o.total_amount),
            "payment_method": o.get_payment_method_display(),
            "payment_status": o.payment_status,
            "order_status": o.order_status,
            "shipping_address": o.shipping_address,
            "created_at": o.created_at.strftime("%d %b %Y, %H:%M"),
            "items": [
                {"title": i.product_title, "quantity": i.quantity, "unit_price": float(i.unit_price)}
                for i in o.items.all()
            ]
        })
    return Response(data)