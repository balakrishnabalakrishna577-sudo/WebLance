import os, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'weblance_project.settings')
django.setup()
from portfolio.models import PortfolioItem
for item in PortfolioItem.objects.all():
    img = item.image.name if item.image else 'none'
    print(f"ID:{item.pk} | {item.title} | {item.category} | {img}")
