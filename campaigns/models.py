from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class Campaign(models.Model):
    CATEGORY_CHOICES = [
        ('fashion', 'Fashion & Beauty'),
        ('tech', 'Technology'),
        ('food', 'Food & Beverage'),
        ('lifestyle', 'Lifestyle'),
        ('travel', 'Travel'),
    ]
    
    PLATFORM_CHOICES = [
        ('instagram', 'Instagram'),
        ('youtube', 'YouTube'),
        ('tiktok', 'TikTok'),
        ('twitter', 'Twitter'),
    ]

    title = models.CharField(max_length=200)
    description = models.TextField()
    image = models.ImageField(upload_to='campaign_images/', null=True, blank=True)
    budget = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    platform = models.CharField(max_length=50, choices=PLATFORM_CHOICES)
    influencers = models.ManyToManyField(User, related_name='campaigns', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.title
    
    class Meta:
        ordering = ['-created_at']
