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

ALLOWED_HOSTS = ['127.0.0.1', 'localhost', '0.0.0.0']
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

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ── Auth ──────────────────────────────────────────────────────────
LOGIN_REDIRECT_URL  = '/'
LOGOUT_REDIRECT_URL = '/accounts/login/'
LOGIN_URL           = '/accounts/login/'

# ── CSRF ──────────────────────────────────────────────────────────
CSRF_TRUSTED_ORIGINS = [
    'http://127.0.0.1:8000',
    'http://localhost:8000',
    'https://weblance.onrender.com',
]
if RENDER_EXTERNAL_HOSTNAME:
    CSRF_TRUSTED_ORIGINS.append(f'https://{RENDER_EXTERNAL_HOSTNAME}')

CSRF_COOKIE_SAMESITE = 'Lax'
SESSION_COOKIE_SAMESITE = 'Lax'

# ── Email ─────────────────────────────────────────────────────────
# Uses Gmail SMTP. Set EMAIL_HOST_PASSWORD to your Gmail App Password.
# Generate at: https://myaccount.google.com/apppasswords
EMAIL_BACKEND       = os.environ.get('EMAIL_BACKEND', 'django.core.mail.backends.smtp.EmailBackend')
EMAIL_HOST          = os.environ.get('EMAIL_HOST', 'smtp.gmail.com')
EMAIL_PORT          = int(os.environ.get('EMAIL_PORT', 587))
EMAIL_USE_TLS       = True
EMAIL_HOST_USER     = os.environ.get('EMAIL_HOST_USER', 'infoweblance01@gmail.com')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD', '')   # ← set your App Password here or in .env
DEFAULT_FROM_EMAIL  = os.environ.get('DEFAULT_FROM_EMAIL', 'Weblance <infoweblance01@gmail.com>')
GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY', 'AIzaSyDDCYVuOJsguXx_dlK_hFTnG_pucnq_3d0')

# ── Gemini AI ─────────────────────────────────────────────────────
# Set SITE_URL env var in production, e.g. https://yoursite.com
SITE_URL = os.environ.get('SITE_URL', '')
