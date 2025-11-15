import os
from pathlib import Path

# Permitir que Django use PyMySQL como MySQLdb
try:
    import pymysql  # type: ignore
    pymysql.install_as_MySQLdb()
except Exception:
    # PyMySQL pode não estar instalado ainda durante algumas execuções
    pass

# Minimal settings for local development
BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret')
DEBUG = True
ALLOWED_HOSTS = ['*']

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # local apps (use package path so imports work when running from project root)
    'apps.clientes',
    'apps.funcionarios',
    'apps.fornecedores',
    'apps.produtos',
    'apps.estoque',
    'apps.vendas',
    'apps.dashboard',
    'apps.usuarios',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'sistema_pdv.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
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

WSGI_APPLICATION = 'sistema_pdv.wsgi.application'
ASGI_APPLICATION = 'sistema_pdv.asgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'sistema_pdv',
        'USER': 'user',
        'PASSWORD': 'userpass',
        'HOST': '127.0.0.1',  # acessando MySQL do Docker via host
        'PORT': '3307',       # porta mapeada no docker-compose
        'OPTIONS': {
            'charset': 'utf8mb4',
        },
    }
}

AUTH_PASSWORD_VALIDATORS = []

LANGUAGE_CODE = 'pt-br'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']

# Opcional: evita warnings de AutoField
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
