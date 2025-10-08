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

def success_stories(request):
    return render(request, 'success-stories.html')

def landing_page(request):
    return render(request, 'index.html')

def influencers(request):
    # Fetch all influencers with their profile information
    influencers_list = CustomUser.objects.filter(
        user_type='influencer'
    ).exclude(
        user_type='admin'
    ).select_related().order_by('-followers_count')

    # Get filter parameters
    niche_filter = request.GET.get('niche', '')
    platform_filter = request.GET.get('platform', '')
    search_query = request.GET.get('search', '')

    # Apply filters if provided
    if niche_filter and niche_filter != 'all':
        influencers_list = influencers_list.filter(niche__icontains=niche_filter)

    if platform_filter and platform_filter != 'all':
        if platform_filter.lower() == 'instagram':
            influencers_list = influencers_list.exclude(instagram_handle='')
        elif platform_filter.lower() == 'tiktok':
            influencers_list = influencers_list.exclude(tiktok_handle='')
        elif platform_filter.lower() == 'youtube':
            influencers_list = influencers_list.exclude(youtube_handle='')

    if search_query:
        influencers_list = influencers_list.filter(
            Q(username__icontains=search_query) |
            Q(niche__icontains=search_query) |
            Q(location__icontains=search_query)
        )

    # Get unique niches for filter sidebar
    niches = CustomUser.objects.filter(
        user_type='influencer',
        niche__isnull=False
    ).exclude(
        niche=''
    ).values_list('niche', flat=True).distinct()

    context = {
        'influencers': influencers_list,
        'niches': niches,
        'current_niche': niche_filter,
        'current_platform': platform_filter,
        'search_query': search_query,
    }

    return render(request, 'influencers.html', context)

def brands(request):
    # Fetch all brands with their profile information
    brands_list = CustomUser.objects.filter(
        user_type='brand'
    ).exclude(
        user_type='admin'
    ).select_related().order_by('-date_joined')

    # Get filter parameters
    industry_filter = request.GET.get('industry', '')
    size_filter = request.GET.get('size', '')
    search_query = request.GET.get('search', '')

    # Apply filters if provided
    if industry_filter and industry_filter != 'all':
        brands_list = brands_list.filter(industry__icontains=industry_filter)

    if size_filter and size_filter != 'all':
        brands_list = brands_list.filter(brand_size=size_filter)

    if search_query:
        brands_list = brands_list.filter(
            Q(username__icontains=search_query) |
            Q(company_name__icontains=search_query) |
            Q(industry__icontains=search_query) |
            Q(location__icontains=search_query)
        )

    # Get unique industries for filter sidebar
    industries = CustomUser.objects.filter(
        user_type='brand',
        industry__isnull=False
    ).exclude(
        industry=''
    ).values_list('industry', flat=True).distinct()

    # Get unique brand sizes for filter sidebar
    brand_sizes = CustomUser.objects.filter(
        user_type='brand',
        brand_size__isnull=False
    ).exclude(
        brand_size=''
    ).values_list('brand_size', flat=True).distinct()

    context = {
        'brands': brands_list,
        'industries': industries,
        'brand_sizes': brand_sizes,
        'current_industry': industry_filter,
        'current_size': size_filter,
        'search_query': search_query,
    }

    return render(request, 'brands.html', context)

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

def influencer_profile(request, influencer_id):
    """Display individual influencer profile with packages and pricing"""
    try:
        # Get the influencer by ID
        influencer = CustomUser.objects.get(id=influencer_id, user_type='influencer')

        context = {
            'influencer': influencer,
        }

        return render(request, 'influencer_profile.html', context)

    except CustomUser.DoesNotExist:
        messages.error(request, 'Influencer not found.')
        return redirect('influencers')

