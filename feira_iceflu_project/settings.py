# feira_iceflu_project/settings.py

import os
from pathlib import Path

# --- Configuração Base ---
BASE_DIR = Path(__file__).resolve().parent.parent


# --- Configurações de Segurança e Deploy ---

SECRET_KEY = os.environ.get('SECRET_KEY', 'django-insecure-fallback-key-for-local-dev-only')

DEBUG = 'K_SERVICE' not in os.environ

# --- Bloco de Configuração de Produção Explícito ---
if 'K_SERVICE' in os.environ:
    # Use a sua URL exata aqui
    SERVICE_URL = 'feira-iceflu-web-763346611327.southamerica-east1.run.app'
    
    ALLOWED_HOSTS = [SERVICE_URL]
    
    # Define as origens confiáveis para a URL exata.
    CSRF_TRUSTED_ORIGINS = [f'https://{SERVICE_URL}']
    
    # Informa ao Django para confiar no cabeçalho do proxy do Google.
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
    
    # Garante que os cookies só sejam enviados via HTTPS.
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    # Instrui o navegador a enviar o cookie CSRF em todos os contextos.
    # Requer que CSRF_COOKIE_SECURE seja True.
    CSRF_COOKIE_SAMESITE = 'None'
    
else:
    # --- Configurações para Desenvolvimento Local ---
    ALLOWED_HOSTS = ['127.0.0.1', 'localhost']


# --- Definições da Aplicação ---
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'feira_app.apps.FeiraAppConfig',
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

ROOT_URLCONF = 'feira_iceflu_project.urls'

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

WSGI_APPLICATION = 'feira_iceflu_project.wsgi.application'


# --- Configuração do Banco de Dados ---
if 'K_SERVICE' in os.environ:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'HOST': f"/cloudsql/{os.environ.get('INSTANCE_CONNECTION_NAME')}",
            'USER': os.environ.get('DB_USER', 'postgres'),
            'PASSWORD': os.environ.get('DB_PASSWORD'),
            'NAME': os.environ.get('DB_NAME', 'postgres'),
        }
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }


# --- Validação de Senhas ---
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]


# --- Autenticação e URLs de Login ---
LOGIN_URL = '/login/'
LOGIN_REDIRECT_URL = '/produtos/'


# --- Internacionalização ---
LANGUAGE_CODE = 'pt-br'
TIME_ZONE = 'America/Sao_Paulo'
USE_I18N = True
USE_TZ = True


# --- Arquivos Estáticos ---
STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'


# --- Chave Primária Padrão ---
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'