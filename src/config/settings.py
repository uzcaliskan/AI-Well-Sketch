import os
from pathlib import Path

from django.core.exceptions import ImproperlyConfigured

BASE_DIR = Path(__file__).resolve().parent.parent
PROJECT_ROOT = BASE_DIR.parent

DEBUG = os.environ.get("DJANGO_DEBUG", "1") == "1"

SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY")
if not SECRET_KEY:
    if not DEBUG:
        raise ImproperlyConfigured("DJANGO_SECRET_KEY ortam değişkeni gerekli.")
    SECRET_KEY = "yalnizca-gelistirme-icin"

ALLOWED_HOSTS = os.environ.get("DJANGO_ALLOWED_HOSTS", "localhost,127.0.0.1").split(",")

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "apps.wells",
    "apps.reports",
    "apps.proposals",
    "apps.photos",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"

# Başlangıç: SQLite (kararlar.md K-12). Ölçekte PostgreSQL değerlendirilecek.
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": os.environ.get("DJANGO_DB_PATH", BASE_DIR / "db.sqlite3"),
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LANGUAGE_CODE = "tr"
TIME_ZONE = "Europe/Istanbul"
USE_I18N = True
USE_TZ = True

STATIC_URL = "static/"
MEDIA_URL = "media/"
MEDIA_ROOT = PROJECT_ROOT / "media"

LOGIN_URL = "login"
LOGIN_REDIRECT_URL = "well_list"
LOGOUT_REDIRECT_URL = "login"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# vLLM (kararlar.md K-04): şirket içi, OpenAI uyumlu uç nokta. Hiçbir veri dış servise gönderilmez.
# Örn. VLLM_BASE_URL=http://10.0.0.5:8000/v1 ; VLLM_MODEL sunucudaki servis edilen model adıdır.
VLLM_BASE_URL = os.environ.get("VLLM_BASE_URL", "")
VLLM_MODEL = os.environ.get("VLLM_MODEL", "")
VLLM_API_KEY = os.environ.get("VLLM_API_KEY", "")
VLLM_MAX_TOKENS = int(os.environ.get("VLLM_MAX_TOKENS", "4096"))
VLLM_TIMEOUT = float(os.environ.get("VLLM_TIMEOUT", "300"))
# IP olmayan (alan adlı) şirket içi sunucu adları, virgülle ayrılmış. Örn. vllm.sirket.local
VLLM_IZINLI_HOSTLAR = [h.strip().lower() for h in os.environ.get("VLLM_IZINLI_HOSTLAR", "").split(",") if h.strip()]
MAX_RAPOR_KARAKTER = int(os.environ.get("MAX_RAPOR_KARAKTER", "300000"))

KURAL_TABANI_YOLU = PROJECT_ROOT / "context" / "kuyu-tasarim-kurallari.md"
