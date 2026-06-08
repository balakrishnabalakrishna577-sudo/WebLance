"""
Comprehensive sample data for Weblance admin panel.
Run: python add_sample_data.py
"""
import os, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'weblance_project.settings')
django.setup()

from django.contrib.auth.models import User
from portfolio.models import PortfolioItem
from pricing.models import PricingPlan
from home.models import Testimonial
from contact.models import ContactMessage
from requestsite.models import WebsiteRequest

print("=" * 50)
print("  Weblance — Loading Sample Data")
print("=" * 50)

# ── 1. PORTFOLIO ──────────────────────────────────────────────────
PortfolioItem.objects.all().delete()
portfolio = [
    ("FashionHub E-Commerce Store",      "ecommerce", "Full-featured online clothing store with Razorpay payment integration, inventory management, and order tracking."),
    ("TechSolutions Corporate Website",  "business",  "Modern corporate website for a Bangalore-based IT firm with service pages, team section, and contact form."),
    ("GreenFarm Organic Landing Page",   "landing",   "High-converting landing page for organic farm products with lead capture and WhatsApp integration."),
    ("MediCare Hospital Website",        "business",  "Professional hospital website with doctor profiles, appointment booking, and department listings."),
    ("StyleKart Fashion Store",          "ecommerce", "Multi-category fashion e-commerce with size filters, wishlist, and COD/online payment options."),
    ("LaunchPad Startup Landing Page",   "landing",   "Product launch landing page with countdown timer, feature highlights, and email signup."),
    ("Devanahalli Real Estate Portal",   "business",  "Property listing website with search filters, map integration, and inquiry forms."),
    ("QuickBite Restaurant Website",     "business",  "Restaurant website with digital menu, table reservation, and online order integration."),
    ("EduLearn School Portal",           "business",  "School website with student portal, notice board, faculty directory, and gallery."),
    ("SportZone E-Commerce",             "ecommerce", "Sports equipment online store with product variants, reviews, and bulk order discounts."),
    ("CloudTech App Landing Page",       "landing",   "SaaS product landing page with pricing table, feature comparison, and free trial signup."),
    ("Nair Consultancy Business Site",   "business",  "Professional consultancy website with service packages, client testimonials, and blog."),
]
for title, cat, desc in portfolio:
    PortfolioItem.objects.create(title=title, category=cat, description=desc)
    print(f"  ✓ Portfolio: {title}")

# ── 2. PRICING PLANS ─────────────────────────────────────────────
PricingPlan.objects.all().delete()
plans = [
    ("Starter",    "₹8,000",  "Perfect for small businesses and startups",
     "1-page website\nMobile responsive\nContact form\nBasic SEO\nWhatsApp button\n-Blog section\n-E-Commerce\n-Admin panel",
     "7-10 days", False, 1),
    ("Business",   "₹15,000", "Ideal for growing businesses",
     "Up to 5 pages\nMobile responsive\nContact form\nSEO optimization\nWhatsApp button\nAdmin panel\nGoogle Maps\n-E-Commerce",
     "15-20 days", True, 2),
    ("E-Commerce", "₹25,000", "Complete online store solution",
     "Full online store\nProduct management\nRazorpay integration\nOrder tracking\nCustomer accounts\nAdmin dashboard\nSEO setup\nMobile responsive",
     "30-45 days", False, 3),
    ("Premium",    "₹40,000", "Enterprise-grade web solution",
     "Custom web app\nUnlimited pages\nAdvanced features\nAPI integrations\nAdmin dashboard\nSEO + Analytics\nPriority support\nFree maintenance 3mo",
     "45-60 days", False, 4),
]
for name, price, desc, features, delivery, popular, order in plans:
    PricingPlan.objects.create(
        name=name, price=price, description=desc,
        features=features, delivery_time=delivery,
        is_popular=popular, order=order
    )
    print(f"  ✓ Pricing: {name} — {price}")

# ── 3. TESTIMONIALS ───────────────────────────────────────────────
Testimonial.objects.all().delete()
testimonials = [
    ("Rajesh Kumar",   "Owner, FashionHub India",        "RK", "WEBLANCE delivered our e-commerce site in just 3 weeks. The design is stunning and our sales have increased by 40% since launch. Highly recommend!", 5, 1),
    ("Priya Sharma",   "CEO, TechSolutions Bangalore",   "PS", "Professional team, clean code, and excellent communication throughout. Our business website looks world-class and loads super fast.", 5, 2),
    ("Arjun Mehta",    "Founder, LaunchPad Startup",     "AM", "The landing page they built for our product launch converted 3x better than our old site. Worth every rupee. Will definitely work with them again.", 5, 3),
    ("Sunita Nair",    "Director, Nair Consultancy",     "SN", "Affordable pricing, premium quality. They redesigned our outdated website and the difference is night and day. Our clients love the new look.", 5, 4),
    ("Vikram Rao",     "MD, Rao Enterprises",            "VR", "Fast delivery, responsive support, and a beautiful result. WEBLANCE understood our vision perfectly and executed it flawlessly.", 5, 5),
    ("Deepa Krishnan", "Principal, EduLearn School",     "DK", "Our school website is now modern, easy to update, and parents love it. The team was patient with all our change requests.", 5, 6),
    ("Mohammed Irfan", "Owner, QuickBite Restaurant",    "MI", "The restaurant website with online menu and reservation system has brought us so many new customers. Excellent work!", 5, 7),
]
for name, role, initials, text, rating, order in testimonials:
    Testimonial.objects.create(
        name=name, role=role, initials=initials,
        text=text, rating=rating, is_active=True, order=order
    )
    print(f"  ✓ Testimonial: {name}")

