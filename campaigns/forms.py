from django import forms
from .models import Campaign, CampaignApplication

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