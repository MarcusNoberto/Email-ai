import os
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# ===============================
#  Segurança / Ambiente
# ===============================

# Em produção (Render) você seta SECRET_KEY via variável de ambiente.
# Em dev (local) ele usa esse fallback.
SECRET_KEY = os.environ.get(
    "SECRET_KEY",
    "django-insecure-dev-chave-apenas-para-uso-local"
)

# DEBUG: em produção, defina DEBUG=False nas env vars
DEBUG = os.environ.get("DEBUG", "True") == "True"

# ALLOWED_HOSTS: no Render você pode deixar "*" ou informar o host.
# Ex.: ALLOWED_HOSTS="email-ai.onrender.com"
ALLOWED_HOSTS = os.environ.get("ALLOWED_HOSTS", "*").split(",")


# ===============================
#  Aplicações
# ===============================

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'core',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    # Whitenoise para servir arquivos estáticos em produção (Render)
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'email_ai.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],  # se quiser pastas de templates globais, coloca aqui
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

WSGI_APPLICATION = 'email_ai.wsgi.application'


# ===============================
#  Banco de Dados
# ===============================

# Para o desafio, SQLite está ok (mesmo no Render).
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}


# ===============================
#  Validação de Senha
# ===============================

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


# ===============================
#  Internacionalização
# ===============================

LANGUAGE_CODE = 'pt-br'
TIME_ZONE = 'America/Sao_Paulo'

USE_I18N = True
USE_TZ = True


# ===============================
#  Arquivos estáticos e mídia
# ===============================

# Arquivos enviados (não é o foco aqui, mas já deixo pronto)
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# URL pública dos estáticos
STATIC_URL = '/static/'

# Onde o collectstatic vai jogar os arquivos pra produção (Render)
STATIC_ROOT = BASE_DIR / 'staticfiles'

# Pasta de estáticos locais (CSS/JS/imagens do projeto)
STATICFILES_DIRS = [
    BASE_DIR / 'static',
]

# Whitenoise storage para compressão e cache busting
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"


# ===============================
#  Default primary key
# ===============================

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
