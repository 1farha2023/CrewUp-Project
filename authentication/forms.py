from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser

class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'user_type', 'company_name', 'bio', 'website', 'phone', 'location', 'industry', 'brand_size', 'niche', 'instagram_handle', 'youtube_channel', 'tiktok_handle', 'followers_count')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make profile fields optional during signup
        self.fields['company_name'].required = False
        self.fields['bio'].required = False
        self.fields['website'].required = False
        self.fields['phone'].required = False
        self.fields['location'].required = False
        self.fields['industry'].required = False
        self.fields['brand_size'].required = False
        self.fields['niche'].required = False
        self.fields['instagram_handle'].required = False
        self.fields['youtube_channel'].required = False
        self.fields['tiktok_handle'].required = False
        self.fields['followers_count'].required = False

class BrandProfileForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'bio', 'profile_picture', 'company_name', 'website', 'phone', 'location', 'industry', 'brand_size')
        widgets = {
            'username': forms.TextInput(attrs={'class': 'mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-purple-500 focus:border-purple-500 sm:text-sm'}),
            'email': forms.EmailInput(attrs={'class': 'mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-purple-500 focus:border-purple-500 sm:text-sm'}),
            'bio': forms.Textarea(attrs={'rows': 4, 'class': 'mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-purple-500 focus:border-purple-500 sm:text-sm'}),
            'company_name': forms.TextInput(attrs={'class': 'mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-purple-500 focus:border-purple-500 sm:text-sm'}),
            'website': forms.URLInput(attrs={'class': 'mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-purple-500 focus:border-purple-500 sm:text-sm'}),
            'phone': forms.TextInput(attrs={'class': 'mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-purple-500 focus:border-purple-500 sm:text-sm'}),
            'location': forms.TextInput(attrs={'class': 'mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-purple-500 focus:border-purple-500 sm:text-sm'}),
            'industry': forms.TextInput(attrs={'class': 'mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-purple-500 focus:border-purple-500 sm:text-sm'}),
            'brand_size': forms.Select(attrs={'class': 'mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-purple-500 focus:border-purple-500 sm:text-sm'}),
        }

class InfluencerProfileForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'bio', 'profile_picture', 'website', 'phone', 'location', 'niche', 'instagram_handle', 'youtube_channel', 'tiktok_handle', 'followers_count')
        widgets = {
            'username': forms.TextInput(attrs={'class': 'mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-purple-500 focus:border-purple-500 sm:text-sm'}),
            'email': forms.EmailInput(attrs={'class': 'mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-purple-500 focus:border-purple-500 sm:text-sm'}),
            'bio': forms.Textarea(attrs={'rows': 4, 'class': 'mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-purple-500 focus:border-purple-500 sm:text-sm'}),
            'website': forms.URLInput(attrs={'class': 'mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-purple-500 focus:border-purple-500 sm:text-sm'}),
            'phone': forms.TextInput(attrs={'class': 'mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-purple-500 focus:border-purple-500 sm:text-sm'}),
            'location': forms.TextInput(attrs={'class': 'mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-purple-500 focus:border-purple-500 sm:text-sm'}),
            'niche': forms.TextInput(attrs={'class': 'mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-purple-500 focus:border-purple-500 sm:text-sm', 'placeholder': 'e.g., Fashion, Tech, Fitness'}),
            'instagram_handle': forms.TextInput(attrs={'class': 'mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-purple-500 focus:border-purple-500 sm:text-sm', 'placeholder': '@yourhandle'}),
            'youtube_channel': forms.URLInput(attrs={'class': 'mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-purple-500 focus:border-purple-500 sm:text-sm', 'placeholder': 'https://youtube.com/yourchannel'}),
            'tiktok_handle': forms.TextInput(attrs={'class': 'mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-purple-500 focus:border-purple-500 sm:text-sm', 'placeholder': '@yourhandle'}),
            'followers_count': forms.NumberInput(attrs={'class': 'mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-purple-500 focus:border-purple-500 sm:text-sm', 'placeholder': 'Total followers across platforms'}),
        }