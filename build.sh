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

echo ">>> Cleaning up broken portfolio items..."
python manage.py shell -c "
from portfolio.models import PortfolioItem
import cloudinary
# Delete any items whose images are NOT on Cloudinary
bad = []
for item in PortfolioItem.objects.all():
    try:
        url = item.image.url if item.image and item.image.name else ''
        if url and 'cloudinary' not in url:
            bad.append(item.pk)
            print(f'Removing bad item: {item.title!r} -> {url[:60]}')
    except Exception:
        bad.append(item.pk)
if bad:
    PortfolioItem.objects.filter(pk__in=bad).delete()
    print(f'Deleted {len(bad)} items with local/broken images')
else:
    print('No broken portfolio items found')
" || echo "Portfolio cleanup skipped"

echo ">>> Verifying Cloudinary connection..."
python manage.py verify_cloudinary || echo "Cloudinary check failed"

echo ">>> Build complete."
