
from django.shortcuts import render
from django.http import HttpResponse



def landing_page(request):
    return render(request, 'index.html')

def how_it_works(request):
    return render(request, 'how-it-works.html')

def pricing(request):
    return render(request, 'pricing.html')

def about(request):
    return render(request, 'about.html')
