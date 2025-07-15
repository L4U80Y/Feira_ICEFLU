# feira_iceflu_project/settings.py

import os
from pathlib import Path

# --- Configuração Base ---
# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# --- Configurações de Segurança e Deploy ---

# CHAVE SECRETA: Lida da variável de ambiente em produção.
# O valor de fallback é APENAS para desenvolvimento local e não deve ser usado em produção.
SECRET_KEY = os.environ.get('SECRET_KEY', 'django-insecure-fallback-key-for-local-dev-only')

# MODO DEBUG: Desligado automaticamente em produção no Google Cloud.
# 'K_SERVICE' é uma variável de ambiente que o Google Cloud Run define.
# Se ela existir, DEBUG será False. Caso contrário (localmente), será True.
DEBUG = 'K_SERVICE' not in os.environ

# HOSTS PERMITIDOS E CONFIGURAÇÕES DE PROXY SEGURO
ALLOWED_HOSTS = []

if 'K_SERVICE' in os.environ:
    # --- Configurações para Produção no Google Cloud Run ---
    
    # Permite acesso a partir do domínio principal do serviço no Cloud Run.
    ALLOWED_HOSTS.append('.run.app')
    
    # Informa ao Django para confiar na conexão segura feita pelo proxy do Google.
    # Essencial para CSRF, redirects e cookies funcionarem corretamente com HTTPS.
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'httpss') # AQUI ESTAVA A CORREÇÃO FALTANTE
    
    # Garante que os cookies de sessão e CSRF só sejam enviados via HTTPS.
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    
    # Define as origens (domínios) confiáveis para requisições que modificam dados (POST).
    CSRF_TRUSTED_ORIGINS = ['https://*.run.app']
    
else:
    # --- Configurações para Desenvolvimento Local ---
    ALLOWED_HOSTS.extend(['127.0.0.1', 'localhost'])


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
# Alterna entre produção (Cloud SQL) e desenvolvimento (SQLite).
if 'K_SERVICE' in os.environ:
    # Configuração para produção (lendo de variáveis de ambiente)
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
    # Configuração para desenvolvimento local
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