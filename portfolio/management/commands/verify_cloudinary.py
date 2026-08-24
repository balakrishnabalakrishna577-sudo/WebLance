"""
Management command: verify_cloudinary
Runs during build to confirm Cloudinary credentials work.
"""
import io
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Verify Cloudinary credentials by running a test upload'

    def handle(self, *args, **options):
        from django.conf import settings
        import cloudinary
        import cloudinary.uploader

        cloud   = settings.CLOUDINARY_CLOUD_NAME
        api_key = settings.CLOUDINARY_API_KEY
        secret  = settings.CLOUDINARY_API_SECRET

        self.stdout.write('>>> Verifying Cloudinary...')
        self.stdout.write(f'    cloud_name : {cloud}')
        self.stdout.write(f'    api_key    : {api_key[:8]}...')
        self.stdout.write(f'    api_secret : {secret[:8]}... ({len(secret)} chars)')

        # Force reconfigure using settings values (not env vars)
        cloudinary.config(
            cloud_name=cloud,
            api_key=api_key,
            api_secret=secret,
            secure=True,
        )

        # 1x1 white pixel PNG
        pixel = (
            b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01'
            b'\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde\x00\x00'
            b'\x00\x0cIDATx\x9cc\xf8\x0f\x00\x00\x01\x01\x00\x05\x18'
            b'\xd8N\x00\x00\x00\x00IEND\xaeB`\x82'
        )
        try:
            result = cloudinary.uploader.upload(
                io.BytesIO(pixel),
                folder='weblance_test',
                public_id='build_verify',
                overwrite=True,
                resource_type='image',
            )
            url = result.get('secure_url', '')
            self.stdout.write(self.style.SUCCESS(
                f'    [OK] Cloudinary upload passed: {url[:65]}'
            ))
            cloudinary.uploader.destroy('weblance_test/build_verify')
        except Exception as exc:
            self.stdout.write(self.style.ERROR(
                f'    [FAIL] Cloudinary upload failed: {exc}'
            ))
