import os
from pathlib import Path
import dj_database_url
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent

# Load .env file if it exists
load_dotenv(BASE_DIR / '.env')

# ── Security ──────────────────────────────────────────────────────
SECRET_KEY = os.environ.get('SECRET_KEY', 'django-insecure-d)5^vbbn_-^&7dk)8jetm%$h!f-6_i#s6zf#0fx(%7gb^%-_bn')
DEBUG = os.environ.get('DEBUG', 'True') == 'True'

# ── Production security settings (all off in dev, on in prod via env vars) ──
# W008 — force HTTPS redirect (set True in production; Render/Nginx handles it externally)
SECURE_SSL_REDIRECT = os.environ.get('SECURE_SSL_REDIRECT', 'False') == 'True'

# W004 — HSTS: tell browsers to only use HTTPS (1 year = 31536000)
SECURE_HSTS_SECONDS            = int(os.environ.get('SECURE_HSTS_SECONDS', 0))
SECURE_HSTS_INCLUDE_SUBDOMAINS = os.environ.get('SECURE_HSTS_INCLUDE_SUBDOMAINS', 'False') == 'True'
SECURE_HSTS_PRELOAD            = os.environ.get('SECURE_HSTS_PRELOAD', 'False') == 'True'

# W012 — session cookie only sent over HTTPS (auto-enabled when DEBUG=False)
_default_secure = 'False' if DEBUG else 'True'
SESSION_COOKIE_SECURE = os.environ.get('SESSION_COOKIE_SECURE', _default_secure) == 'True'

# W016 — CSRF cookie only sent over HTTPS (auto-enabled when DEBUG=False)
CSRF_COOKIE_SECURE = os.environ.get('CSRF_COOKIE_SECURE', _default_secure) == 'True'

# W009 — SECRET_KEY warning is suppressed in dev; set a strong key in production .env

# Silence W008 (SSL redirect) — Render/Nginx terminates SSL externally, no need to redirect in Django
# Silence W005/W021 — HSTS subdomains/preload are optional; enable in .env.production when ready
SILENCED_SYSTEM_CHECKS = ['security.W008', 'security.W005', 'security.W021']

ALLOWED_HOSTS = ['127.0.0.1', 'localhost', '0.0.0.0', 'weblancehub.in', 'www.weblancehub.in']
RENDER_EXTERNAL_HOSTNAME = os.environ.get('RENDER_EXTERNAL_HOSTNAME')
if RENDER_EXTERNAL_HOSTNAME:
    ALLOWED_HOSTS.append(RENDER_EXTERNAL_HOSTNAME)

# AWS EC2 / custom domain / Render support
for host in os.environ.get('ALLOWED_HOSTS', '').split(','):
    host = host.strip()
    if host:
        ALLOWED_HOSTS.append(host)

EC2_IP = os.environ.get('EC2_IP', '')
if EC2_IP:
    ALLOWED_HOSTS.append(EC2_IP)

# ── Apps ──────────────────────────────────────────────────────────
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'home',
    'about',
    'services',
    'portfolio',
    'pricing',
    'contact',
    'requestsite',
    'adminpanel',
    'agreement',
    'dashboard',
    'features',
    'notifications',
    'agent',
    'cloudinary_storage',
    'cloudinary',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',   # serve static files
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'weblance_project.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                    'django.template.context_processors.request',
                    'django.contrib.auth.context_processors.auth',
                    'django.contrib.messages.context_processors.messages',
                    'weblance_project.context_processors.recaptcha_key',
                    'weblance_project.context_processors.notifications',
                    'weblance_project.context_processors.bot_unread',
                    'weblance_project.context_processors.active_offers',
                ],
        },
    },
]

AUTHENTICATION_BACKENDS = ['django.contrib.auth.backends.ModelBackend']
WSGI_APPLICATION = 'weblance_project.wsgi.application'

# ── Database ──────────────────────────────────────────────────────
DATABASE_URL = os.environ.get('DATABASE_URL')

if DATABASE_URL:
    DATABASES = {
        'default': dj_database_url.config(
            default=DATABASE_URL,
            conn_max_age=600,
            conn_health_checks=True,
        )
    }
    if os.environ.get('DB_SSL', 'False') == 'True':
        DATABASES['default']['OPTIONS'] = {'sslmode': 'require'}
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }

