import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'nexcart_core.settings')
django.setup()

from store.models import Category, Product

categories = [
    {"name": "Electronics & Audio", "slug": "electronics", "icon": "🎧"},
    {"name": "Computers & Keyboards", "slug": "computers", "icon": "⌨️"},
    {"name": "Smart Home & IoT", "slug": "smart-home", "icon": "🏠"},
    {"name": "Fitness & E-Mobility", "slug": "mobility", "icon": "⚡"},
    {"name": "Fashion & Watches", "slug": "fashion", "icon": "⌚"},
]

cat_objs = {}
for c in categories:
    obj, _ = Category.objects.get_or_create(slug=c["slug"], defaults={"name": c["name"], "icon": c["icon"]})
    cat_objs[c["slug"]] = obj

products = [
    {
        "category": cat_objs["electronics"],
        "title": "Sony WH-1000XM5 Wireless Noise-Canceling Headphones (Midnight Black)",
        "brand": "Sony",
        "description": "Industry-leading Dual Noise Sensor technology, 30-hour battery life, crystal-clear hands-free calling, and multipoint Bluetooth connection.",
        "price": 299.00,
        "mrp_price": 379.00,
        "stock_qty": 18,
        "image_url": "https://images.unsplash.com/photo-1618366712010-f4ae9c647dcb?auto=format&fit=crop&w=600&q=80",
        "rating": 4.8,
        "review_count": 1420,
        "is_featured": True,
    },
    {
        "category": cat_objs["computers"],
        "title": "Keychron Q1 Pro QMK/VIA Wireless Custom Mechanical Keyboard (75% Layout)",
        "brand": "Keychron",
        "description": "Full CNC machined aluminum body, hot-swappable tactile switches, double-gasket design, and customizable RGB backlight for developers.",
        "price": 189.00,
        "mrp_price": 219.00,
        "stock_qty": 12,
        "image_url": "https://images.unsplash.com/photo-1595225476474-87563907a212?auto=format&fit=crop&w=600&q=80",
        "rating": 4.9,
        "review_count": 640,
        "is_featured": True,
    },
    {
        "category": cat_objs["fashion"],
        "title": "Garmin Fenix 7X Solar Multisport GPS Smartwatch (Slate Gray)",
        "brand": "Garmin",
        "description": "Power Glass solar charging lens, built-in LED flashlight, preloaded TopoActive Europe maps, and 28-day battery endurance.",
        "price": 549.00,
        "mrp_price": 699.00,
        "stock_qty": 9,
        "image_url": "https://images.unsplash.com/photo-1523275335684-37898b6baf30?auto=format&fit=crop&w=600&q=80",
        "rating": 4.7,
        "review_count": 890,
        "is_featured": True,
    },
    {
        "category": cat_objs["computers"],
        "title": "LG UltraGear 27-Inch QHD 240Hz Nano IPS Gaming & Coding Monitor",
        "brand": "LG",
        "description": "2560x1440 resolution, 1ms GtG response time, NVIDIA G-SYNC compatible, HDR400, and ergonomic height/pivot stand.",
        "price": 349.00,
        "mrp_price": 449.00,
        "stock_qty": 14,
        "image_url": "https://images.unsplash.com/photo-1527443224154-c4a3942d3acf?auto=format&fit=crop&w=600&q=80",
        "rating": 4.6,
        "review_count": 512,
        "is_featured": False,
    },
    {
        "category": cat_objs["smart-home"],
        "title": "Philips Hue White & Color Ambiance Smart Lightstrip Plus (2m Base Kit)",
        "brand": "Philips Hue",
        "description": "16 million colors, Bluetooth and Hue Bridge compatible, works with Alexa, Google Home, and Apple HomeKit.",
        "price": 74.99,
        "mrp_price": 89.99,
        "stock_qty": 30,
        "image_url": "https://images.unsplash.com/photo-1558002038-1055907df827?auto=format&fit=crop&w=600&q=80",
        "rating": 4.5,
        "review_count": 2110,
        "is_featured": False,
    },
    {
        "category": cat_objs["mobility"],
        "title": "ABUS Bordo Granit XPlus 6500 Folding E-Bike Lock (Security Level 15)",
        "brand": "ABUS",
        "description": "5.5mm hardened steel bars with extra-soft coating, XPlus cylinder against picking, ideal for urban Berlin e-bike commuters.",
        "price": 119.00,
        "mrp_price": 159.95,
        "stock_qty": 22,
        "image_url": "https://images.unsplash.com/photo-1532298229144-0ec0c57515c7?auto=format&fit=crop&w=600&q=80",
        "rating": 4.8,
        "review_count": 975,
        "is_featured": True,
    },
]

for p in products:
    Product.objects.get_or_create(title=p["title"], defaults=p)

print("Seeded 5 Categories & 6 Starter Products successfully!")