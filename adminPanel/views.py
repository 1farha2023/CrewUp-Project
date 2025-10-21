from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Count, Sum, Q
from django.utils import timezone
from datetime import timedelta
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from authentication.models import CustomUser
from campaigns.models import Campaign, CampaignApplication, CustomOffer
from payments.models import Payment, Subscription
from .models import ContactMessage

def dashboard_view(request):
    # Get total users count
    total_users = CustomUser.objects.count()

    # Get active campaigns (campaigns created in the last 30 days)
    thirty_days_ago = timezone.now() - timedelta(days=30)
    active_campaigns = Campaign.objects.filter(created_at__gte=thirty_days_ago).count()

    # Get brand users count
    brand_users = CustomUser.objects.filter(user_type='brand').count()

    # Get influencer users count
    influencer_users = CustomUser.objects.filter(user_type='influencer').count()

    # Get recent campaigns (last 5)
    recent_campaigns = Campaign.objects.select_related('creator').order_by('-created_at')[:5]

    # Get recent users (last 5)
    recent_users = CustomUser.objects.order_by('-date_joined')[:5]

    # Get total revenue from completed payments
    total_revenue = Payment.objects.filter(status='completed').aggregate(
        total=Sum('amount')
    )['total'] or 0

    # Get active subscriptions count
    active_subscriptions = Subscription.objects.filter(status='active').count()

    # Get pending applications count
    pending_applications = CampaignApplication.objects.filter(status='pending').count()

    # Get total custom offers
    total_offers = CustomOffer.objects.count()

    # Get unread messages count
    unread_messages = ContactMessage.objects.filter(is_read=False).count()

    context = {
        'total_users': total_users,
        'active_campaigns': active_campaigns,
        'brand_users': brand_users,
        'influencer_users': influencer_users,
        'recent_campaigns': recent_campaigns,
        'recent_users': recent_users,
        'total_revenue': total_revenue,
        'active_subscriptions': active_subscriptions,
        'pending_applications': pending_applications,
        'total_offers': total_offers,
        'unread_messages': unread_messages,
    }

    return render(request, 'admin/dashboard.html', context)

@login_required
def ban_user(request, user_id):
    """Ban a user from the platform"""
    if request.user.user_type != 'admin':
        messages.error(request, 'Access denied.')
        return redirect('admin_dashboard')

    user = get_object_or_404(CustomUser, id=user_id)

    if user == request.user:
        messages.error(request, 'You cannot ban yourself.')
        return redirect('admin_dashboard')

    if user.user_type == 'admin':
        messages.error(request, 'You cannot ban another admin.')
        return redirect('admin_dashboard')

    if request.method == 'POST':
        reason = request.POST.get('reason', '').strip()
        user.is_banned = True
        user.banned_at = timezone.now()
        user.banned_reason = reason
        user.banned_by = request.user
        user.is_active = False  # Deactivate the user
        user.save()

        messages.success(request, f'User {user.username} has been banned successfully.')
        return redirect('admin_dashboard')

    context = {
        'user_to_ban': user,
    }
    return render(request, 'admin/ban_user.html', context)

@login_required
def unban_user(request, user_id):
    """Unban a user from the platform"""
    if request.user.user_type != 'admin':
        messages.error(request, 'Access denied.')
        return redirect('admin_dashboard')

    user = get_object_or_404(CustomUser, id=user_id)

    if not user.is_banned:
        messages.warning(request, 'User is not banned.')
        return redirect('admin_dashboard')

    if request.method == 'POST':
        user.is_banned = False
        user.banned_at = None
        user.banned_reason = None
        user.banned_by = None
        user.is_active = True  # Reactivate the user
        user.save()

        messages.success(request, f'User {user.username} has been unbanned successfully.')
        return redirect('admin_dashboard')

    context = {
        'user_to_unban': user,
    }
    return render(request, 'admin/unban_user.html', context)

