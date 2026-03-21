from django.apps import AppConfig


class CoreConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "projects_service.core"
    label = "projects_core"
    verbose_name = "Core (base models, utils, services)"
