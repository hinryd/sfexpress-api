import os
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

User = get_user_model()


class Command(BaseCommand):
    help = 'Creates or updates admin user with password from environment variables'

    def handle(self, *args, **options):
        admin_password = os.environ.get('DJANGO_ADMIN_PASSWORD')
        admin_email = os.environ.get('DJANGO_ADMIN_EMAIL', 'admin@example.com')

        if not admin_password:
            self.stdout.write(self.style.WARNING('DJANGO_ADMIN_PASSWORD not set, skipping admin setup'))
            return

        try:
            admin_user = User.objects.get(username='admin')
            admin_user.set_password(admin_password)
            admin_user.email = admin_email
            admin_user.is_superuser = True
            admin_user.is_staff = True
            admin_user.save()
            self.stdout.write(self.style.SUCCESS('Admin user updated successfully'))
        except User.DoesNotExist:
            admin_user = User.objects.create_superuser(
                username='admin',
                email=admin_email,
                password=admin_password
            )
            self.stdout.write(self.style.SUCCESS('Admin user created successfully'))
