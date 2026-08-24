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

echo ">>> Verifying Cloudinary connection..."
python manage.py verify_cloudinary || echo "Cloudinary check failed — check CLOUDINARY_API_SECRET env var"

echo ">>> Build complete."
