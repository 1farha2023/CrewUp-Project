from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    class Role(models.TextChoices):
        ADMIN = 'ADMIN', 'Admin'
        BRAND_OWNER = 'BRAND_OWNER', 'Brand Owner'
        INFLUENCER = 'INFLUENCER', 'Influencer'

    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.INFLUENCER
    )

    def __str__(self):
        return f"{self.email} ({self.get_role_display()})"
