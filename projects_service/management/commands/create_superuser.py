from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.conf import settings


class Command(BaseCommand):
    help = "Create default superuser if not exists"

    def handle(self, *args, **options):
        User = get_user_model()
        email = settings.SUPERUSER_EMAIL
        password = settings.SUPERUSER_PASSWORD
        if not User.objects.filter(email=email).exists():
            User.objects.create_superuser(username=email.split("@")[0], email=email, password=password)
            self.stdout.write(self.style.SUCCESS(f"Superuser {email} created."))
        else:
            self.stdout.write(f"Superuser {email} already exists.")
