from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from authentication.models import CustomUser
from campaigns.models import Campaign




def index(request):
    # Fetch featured users (mix of brands and influencers)
    featured_users = CustomUser.objects.filter(
        user_type__in=['brand', 'influencer']
    ).exclude(
        user_type='admin'
    )[:8]  # Limit to 8 featured users

    # Fetch Instagram users
    instagram_users = CustomUser.objects.filter(
        user_type='influencer',
        instagram_handle__isnull=False
    ).exclude(
        instagram_handle=''
    )[:6]

    # Fetch TikTok users
    tiktok_users = CustomUser.objects.filter(
        user_type='influencer',
        tiktok_handle__isnull=False
    ).exclude(
        tiktok_handle=''
    )[:6]

    # Get category choices from Campaign model
    category_choices = Campaign.CATEGORY_CHOICES

    # Get platform choices from Campaign model
    platform_choices = Campaign.PLATFORM_CHOICES

    context = {
        'featured_users': featured_users,
        'instagram_users': instagram_users,
        'tiktok_users': tiktok_users,
        'categories': category_choices,
        'platforms': platform_choices,
    }

    return render(request, 'index.html', context)

def about(request):
    return render(request, 'about.html')

def how_it_works(request):
    return render(request, 'how-it-works.html')

def campaign_list(request):
    return render(request, 'Campaignlist.html')

def pricing(request):
    return render(request, 'pricing.html')

def landing_page(request):
    return render(request, 'index.html')

@login_required
def admin_dashboard(request):
    if request.user.user_type != 'admin':
        messages.error(request, 'Only admin users can access this page.')
        return redirect('home')
    return render(request, 'admin/dashboard.html')

@login_required
def influencer_dashboard(request):
    if request.user.user_type != 'influencer':
        messages.error(request, 'Only influencer users can access this page.')
        return redirect('home')
    return render(request, 'Profiles/influencer dashboard.html')

@login_required
def brand_dashboard(request):
    if request.user.user_type != 'brand':
        messages.error(request, 'Only brand users can access this page.')
        return redirect('home')

    # Calculate total budget for all campaigns created by this brand
    total_budget = sum(campaign.budget for campaign in request.user.created_campaigns.all())

    context = {
        'total_budget': total_budget,
    }
    return render(request, 'Profiles/brand dashboard.html', context)

