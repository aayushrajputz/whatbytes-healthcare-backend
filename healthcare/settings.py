"""
Django settings for healthcare project.

Generated for a production-grade Healthcare Backend API.
"""

import os
from pathlib import Path

from dotenv import load_dotenv

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

load_dotenv(BASE_DIR / '.env')


def env_bool(name, default=False):
    return os.getenv(name, str(default)).lower() in ('1', 'true', 'yes', 'on')


# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv(
    'SECRET_KEY',
    'django-insecure-dev-only-change-me-in-production',
)

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = env_bool('DEBUG', True)

ALLOWED_HOSTS = [
    h.strip()
    for h in os.getenv('ALLOWED_HOSTS', 'localhost,127.0.0.1').split(',')
    if h.strip()
]


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # Third party
    'rest_framework',
    'rest_framework_simplejwt',
    'corsheaders',
    'drf_spectacular',
    # Local apps
    'authentication',
    'patients',
    'doctors',
    'mappings',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'healthcare.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
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

WSGI_APPLICATION = 'healthcare.wsgi.application'


# Database
# Switch between SQLite (default) and PostgreSQL via DATABASE_URL in .env.
# Examples:
#   DATABASE_URL=sqlite:///db.sqlite3
#   DATABASE_URL=postgres://user:password@localhost:5432/healthcare

def build_database_config():
    database_url = os.getenv('DATABASE_URL', 'sqlite:///db.sqlite3')
    scheme, _, path = database_url.partition('://')

    if scheme == 'postgres' or scheme == 'postgresql':
        # postgres://user:pass@host:port/dbname
        auth_host, _, dbname = path.partition('/')
        auth, _, hostport = auth_host.rpartition('@')
        user, _, password = auth.partition(':')
        host, _, port = hostport.partition(':')
        return {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': dbname,
            'USER': user,
            'PASSWORD': password,
            'HOST': host or 'localhost',
            'PORT': port or '5432',
        }

    # sqlite:///path/to/db.sqlite3  (absolute or relative to BASE_DIR)
    db_path = path.lstrip('/') or 'db.sqlite3'
    if not db_path.endswith('.sqlite3'):
        db_path = f'{db_path}.sqlite3'
    return {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / db_path,
    }


DATABASES = {
    'default': build_database_config(),
}


# Password validation

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True


# Static files

STATIC_URL = 'static/'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


# Django REST Framework

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
    'EXCEPTION_HANDLER': 'rest_framework.views.exception_handler',
}


# Simple JWT

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': __import__('datetime').timedelta(
        minutes=int(os.getenv('JWT_ACCESS_TOKEN_LIFETIME_MINUTES', '60'))
    ),
    'REFRESH_TOKEN_LIFETIME': __import__('datetime').timedelta(
        days=int(os.getenv('JWT_REFRESH_TOKEN_LIFETIME_DAYS', '7'))
    ),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': False,
    'AUTH_HEADER_TYPES': ('Bearer',),
    'USER_ID_FIELD': 'id',
    'USER_ID_CLAIM': 'user_id',
}


# drf-spectacular (Swagger / OpenAPI)

SPECTACULAR_SETTINGS = {
    'TITLE': 'Healthcare Backend API',
    'DESCRIPTION': 'Patient, Doctor & Mapping management API with JWT auth.',
    'VERSION': '1.0.0',
    'SERVE_INCLUDE_SCHEMA': False,
}


# CORS

CORS_ALLOWED_ORIGINS = [
    o.strip()
    for o in os.getenv(
        'CORS_ALLOWED_ORIGINS', 'http://localhost:3000,http://127.0.0.1:3000'
    ).split(',')
    if o.strip()
]
CORS_ALLOW_CREDENTIALS = True