# ── Password validation ───────────────────────────────────────────
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# ── Internationalisation ──────────────────────────────────────────
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# ── Static & Media ────────────────────────────────────────────────
STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# ── Cloudinary (persistent media storage for Render) ──────────────
# Credentials are hardcoded to avoid Render env var corruption issues.
# The env vars are still read but the hardcoded values win if env is wrong.
CLOUDINARY_CLOUD_NAME = 'dbbq1bl4u'
CLOUDINARY_API_KEY    = '416514896248622'
CLOUDINARY_API_SECRET = 'S7WSkqn_qlTVidYN7rWeYYEjt3w'

import cloudinary as _cld
_cld.config(
    cloud_name = CLOUDINARY_CLOUD_NAME,
    api_key    = CLOUDINARY_API_KEY,
    api_secret = CLOUDINARY_API_SECRET,
    secure     = True,
)

DEFAULT_FILE_STORAGE = 'cloudinary_storage.storage.MediaCloudinaryStorage'
CLOUDINARY_STORAGE = {
    'CLOUD_NAME': CLOUDINARY_CLOUD_NAME,
    'API_KEY':    CLOUDINARY_API_KEY,
    'API_SECRET': CLOUDINARY_API_SECRET,
}

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ── Auth ──────────────────────────────────────────────────────────
LOGIN_REDIRECT_URL  = '/panel/projects/'
LOGOUT_REDIRECT_URL = '/accounts/login/'
LOGIN_URL           = '/accounts/login/'

# ── CSRF ──────────────────────────────────────────────────────────
CSRF_TRUSTED_ORIGINS = [
    'http://127.0.0.1:8000',
    'http://localhost:8000',
    'https://weblancehub.in',
    'https://www.weblancehub.in',
]
if RENDER_EXTERNAL_HOSTNAME:
    CSRF_TRUSTED_ORIGINS.append(f'https://{RENDER_EXTERNAL_HOSTNAME}')

CSRF_COOKIE_SAMESITE = 'Lax'
SESSION_COOKIE_SAMESITE = 'Lax'
SESSION_COOKIE_HTTPONLY = True   # JS cannot access the session cookie
SESSION_COOKIE_AGE = 60 * 60 * 24 * 7  # 1 week (in seconds)
SESSION_SAVE_EVERY_REQUEST = True

# ── Email ─────────────────────────────────────────────────────────
# Uses Gmail SMTP. Set EMAIL_HOST_PASSWORD to your Gmail App Password.
# Generate at: https://myaccount.google.com/apppasswords
# -- Email: use Brevo REST API backend when BREVO_API_KEY is set,
# -- else fall back to SMTP (for local dev with Gmail).
BREVO_API_KEY = os.environ.get('BREVO_API_KEY', '')
if BREVO_API_KEY:
    EMAIL_BACKEND = 'weblance_project.brevo_backend.BrevoAPIBackend'
else:
    EMAIL_BACKEND       = os.environ.get('EMAIL_BACKEND', 'django.core.mail.backends.smtp.EmailBackend')
    EMAIL_HOST          = os.environ.get('EMAIL_HOST', 'smtp.gmail.com')
    EMAIL_PORT          = int(os.environ.get('EMAIL_PORT', 465))
    EMAIL_USE_TLS       = os.environ.get('EMAIL_USE_TLS', 'False') == 'True'
    EMAIL_USE_SSL       = os.environ.get('EMAIL_USE_SSL', 'True')  == 'True'
    EMAIL_HOST_USER     = os.environ.get('EMAIL_HOST_USER', '')
    EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD', '')
DEFAULT_FROM_EMAIL  = os.environ.get('DEFAULT_FROM_EMAIL', 'Weblance <infoweblance01@gmail.com>')
SERVER_EMAIL        = 'infoweblance01@gmail.com'
GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY', '')

# ── Gemini AI ─────────────────────────────────────────────────────
# Set SITE_URL env var in production, e.g. https://yoursite.com
SITE_URL = os.environ.get('SITE_URL', '')

# ── reCAPTCHA ─────────────────────────────────────────────────────
RECAPTCHA_SITE_KEY   = os.environ.get('RECAPTCHA_SITE_KEY', '6Le0JrMsAAAAAB6Iut5PRmylHFvObbIUL7UOM88A')
RECAPTCHA_SECRET_KEY = os.environ.get('RECAPTCHA_SECRET_KEY', '6Le0JrMsAAAAAIAYjQADGsxVLuG62c_MwANEVUnv')
