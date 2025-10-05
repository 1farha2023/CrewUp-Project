
from django.db import models
from django.conf import settings

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
    creator = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='created_campaigns', null=True, blank=True)
    influencers = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='campaigns', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.title

    class Meta:
        ordering = ['-created_at']

class CampaignApplication(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('completed', 'Completed'),
    ]

    campaign = models.ForeignKey(Campaign, on_delete=models.CASCADE, related_name='applications')
    influencer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='campaign_applications')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    application_message = models.TextField(blank=True, null=True)
    applied_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['campaign', 'influencer']
        ordering = ['-applied_at']

    def __str__(self):
        return f"{self.influencer.username} - {self.campaign.title}"

class InfluencerAnalytics(models.Model):
    influencer = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='analytics')
    total_applications = models.IntegerField(default=0)
    approved_applications = models.IntegerField(default=0)
    total_earnings = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    profile_views = models.IntegerField(default=0)
    last_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Analytics for {self.influencer.username}"
