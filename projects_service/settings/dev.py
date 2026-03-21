from .base import *
import os

DEBUG = True
ALLOWED_HOSTS = ["*"]

CORS_ALLOW_ALL_ORIGINS = True

# Override DB with compose-provided values for dev
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.environ.get("DB_NAME", "devdb"),
        "USER": os.environ.get("DB_USER", "devuser"),
        "PASSWORD": os.environ.get("DB_PASSWORD", "devpass"),
        "HOST": os.environ.get("DB_HOST", "db").strip(),
        "PORT": os.environ.get("DB_PORT", "5432").strip(),
    }
}

# Use DATABASE_URL if provided (overrides individual vars)
_db_url = os.environ.get("DATABASE_URL", "")
if _db_url:
    import dj_database_url
    DATABASES["default"] = dj_database_url.parse(_db_url)

# Use custom JWT-middleware-aware authentication for DRF
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "projects_service.core.authentication.JWTMiddlewareAuthentication",
    ],
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticated",
    ],
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": 25,
    "DEFAULT_RENDERER_CLASSES": ["rest_framework.renderers.JSONRenderer"],
}

