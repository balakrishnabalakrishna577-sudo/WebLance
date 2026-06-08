"""
Management command to seed default pricing plans.
Safe to run multiple times — uses update_or_create so existing data is not duplicated.
Usage: python manage.py seed_pricing
"""
from django.core.management.base import BaseCommand
from pricing.models import PricingPlan


PLANS = [
    {
        "name": "Starter",
        "price": "₹8,000",
        "description": "Perfect for small businesses and startups",
        "features": (
            "1-page website\n"
            "Mobile responsive\n"
            "Contact form\n"
            "Basic SEO\n"
            "WhatsApp button\n"
            "-Blog section\n"
            "-E-Commerce\n"
            "-Admin panel"
        ),
        "delivery_time": "7-10 days",
        "is_popular": False,
        "order": 1,
    },
    {
        "name": "Business",
        "price": "₹15,000",
        "description": "Ideal for growing businesses",
        "features": (
            "Up to 5 pages\n"
            "Mobile responsive\n"
            "Contact form\n"
            "SEO optimization\n"
            "WhatsApp button\n"
            "Admin panel\n"
            "Google Maps\n"
            "-E-Commerce"
        ),
        "delivery_time": "15-20 days",
        "is_popular": True,
        "order": 2,
    },
    {
        "name": "E-Commerce",
        "price": "₹25,000",
        "description": "Complete online store solution",
        "features": (
            "Full online store\n"
            "Product management\n"
            "Razorpay integration\n"
            "Order tracking\n"
            "Customer accounts\n"
            "Admin dashboard\n"
            "SEO setup\n"
            "Mobile responsive"
        ),
        "delivery_time": "30-45 days",
        "is_popular": False,
        "order": 3,
    },
    {
        "name": "Premium",
        "price": "₹40,000",
        "description": "Enterprise-grade web solution",
        "features": (
            "Custom web app\n"
            "Unlimited pages\n"
            "Advanced features\n"
            "API integrations\n"
            "Admin dashboard\n"
            "SEO + Analytics\n"
            "Priority support\n"
            "Free maintenance 3mo"
        ),
        "delivery_time": "45-60 days",
        "is_popular": False,
        "order": 4,
    },
]


class Command(BaseCommand):
    help = "Seed default pricing plans (safe to re-run)"

    def handle(self, *args, **options):
        created_count = 0
        updated_count = 0

        for plan_data in PLANS:
            obj, created = PricingPlan.objects.update_or_create(
                name=plan_data["name"],
                defaults={
                    "price": plan_data["price"],
                    "description": plan_data["description"],
                    "features": plan_data["features"],
                    "delivery_time": plan_data["delivery_time"],
                    "is_popular": plan_data["is_popular"],
                    "order": plan_data["order"],
                },
            )
            if created:
                created_count += 1
                self.stdout.write(self.style.SUCCESS(f"  Created: {obj.name}"))
            else:
                updated_count += 1
                self.stdout.write(f"  Already exists (updated): {obj.name}")

        self.stdout.write(
            self.style.SUCCESS(
                f"\nDone. {created_count} created, {updated_count} updated."
            )
        )
