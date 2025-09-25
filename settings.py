# === TEST DEPLOY ERROR ===
# Якщо потрібно навмисно зупинити деплой, розкоментуй рядок нижче:
raise Exception("TEST DEPLOY ERROR")

print("=== SETTINGS.PY IS LOADING ===")
print(f"Settings file path: {__file__}")

from pathlib import Path
import os
import logging

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.environ.get('SECRET_KEY', 'django-insecure-default-key-for-local-dev')

# Налаштування DEBUG - одне значення
DEBUG = os.environ.get('DJANGO_DEBUG', 'False').lower() in ['true', '1', 'yes']

# Початкове значення ALLOWED_HOSTS — дозволяємо всі (для Railway тестів)
ALLOWED_HOSTS = ['*']

# Додати домени з Railway змінних середовища (вони додадуться, навіть якщо є '*')
railway_public = os.environ.get('RAILWAY_PUBLIC_DOMAIN')
railway_private = os.environ.get('RAILWAY_PRIVATE_DOMAIN')

if railway_public:
    ALLOWED_HOSTS.append(railway_public)
if railway_private:
    ALLOWED_HOSTS.append(railway_private)

INSTALLED_APPS = [
    'scheduler.apps.SchedulerConfig',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'parent_drive.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'parent_drive.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

AUTH_PASSWORD_VALIDATORS = []

LANGUAGE_CODE = 'uk'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

STATIC_URL = 'static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

LOGIN_REDIRECT_URL = '/'
LOGIN_URL = '/accounts/login/'
LOGOUT_REDIRECT_URL = '/'

# Логування для відладки
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
logger.info(f"FINAL ALLOWED_HOSTS: {ALLOWED_HOSTS}")
logger.info(f"DEBUG: {DEBUG}")
