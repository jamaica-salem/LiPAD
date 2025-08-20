from django.core.management.base import BaseCommand
from django.contrib.auth.hashers import make_password, identify_hasher
from django.db import transaction
from core.models import User, Admin  

def looks_hashed(pw: str) -> bool:
    if not pw:
        return False
    try:
        identify_hasher(pw)
        return True
    except Exception:
        return False

class Command(BaseCommand):
    help = "Rehash plaintext passwords for Users/Admins that were stored unhashed."

    def handle(self, *args, **options):
        updated_users = 0
        updated_admins = 0

        with transaction.atomic():
            for u in User.objects.all().only('id', 'password'):
                if u.password and not looks_hashed(u.password):
                    u.password = make_password(u.password)
                    u.save(update_fields=['password'])
                    updated_users += 1

            for a in Admin.objects.all().only('id', 'password'):
                if a.password and not looks_hashed(a.password):
                    a.password = make_password(a.password)
                    a.save(update_fields=['password'])
                    updated_admins += 1

        self.stdout.write(self.style.SUCCESS(
            f"Rehashed {updated_users} user(s) and {updated_admins} admin(s)."
        ))
