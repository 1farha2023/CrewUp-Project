
from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from .models import Campaign, CampaignApplication, InfluencerAnalytics, CustomOffer
from .forms import CampaignForm, CampaignApplicationForm, CustomOfferForm
from authentication.models import CustomUser

def campaign_list(request):
    # Get all campaigns
    campaign_list = Campaign.objects.all().order_by('-created_at')

    # Get filter parameters
    category = request.GET.get('category')
    budget_range = request.GET.get('budget')
    platform = request.GET.get('platform')
    search = request.GET.get('search')

    # Apply filters
    if category:
        campaign_list = campaign_list.filter(category=category)

    if platform:
        campaign_list = campaign_list.filter(platform=platform)

    if search:
        campaign_list = campaign_list.filter(title__icontains=search)

    # Apply budget range filtering
    if budget_range:
        if budget_range == '0-500':
            campaign_list = campaign_list.filter(budget__lte=500)
        elif budget_range == '501-1000':
            campaign_list = campaign_list.filter(budget__gte=501, budget__lte=1000)
        elif budget_range == '1001-5000':
            campaign_list = campaign_list.filter(budget__gte=1001, budget__lte=5000)
        elif budget_range == '5001+':
            campaign_list = campaign_list.filter(budget__gte=5001)

    # Pagination
    paginator = Paginator(campaign_list, 9)  # Show 9 campaigns per page
    page = request.GET.get('page')
    campaigns = paginator.get_page(page)

    # Get filter options for template
    context = {
        'campaigns': campaigns,
        'selected_category': category or '',
        'selected_budget': budget_range or '',
        'selected_platform': platform or '',
        'search_query': search or '',
    }

    # Add current query parameters for pagination
    current_params = request.GET.copy()
    context['current_params'] = current_params

    return render(request, 'campaigns/campaigns.html', context)

def campaign_detail(request, campaign_id):
    campaign = get_object_or_404(Campaign, id=campaign_id)
    return render(request, 'campaigns/campaign_detail.html', {'campaign': campaign})

@login_required
def campaign_create(request):
    # Only brands can create campaigns
    if request.user.user_type != 'brand':
        messages.error(request, 'Only brand users can create campaigns.')
        return redirect('campaigns:campaign_list')

    if request.method == 'POST':
        form = CampaignForm(request.POST, request.FILES)
        if form.is_valid():
            campaign = form.save(commit=False)
            campaign.creator = request.user  # Set the creator to the current user
            campaign.save()
            form.save_m2m()  # Save many-to-many relationships
            return redirect('campaigns:campaign_detail', campaign_id=campaign.id)
    else:
        form = CampaignForm()
    return render(request, 'campaigns/campaign_form.html', {'form': form})

@login_required
def campaign_update(request, campaign_id):
    campaign = get_object_or_404(Campaign, id=campaign_id)

    # Only the creator brand or admin can edit campaigns
    if request.user.user_type not in ['brand', 'admin']:
        messages.error(request, 'Only brand users can edit campaigns.')
        return redirect('campaigns:campaign_detail', campaign_id=campaign.id)

    # If user is a brand, check if they are the creator
    if request.user.user_type == 'brand' and campaign.creator != request.user:
        messages.error(request, 'You can only edit your own campaigns.')
        return redirect('campaigns:campaign_detail', campaign_id=campaign.id)

    if request.method == 'POST':
        form = CampaignForm(request.POST, request.FILES, instance=campaign)
        if form.is_valid():
            form.save()
            return redirect('campaigns:campaign_detail', campaign_id=campaign.id)
    else:
        form = CampaignForm(instance=campaign)
    return render(request, 'campaigns/campaign_edit.html', {'form': form, 'campaign': campaign})

@login_required
def campaign_delete(request, campaign_id):
    campaign = get_object_or_404(Campaign, id=campaign_id)

    # Only the creator brand or admin users can delete campaigns
    if request.user.user_type not in ['brand', 'admin']:
        messages.error(request, 'Only brand users or admins can delete campaigns.')
        return redirect('campaigns:campaign_detail', campaign_id=campaign.id)

    # If user is a brand, check if they are the creator
    if request.user.user_type == 'brand' and campaign.creator != request.user:
        messages.error(request, 'You can only delete your own campaigns.')
        return redirect('campaigns:campaign_detail', campaign_id=campaign.id)

    if request.method == 'POST':
        campaign.delete()
        messages.success(request, 'Campaign deleted successfully!')
        return redirect('campaigns:campaign_list')
    return render(request, 'campaigns/campaign_detail.html', {'campaign': campaign})

