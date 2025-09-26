from django.shortcuts import render
from django.http import HttpResponse



<<<<<<< HEAD
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
=======
def landing_page(request):
    return render(request, 'index.html')
>>>>>>> f074d2f1517a89854def9b484246dec45cb57890