# ── 4. CONTACT MESSAGES ───────────────────────────────────────────
ContactMessage.objects.all().delete()
contacts = [
    ("Rahul Verma",    "rahul.verma@gmail.com",      "+91 9876543210", "E-Commerce",  "Hi, I need an online store for my clothing business. Can you share your pricing and timeline?"),
    ("Anita Desai",    "anita.desai@yahoo.com",       "+91 8765432109", "Business",    "We need a professional website for our consultancy firm. Please contact us for a discussion."),
    ("Suresh Patil",   "suresh.patil@outlook.com",    "+91 7654321098", "Restaurant",  "Looking for a restaurant website with online menu and table booking. What is the cost?"),
    ("Kavitha Reddy",  "kavitha.reddy@gmail.com",     "+91 6543210987", "Education",   "Our school needs a new website. We want student portal, notice board, and gallery features."),
    ("Arun Nair",      "arun.nair@gmail.com",         "+91 9988776655", "Landing Page","Need a landing page for my new product launch next month. Urgent requirement."),
]
for name, email, phone, btype, msg in contacts:
    ContactMessage.objects.create(
        name=name, email=email, phone=phone,
        business_type=btype, message=msg
    )
    print(f"  ✓ Contact: {name}")

# ── 5. WEBSITE REQUESTS ───────────────────────────────────────────
WebsiteRequest.objects.all().delete()
requests_data = [
    ("Rajesh Kumar",   "FashionHub India",       "+91 9876543210", "rajesh@fashionhub.in",  "ecommerce", "high",    "Full e-commerce store with Razorpay, product management, and order tracking.",    "completed"),
    ("Priya Sharma",   "TechSolutions Pvt Ltd",  "+91 8765432109", "priya@techsolutions.in", "business",  "medium",  "Corporate website with 5 pages, team section, services, and contact form.",       "completed"),
    ("Arjun Mehta",    "LaunchPad Startup",      "+91 7654321098", "arjun@launchpad.in",     "landing",   "low",     "Single landing page for SaaS product with pricing table and free trial signup.",  "active"),
    ("Sunita Nair",    "Nair Consultancy",       "+91 6543210987", "sunita@nairconsult.in",  "business",  "medium",  "Redesign of existing consultancy website with modern UI and blog section.",        "in_progress"),
    ("Vikram Rao",     "Rao Enterprises",        "+91 9988776655", "vikram@raoent.in",       "custom",    "premium", "Custom web application for inventory and order management system.",               "in_progress"),
    ("Deepa Krishnan", "EduLearn School",        "+91 8877665544", "deepa@edulearn.in",      "business",  "medium",  "School website with student portal, notice board, faculty directory.",            "received"),
    ("Mohammed Irfan", "QuickBite Restaurant",   "+91 7766554433", "irfan@quickbite.in",     "business",  "low",     "Restaurant website with digital menu, table reservation, and gallery.",           "new"),
    ("Anita Desai",    "Desai Consultants",      "+91 6655443322", "anita@desaiconsult.in",  "business",  "medium",  "Professional website for HR consultancy with service listings and contact.",      "new"),
]
for name, bname, phone, email, wtype, budget, desc, status in requests_data:
    WebsiteRequest.objects.create(
        name=name, business_name=bname, phone=phone, email=email,
        website_type=wtype, budget=budget, description=desc, status=status
    )
    print(f"  ✓ Request: {bname} ({status})")

# ── 6. EXTRA USERS ────────────────────────────────────────────────
for username, email, fname, lname in [
    ("rajesh_k",  "rajesh@fashionhub.in",   "Rajesh",  "Kumar"),
    ("priya_s",   "priya@techsolutions.in",  "Priya",   "Sharma"),
    ("arjun_m",   "arjun@launchpad.in",      "Arjun",   "Mehta"),
]:
    if not User.objects.filter(username=username).exists():
        User.objects.create_user(
            username=username, email=email,
            first_name=fname, last_name=lname,
            password="client123"
        )
        print(f"  ✓ User: {username}")

print()
print("=" * 50)
print("  All sample data loaded successfully!")
print("=" * 50)
print(f"  Portfolio items : {PortfolioItem.objects.count()}")
print(f"  Pricing plans   : {PricingPlan.objects.count()}")
print(f"  Testimonials    : {Testimonial.objects.count()}")
print(f"  Contact messages: {ContactMessage.objects.count()}")
print(f"  Website requests: {WebsiteRequest.objects.count()}")
print(f"  Users           : {User.objects.count()}")
print()
print("  Admin panel: http://127.0.0.1:8000/panel/")
print("  Login: balakrishna / admin123")