# Influencer-specific views
@login_required
def apply_to_campaign(request, campaign_id):
    """Allow influencers to apply to campaigns"""
    campaign = get_object_or_404(Campaign, id=campaign_id)

    # Only influencers can apply to campaigns
    if request.user.user_type != 'influencer':
        messages.error(request, 'Only influencer users can apply to campaigns.')
        return redirect('campaigns:campaign_detail', campaign_id=campaign.id)

    # Check if already applied
    if CampaignApplication.objects.filter(campaign=campaign, influencer=request.user).exists():
        messages.warning(request, 'You have already applied to this campaign.')
        return redirect('campaigns:campaign_detail', campaign_id=campaign.id)

    if request.method == 'POST':
        form = CampaignApplicationForm(request.POST)
        if form.is_valid():
            try:
                application = form.save(commit=False)
                application.campaign = campaign
                application.influencer = request.user
                application.save()

                # Add influencer to campaign's influencers list
                campaign.influencers.add(request.user)

                # Update analytics
                analytics, created = InfluencerAnalytics.objects.get_or_create(
                    influencer=request.user,
                    defaults={'total_applications': 0, 'approved_applications': 0, 'total_earnings': 0, 'profile_views': 0}
                )
                analytics.total_applications += 1
                analytics.save()

                return redirect('campaigns:campaign_detail', campaign_id=campaign.id)
            except IntegrityError:
                messages.warning(request, 'You have already applied to this campaign.')
                return redirect('campaigns:campaign_detail', campaign_id=campaign.id)
    else:
        form = CampaignApplicationForm()

    return render(request, 'campaigns/apply_to_campaign.html', {'form': form, 'campaign': campaign})

@login_required
def my_applications(request):
    """Show influencer's campaign applications"""
    if request.user.user_type != 'influencer':
        messages.error(request, 'Only influencer users can view applications.')
        return redirect('home')

    applications = CampaignApplication.objects.filter(influencer=request.user).order_by('-applied_at')
    return render(request, 'campaigns/my_applications.html', {'applications': applications})

@login_required
def influencer_analytics(request):
    """Show influencer's analytics dashboard"""
    if request.user.user_type != 'influencer':
        messages.error(request, 'Only influencer users can view analytics.')
        return redirect('home')

    analytics, created = InfluencerAnalytics.objects.get_or_create(
        influencer=request.user,
        defaults={'total_applications': 0, 'approved_applications': 0, 'total_earnings': 0, 'profile_views': 0}
    )

    # Get recent applications
    recent_applications = CampaignApplication.objects.filter(influencer=request.user).order_by('-applied_at')[:5]

    context = {
        'analytics': analytics,
        'recent_applications': recent_applications,
    }
    return render(request, 'campaigns/influencer_analytics.html', context)

@login_required
def approve_application(request, application_id):
    """Allow brand users to approve influencer applications"""
    application = get_object_or_404(CampaignApplication, id=application_id)

    # Only the campaign creator or admin can approve applications
    if request.user.user_type not in ['brand', 'admin']:
        messages.error(request, 'Only brand users or admins can approve applications.')
        return redirect('campaigns:campaign_detail', campaign_id=application.campaign.id)

    # If user is a brand, check if they are the campaign creator
    if request.user.user_type == 'brand' and application.campaign.creator != request.user:
        messages.error(request, 'You can only approve applications for your own campaigns.')
        return redirect('campaigns:campaign_detail', campaign_id=application.campaign.id)

    if request.method == 'POST':
        application.status = 'approved'
        application.save()

        # Update influencer analytics
        analytics, created = InfluencerAnalytics.objects.get_or_create(
            influencer=application.influencer,
            defaults={'total_applications': 0, 'approved_applications': 0, 'total_earnings': 0, 'profile_views': 0}
        )
        analytics.approved_applications += 1
        analytics.save()

        messages.success(request, f'Application from {application.influencer.username} has been approved!')

    return redirect('campaigns:campaign_detail', campaign_id=application.campaign.id)

@login_required
def reject_application(request, application_id):
    """Allow brand users to reject influencer applications"""
    application = get_object_or_404(CampaignApplication, id=application_id)

    # Only the campaign creator or admin can reject applications
    if request.user.user_type not in ['brand', 'admin']:
        messages.error(request, 'Only brand users or admins can reject applications.')
        return redirect('campaigns:campaign_detail', campaign_id=application.campaign.id)

    # If user is a brand, check if they are the campaign creator
    if request.user.user_type == 'brand' and application.campaign.creator != request.user:
        messages.error(request, 'You can only reject applications for your own campaigns.')
        return redirect('campaigns:campaign_detail', campaign_id=application.campaign.id)

    if request.method == 'POST':
        application.status = 'rejected'
        application.save()

        messages.success(request, f'Application from {application.influencer.username} has been rejected.')

    return redirect('campaigns:campaign_detail', campaign_id=application.campaign.id)

