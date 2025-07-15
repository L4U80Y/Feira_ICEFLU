# feira_iceflu_project/settings_prod.py
# Este arquivo contém APENAS configurações de produção.

from .settings import * # Importa todas as configurações do settings.py base
import os
from decimal import Decimal

# --- SOBRESCREVENDO CONFIGURAÇÕES PARA PRODUÇÃO ---

# Segurança (explícita para produção)
DEBUG = False
SECRET_KEY = os.environ.get('SECRET_KEY')
ALLOWED_HOSTS = ['feira-iceflu-web-763346611327.southamerica-east1.run.app']

# Configurações de CSRF e Proxy (explícitas)
CSRF_TRUSTED_ORIGINS = ['https://feira-iceflu-web-763346611327.southamerica-east1.run.app']
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
CSRF_COOKIE_SAMESITE = 'None'
CSRF_USE_SESSIONS = True

# Banco de Dados (explícito para produção)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'HOST': f"/cloudsql/{os.environ.get('INSTANCE_CONNECTION_NAME')}",
        'USER': os.environ.get('DB_USER'),
        'PASSWORD': os.environ.get('DB_PASSWORD'),
        'NAME': os.environ.get('DB_NAME'),
    }
}

# MIDDLEWARE (com WhiteNoise e middleware de debug removidos para teste)
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    # 'whitenoise.middleware.WhiteNoiseMiddleware', # Removido temporariamente
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# Arquivos Estáticos (WhiteNoise storage desabilitado temporariamente)
STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.StaticFilesStorage'