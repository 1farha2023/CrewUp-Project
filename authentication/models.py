from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    user_type = models.CharField(max_length=10, choices=[('brand', 'Brand'), ('influencer', 'Influencer')], default='influencer')

    def __str__(self):
        return self.username