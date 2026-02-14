import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
SECRET_KEY = os.getenv('DJANGO_SECRET_KEY', 'dev-secret-key')
DEBUG = os.getenv('DEBUG', 'true').lower() == 'true'
ALLOWED_HOSTS = ['*']

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'education',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
]

ROOT_URLCONF = 'config.urls'
TEMPLATES = [{
    'BACKEND': 'django.template.backends.django.DjangoTemplates',
    'DIRS': [BASE_DIR / 'templates'],
    'APP_DIRS': True,
    'OPTIONS': {'context_processors': [
        'django.template.context_processors.request',
        'django.contrib.auth.context_processors.auth',
        'django.contrib.messages.context_processors.messages',
    ]},
}]
WSGI_APPLICATION = 'config.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': os.getenv('TXN_DB_ENGINE', 'django.db.backends.sqlite3'),
        'NAME': os.getenv('TXN_DB_NAME', BASE_DIR / 'db.sqlite3'),
        'USER': os.getenv('TXN_DB_USER', ''),
        'PASSWORD': os.getenv('TXN_DB_PASSWORD', ''),
        'HOST': os.getenv('TXN_DB_HOST', ''),
        'PORT': os.getenv('TXN_DB_PORT', ''),
    },
    'reporting': {
        'ENGINE': os.getenv('RPT_DB_ENGINE', 'django.db.backends.sqlite3'),
        'NAME': os.getenv('RPT_DB_NAME', BASE_DIR / 'reporting.sqlite3'),
        'USER': os.getenv('RPT_DB_USER', ''),
        'PASSWORD': os.getenv('RPT_DB_PASSWORD', ''),
        'HOST': os.getenv('RPT_DB_HOST', ''),
        'PORT': os.getenv('RPT_DB_PORT', ''),
    }
}

DATABASE_ROUTERS = ['education.db_router.EducationRouter']
AUTH_PASSWORD_VALIDATORS = []
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
LOGIN_URL = '/login/'
LOGIN_REDIRECT_URL = '/dashboard/'
