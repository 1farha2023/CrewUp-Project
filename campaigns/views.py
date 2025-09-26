
from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator
from .models import Campaign

def campaign_list(request):
    # Get all campaigns
    campaign_list = Campaign.objects.all().order_by('-created_at')
    
    # Get filter parameters
    category = request.GET.get('category')
    budget = request.GET.get('budget')
    platform = request.GET.get('platform')
    search = request.GET.get('search')
    
    # Apply filters
    if category:
        campaign_list = campaign_list.filter(category=category)
    if platform:
        campaign_list = campaign_list.filter(platform=platform)
    if search:
        campaign_list = campaign_list.filter(title__icontains=search)
    
    # Pagination
    paginator = Paginator(campaign_list, 9)  # Show 9 campaigns per page
    page = request.GET.get('page')
    campaigns = paginator.get_page(page)
    
    return render(request, 'campaigns/campaigns.html', {'campaigns': campaigns})

def campaign_detail(request, campaign_id):
    campaign = get_object_or_404(Campaign, id=campaign_id)
    return render(request, 'campaigns/campaign_detail.html', {'campaign': campaign})
