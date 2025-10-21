from django.contrib import admin
from .models import Campaign, CampaignApplication, InfluencerAnalytics, CustomOffer

@admin.register(Campaign)
class CampaignAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'platform', 'budget', 'created_at')
    list_filter = ('category', 'platform', 'created_at')
    search_fields = ('title', 'description')
    readonly_fields = ('created_at', 'updated_at')

@admin.register(CampaignApplication)
class CampaignApplicationAdmin(admin.ModelAdmin):
    list_display = ('campaign', 'influencer', 'status', 'applied_at')
    list_filter = ('status', 'applied_at')
    search_fields = ('campaign__title', 'influencer__username')
    readonly_fields = ('applied_at', 'updated_at')

@admin.register(InfluencerAnalytics)
class InfluencerAnalyticsAdmin(admin.ModelAdmin):
    list_display = ('influencer', 'total_applications', 'approved_applications', 'total_earnings', 'profile_views')
    search_fields = ('influencer__username',)
    readonly_fields = ('last_updated',)

@admin.register(CustomOffer)
class CustomOfferAdmin(admin.ModelAdmin):
    list_display = ('title', 'brand', 'influencer', 'offer_amount', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('title', 'brand__username', 'influencer__username')
    readonly_fields = ('created_at', 'updated_at')
