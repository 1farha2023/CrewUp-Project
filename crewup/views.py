from django.shortcuts import render
from django.http import HttpResponse




def index(request):
    return render(request, 'index.html')

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

