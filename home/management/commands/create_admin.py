import os
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User


class Command(BaseCommand):
    help = 'Create superuser from environment variables (safe for production)'

    def handle(self, *args, **kwargs):
        username = os.environ.get('ADMIN_USER', 'balakrishna')
        email    = os.environ.get('ADMIN_EMAIL', 'infoweblance01@gmail.com')
        password = os.environ.get('ADMIN_PASS', 'admin123')

        if User.objects.filter(username=username).exists():
            self.stdout.write(self.style.WARNING(f'Admin "{username}" already exists — skipped.'))
        else:
            User.objects.create_superuser(username=username, email=email, password=password)
            self.stdout.write(self.style.SUCCESS(f'Superuser "{username}" created successfully.'))
