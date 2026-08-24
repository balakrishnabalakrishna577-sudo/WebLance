"""
Management command: verify_cloudinary
Runs during build to confirm Cloudinary credentials work.
Exits with code 0 on success, prints warning on failure (non-blocking).
"""
import io
import os
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Verify Cloudinary credentials by running a test upload'

    def handle(self, *args, **options):
        cloud   = os.environ.get('CLOUDINARY_CLOUD_NAME', '')
        api_key = os.environ.get('CLOUDINARY_API_KEY', '')
        secret  = os.environ.get('CLOUDINARY_API_SECRET', '')

        self.stdout.write('>>> Verifying Cloudinary...')
        self.stdout.write(f'    cloud_name : {cloud}')
        self.stdout.write(f'    api_key    : {api_key[:8]}...' if api_key else '    api_key    : NOT SET')
        self.stdout.write(f'    api_secret : {secret[:8]}...' if secret else '    api_secret : NOT SET')

        if not (cloud and api_key and secret):
            self.stdout.write(self.style.WARNING(
                '    [SKIP] Cloudinary env vars not set — media will use local disk'
            ))
            return

        try:
            import cloudinary
            import cloudinary.uploader

            # Reconfigure with env vars directly (in case cached config is stale)
            cloudinary.config(
                cloud_name=cloud,
                api_key=api_key,
                api_secret=secret,
                secure=True,
            )

            # Upload a 1x1 white pixel PNG
            pixel = (
                b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01'
                b'\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde\x00\x00'
                b'\x00\x0cIDATx\x9cc\xf8\x0f\x00\x00\x01\x01\x00\x05\x18'
                b'\xd8N\x00\x00\x00\x00IEND\xaeB`\x82'
            )
            buf = io.BytesIO(pixel)
            result = cloudinary.uploader.upload(
                buf,
                folder='weblance_test',
                public_id='build_verify',
                overwrite=True,
                resource_type='image',
            )
            url = result.get('secure_url', '')
            self.stdout.write(self.style.SUCCESS(
                f'    [OK] Cloudinary upload test passed: {url[:60]}'
            ))
            # Clean up test image
            cloudinary.uploader.destroy('weblance_test/build_verify')

        except Exception as exc:
            self.stdout.write(self.style.ERROR(
                f'    [FAIL] Cloudinary test upload failed: {exc}'
            ))
            self.stdout.write(self.style.WARNING(
                '    Images will fall back to local disk — check CLOUDINARY_API_SECRET in Render env vars'
            ))
