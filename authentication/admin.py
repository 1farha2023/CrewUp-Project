from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.html import format_html
from django.urls import reverse
from .models import CustomUser

@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    # Display fields in the list view
    list_display = ('username', 'email', 'user_type', 'is_banned', 'is_active', 'date_joined', 'ban_actions')
    list_filter = ('user_type', 'is_banned', 'is_active', 'date_joined', 'is_staff', 'is_superuser')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    ordering = ('-date_joined',)

    # Fieldsets for the detail view
    fieldsets = UserAdmin.fieldsets + (
        ('Additional Info', {
            'fields': ('user_type', 'bio', 'profile_picture', 'company_name', 'website', 'phone', 'location')
        }),
        ('Brand Fields', {
            'fields': ('industry', 'brand_size'),
            'classes': ('collapse',)
        }),
        ('Influencer Fields', {
            'fields': ('niche', 'instagram_handle', 'youtube_channel', 'tiktok_handle', 'followers_count'),
            'classes': ('collapse',)
        }),
        ('Ban Information', {
            'fields': ('is_banned', 'banned_at', 'banned_reason', 'banned_by'),
        }),
    )

    # Fields for the add form
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Additional Info', {
            'fields': ('user_type', 'email')
        }),
    )

    # Read-only fields
    readonly_fields = ('banned_at', 'banned_by', 'date_joined', 'last_login')

    # Actions
    actions = ['ban_selected_users', 'unban_selected_users']

    def ban_actions(self, obj):
        """Display ban/unban actions in the list view"""
        if obj.is_banned:
            return format_html(
                '<a class="button" href="{}" style="color: green;">Unban</a>',
                reverse('admin:authentication_customuser_change', args=[obj.pk])
            )
        else:
            return format_html(
                '<a class="button" href="{}" style="color: red;">Ban</a>',
                reverse('admin:authentication_customuser_change', args=[obj.pk])
            )
    ban_actions.short_description = 'Actions'

    def ban_selected_users(self, request, queryset):
        """Action to ban selected users"""
        for user in queryset:
            if not user.is_banned and user.user_type != 'admin' and user != request.user:
                user.is_banned = True
                user.is_active = False
                user.banned_by = request.user
                user.save()
        self.message_user(request, f'Successfully banned {queryset.count()} users.')
    ban_selected_users.short_description = 'Ban selected users'

    def unban_selected_users(self, request, queryset):
        """Action to unban selected users"""
        for user in queryset:
            if user.is_banned:
                user.is_banned = False
                user.is_active = True
                user.banned_at = None
                user.banned_reason = None
                user.banned_by = None
                user.save()
        self.message_user(request, f'Successfully unbanned {queryset.count()} users.')
    unban_selected_users.short_description = 'Unban selected users'

    def get_queryset(self, request):
        """Optimize queryset with select_related"""
        return super().get_queryset(request).select_related('banned_by')
