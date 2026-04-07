#!/usr/bin/env bash
# Render build script
set -o errexit

pip install -r requirements.txt --no-warn-script-location

python manage.py collectstatic --noinput
python manage.py migrate
python manage.py create_admin
