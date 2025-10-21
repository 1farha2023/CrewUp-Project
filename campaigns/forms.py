from django import forms
from .models import Campaign, CampaignApplication, CustomOffer

class CampaignForm(forms.ModelForm):
    class Meta:
        model = Campaign
        fields = ['title', 'description', 'image', 'budget', 'category', 'platform']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter campaign title'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Describe your campaign'
            }),
            'budget': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'placeholder': '0.00'
            }),
            'category': forms.Select(attrs={
                'class': 'form-control'
            }),
            'platform': forms.Select(attrs={
                'class': 'form-control'
            }),
        }

class CampaignApplicationForm(forms.ModelForm):
    class Meta:
        model = CampaignApplication
        fields = ['application_message']
        widgets = {
            'application_message': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Tell the brand why you\'re interested in this campaign and how you can help...'
            }),
        }

class CustomOfferForm(forms.ModelForm):
    class Meta:
        model = CustomOffer
        fields = ['title', 'description', 'offer_amount', 'deliverables', 'deadline', 'brand_message', 'campaign']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter offer title'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Describe the collaboration opportunity'
            }),
            'offer_amount': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'placeholder': '0.00'
            }),
            'deliverables': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'List what the influencer needs to deliver (e.g., 3 Instagram posts, 1 story, etc.)'
            }),
            'deadline': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'brand_message': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Add a personal message to the influencer (optional)'
            }),
            'campaign': forms.Select(attrs={
                'class': 'form-control'
            }),
        }