#!/usr/bin/env bash
# ── Render Build Script ──────────────────────────────────────────
set -o errexit

echo ">>> Installing dependencies..."
pip install -r requirements.txt --no-warn-script-location

echo ">>> Collecting static files..."
python manage.py collectstatic --noinput

echo ">>> Running migrations..."
python manage.py migrate --noinput || echo "Migrations failed — check DATABASE_URL"

echo ">>> Creating admin user..."
python manage.py create_admin || echo "create_admin failed — skipping"

echo ">>> Seeding pricing plans..."
python manage.py seed_pricing || echo "seed_pricing failed — skipping"

echo ">>> Cleaning up broken portfolio items (non-Cloudinary images)..."
python manage.py shell -c "
from portfolio.models import PortfolioItem
import cloudinary.uploader

deleted = 0
for item in PortfolioItem.objects.all():
    try:
        url = item.image.url if item.image and item.image.name else ''
        is_cloudinary = 'res.cloudinary.com' in url
        if not is_cloudinary:
            print(f'Deleting bad item: {item.title!r} | url: {url[:60]}')
            item.delete()
            deleted += 1
    except Exception as e:
        print(f'Deleting item with error: {item.title!r} | error: {e}')
        item.delete()
        deleted += 1

print(f'Cleanup done: deleted {deleted} item(s) with non-Cloudinary images')
" || echo "Portfolio cleanup skipped"

echo ">>> Verifying Cloudinary connection..."
python manage.py verify_cloudinary || echo "Cloudinary check failed"

echo ">>> Build complete."
