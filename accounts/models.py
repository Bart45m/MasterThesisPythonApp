from django.db import models

# Create your models here.
from django.db import models

class Users(models.Model):
    id = models.BigAutoField(primary_key=True)
    email = models.CharField(max_length=255, unique=True)
    password_hash = models.CharField(max_length=255)
    role = models.CharField(max_length=255, default='USER')
    reset_token = models.CharField(max_length=255, blank=True, null=True)

    # Informujemy wewnętrzne mechanizmy autoryzacji Django, że to nasza encja biznesowa
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

# Wymagane właściwości interfejsu użytkownika dla kompatybilności z DRF i SimpleJWT
    @property
    def is_active(self):
        return True

    @property
    def is_anonymous(self):
        return False

    @property
    def is_authenticated(self):
        return True

    @property
    def is_staff(self):
        return self.role == 'ADMIN'  # lub True, zależnie od logiki

    class Meta:
        managed = True
        db_table = 'users'
        
    def __str__(self):
        return self.email