@login_required
def user_management(request):
    """Comprehensive user management page for admins"""
    if request.user.user_type != 'admin':
        messages.error(request, 'Access denied.')
        return redirect('admin_dashboard')

    # Get filter parameters
    search_query = request.GET.get('search', '')
    user_type_filter = request.GET.get('user_type', '')
    status_filter = request.GET.get('status', '')
    page_number = request.GET.get('page', 1)

    # Base queryset
    users = CustomUser.objects.all().select_related()

    # Apply filters
    if search_query:
        users = users.filter(
            Q(username__icontains=search_query) |
            Q(email__icontains=search_query) |
            Q(first_name__icontains=search_query) |
            Q(last_name__icontains=search_query)
        )

    if user_type_filter and user_type_filter != 'all':
        users = users.filter(user_type=user_type_filter)

    if status_filter == 'banned':
        users = users.filter(is_banned=True)
    elif status_filter == 'active':
        users = users.filter(is_banned=False, is_active=True)
    elif status_filter == 'inactive':
        users = users.filter(is_active=False)

    # Order by date joined (newest first)
    users = users.order_by('-date_joined')

    # Pagination
    paginator = Paginator(users, 20)  # 20 users per page
    page_obj = paginator.get_page(page_number)

    # Statistics for the page
    total_users = CustomUser.objects.count()
    active_users = CustomUser.objects.filter(is_active=True, is_banned=False).count()
    banned_users = CustomUser.objects.filter(is_banned=True).count()
    brand_users = CustomUser.objects.filter(user_type='brand').count()
    influencer_users = CustomUser.objects.filter(user_type='influencer').count()
    admin_users = CustomUser.objects.filter(user_type='admin').count()

    context = {
        'page_obj': page_obj,
        'search_query': search_query,
        'user_type_filter': user_type_filter,
        'status_filter': status_filter,
        'total_users': total_users,
        'active_users': active_users,
        'banned_users': banned_users,
        'brand_users': brand_users,
        'influencer_users': influencer_users,
        'admin_users': admin_users,
    }

    return render(request, 'admin/user_management.html', context)

@login_required
def message_management(request):
    """Message management page for admins"""
    if request.user.user_type != 'admin':
        messages.error(request, 'Access denied.')
        return redirect('admin_dashboard')

    # Get filter parameters
    status_filter = request.GET.get('status', 'all')
    page_number = request.GET.get('page', 1)

    # Base queryset
    messages_queryset = ContactMessage.objects.all()

    # Apply filters
    if status_filter == 'unread':
        messages_queryset = messages_queryset.filter(is_read=False)
    elif status_filter == 'read':
        messages_queryset = messages_queryset.filter(is_read=True)

    # Order by creation date (newest first)
    messages_queryset = messages_queryset.order_by('-created_at')

    # Pagination
    paginator = Paginator(messages_queryset, 20)  # 20 messages per page
    page_obj = paginator.get_page(page_number)

    # Statistics
    total_messages = ContactMessage.objects.count()
    unread_messages = ContactMessage.objects.filter(is_read=False).count()
    read_messages = ContactMessage.objects.filter(is_read=True).count()

    context = {
        'page_obj': page_obj,
        'status_filter': status_filter,
        'total_messages': total_messages,
        'unread_messages': unread_messages,
        'read_messages': read_messages,
    }

    return render(request, 'admin/messages.html', context)

@login_required
def mark_message_read(request, message_id):
    """Mark a message as read"""
    if request.user.user_type != 'admin':
        messages.error(request, 'Access denied.')
        return redirect('admin_dashboard')

    message = get_object_or_404(ContactMessage, id=message_id)
    message.is_read = True
    message.save()

    messages.success(request, 'Message marked as read.')
    return redirect('adminPanel:messages')

@login_required
def delete_message(request, message_id):
    """Delete a message"""
    if request.user.user_type != 'admin':
        messages.error(request, 'Access denied.')
        return redirect('admin_dashboard')

    message = get_object_or_404(ContactMessage, id=message_id)
    message.delete()

    messages.success(request, 'Message deleted successfully.')
    return redirect('adminPanel:messages')