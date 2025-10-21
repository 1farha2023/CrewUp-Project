
from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    USER_TYPE_CHOICES = [
        ('brand', 'Brand'),
        ('influencer', 'Influencer'),
        ('admin', 'Admin'),
    ]

    user_type = models.CharField(max_length=10, choices=USER_TYPE_CHOICES, default='influencer')

    # Profile fields
    bio = models.TextField(max_length=500, blank=True, null=True)
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, null=True)
    company_name = models.CharField(max_length=100, blank=True, null=True)
    website = models.URLField(blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    location = models.CharField(max_length=100, blank=True, null=True)

    # Brand-specific fields
    industry = models.CharField(max_length=100, blank=True, null=True)
    brand_size = models.CharField(
        max_length=50,
        choices=[
            ('startup', 'Startup'),
            ('small', 'Small Business'),
            ('medium', 'Medium Business'),
            ('large', 'Large Corporation'),
        ],
        blank=True,
        null=True,
    )

    # Influencer-specific fields
    niche = models.CharField(max_length=100, blank=True, null=True)
    instagram_handle = models.CharField(max_length=100, blank=True, null=True)
    youtube_channel = models.CharField(max_length=200, blank=True, null=True)
    tiktok_handle = models.CharField(max_length=100, blank=True, null=True)
    followers_count = models.IntegerField(blank=True, null=True)

    # Admin fields
    is_banned = models.BooleanField(default=False)
    banned_at = models.DateTimeField(blank=True, null=True)
    banned_reason = models.TextField(blank=True, null=True)
    banned_by = models.ForeignKey('self', on_delete=models.SET_NULL, blank=True, null=True, related_name='banned_users')

    def __str__(self):
        return self.username

    class Meta:
        # Consider adding a database-level unique constraint on email to prevent duplicates.
        # To enforce this, run makemigrations/migrate after ensuring existing data is cleaned.
        # Uncomment the UniqueConstraint below and run migrations if you want DB-level enforcement.
        #
        # constraints = [
        #     models.UniqueConstraint(fields=['email'], name='unique_email')
        # ]
        pass