@login_required
def brand_campaign_applications(request, campaign_id):
    """Show all applications for a specific campaign (for brand users)"""
    campaign = get_object_or_404(Campaign, id=campaign_id)

    # Only the campaign creator or admin can view applications
    if request.user.user_type not in ['brand', 'admin']:
        messages.error(request, 'Only brand users or admins can view applications.')
        return redirect('campaigns:campaign_detail', campaign_id=campaign.id)

    # If user is a brand, check if they are the campaign creator
    if request.user.user_type == 'brand' and campaign.creator != request.user:
        messages.error(request, 'You can only view applications for your own campaigns.')
        return redirect('campaigns:campaign_detail', campaign_id=campaign.id)

    applications = CampaignApplication.objects.filter(campaign=campaign).order_by('-applied_at')

    context = {
        'campaign': campaign,
        'applications': applications,
    }
    return render(request, 'campaigns/campaign_applications.html', context)

# Custom Offer Views
@login_required
def send_custom_offer(request, influencer_id):
    """Allow brands to send custom offers to influencers"""
    influencer = get_object_or_404(CustomUser, id=influencer_id, user_type='influencer')
    
    # Only brands can send offers
    if request.user.user_type != 'brand':
        messages.error(request, 'Only brand users can send custom offers.')
        return redirect('home')
    
    if request.method == 'POST':
        form = CustomOfferForm(request.POST)
        if form.is_valid():
            offer = form.save(commit=False)
            offer.brand = request.user
            offer.influencer = influencer
            offer.save()
            return redirect('campaigns:offer_sent_success')
    else:
        # Pre-populate form with brand's campaigns
        form = CustomOfferForm()
        form.fields['campaign'].queryset = Campaign.objects.filter(creator=request.user)
    
    context = {
        'form': form,
        'influencer': influencer,
    }
    return render(request, 'campaigns/send_custom_offer.html', context)

@login_required
def my_offers(request):
    """Show influencer's received offers or brand's sent offers"""
    if request.user.user_type == 'influencer':
        offers = CustomOffer.objects.filter(influencer=request.user).order_by('-created_at')
        template = 'campaigns/influencer_offers.html'
    elif request.user.user_type == 'brand':
        offers = CustomOffer.objects.filter(brand=request.user).order_by('-created_at')
        template = 'campaigns/brand_offers.html'
    else:
        messages.error(request, 'Invalid user type.')
        return redirect('home')
    
    context = {
        'offers': offers,
    }
    return render(request, template, context)

@login_required
def offer_detail(request, offer_id):
    """View details of a custom offer"""
    offer = get_object_or_404(CustomOffer, id=offer_id)
    
    # Only the brand or influencer involved can view the offer
    if request.user not in [offer.brand, offer.influencer]:
        messages.error(request, 'You do not have permission to view this offer.')
        return redirect('home')
    
    context = {
        'offer': offer,
    }
    return render(request, 'campaigns/offer_detail.html', context)

@login_required
def accept_offer(request, offer_id):
    """Allow influencers to accept custom offers"""
    offer = get_object_or_404(CustomOffer, id=offer_id)
    
    # Only the influencer can accept their offer
    if request.user != offer.influencer:
        messages.error(request, 'You do not have permission to accept this offer.')
        return redirect('campaigns:offer_detail', offer_id=offer.id)
    
    # Only pending offers can be accepted
    if offer.status != 'pending':
        messages.error(request, 'This offer has already been processed.')
        return redirect('campaigns:offer_detail', offer_id=offer.id)
    
    if request.method == 'POST':
        offer.status = 'accepted'
        offer.influencer_response = request.POST.get('response', '')
        offer.save()
        
        # Update analytics
        analytics, created = InfluencerAnalytics.objects.get_or_create(
            influencer=request.user,
            defaults={'total_applications': 0, 'approved_applications': 0, 'total_earnings': 0, 'profile_views': 0}
        )
        analytics.total_earnings += offer.offer_amount
        analytics.save()
        
        return redirect('campaigns:offer_detail', offer_id=offer.id)
    
    return redirect('campaigns:offer_detail', offer_id=offer.id)

@login_required
def reject_offer(request, offer_id):
    """Allow influencers to reject custom offers"""
    offer = get_object_or_404(CustomOffer, id=offer_id)
    
    # Only the influencer can reject their offer
    if request.user != offer.influencer:
        messages.error(request, 'You do not have permission to reject this offer.')
        return redirect('campaigns:offer_detail', offer_id=offer.id)
    
    # Only pending offers can be rejected
    if offer.status != 'pending':
        messages.error(request, 'This offer has already been processed.')
        return redirect('campaigns:offer_detail', offer_id=offer.id)
    
    if request.method == 'POST':
        offer.status = 'rejected'
        offer.influencer_response = request.POST.get('response', '')
        offer.save()
        return redirect('campaigns:offer_detail', offer_id=offer.id)
    
    return redirect('campaigns:offer_detail', offer_id=offer.id)

@login_required
def offer_sent_success(request):
    """Success page after sending an offer"""
    return render(request, 'campaigns/offer_sent_success.html')
