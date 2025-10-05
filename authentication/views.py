
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .forms import CustomUserCreationForm, BrandProfileForm, InfluencerProfileForm
from .models import CustomUser

def signup_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Account created successfully!')

            # Redirect to appropriate dashboard based on user type
            if user.user_type == 'brand':
                return redirect('brand_dashboard')
            elif user.user_type == 'influencer':
                return redirect('influencer_dashboard')
            else:
                return redirect('admin_dashboard')

    else:
        form = CustomUserCreationForm()
    return render(request, 'authentication/signup.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        remember_me = request.POST.get('remember_me')
        
        # Authenticate using email with custom backend
        from .backends import EmailOrUsernameModelBackend
        backend = EmailOrUsernameModelBackend()
        user = backend.authenticate(request, username=email, password=password)
        
        if user is not None:
            login(request, user)
            
            # Set session expiry based on remember me
            if not remember_me:
                request.session.set_expiry(0)  # Session expires when browser closes
            
            messages.success(request, f'Welcome back, {user.username}!')
            
            # Redirect to appropriate dashboard based on user type
            if user.user_type == 'brand':
                return redirect('brand_dashboard')
            elif user.user_type == 'influencer':
                return redirect('influencer_dashboard')
            else:
                return redirect('admin_dashboard')
        else:
            messages.error(request, 'Invalid email or password.')
    
    return render(request, 'authentication/login.html')

def forget_password_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        # Implement password reset logic here
        messages.success(request, 'Password reset link sent!')
        return redirect('login')
    return render(request, 'authentication/forget_password.html')

@login_required
def brand_profile_view(request):
    """Allow brand users to manage their profile"""
    if request.user.user_type != 'brand':
        messages.error(request, 'Only brand users can access this page.')
        return redirect('home')

    if request.method == 'POST':
        form = BrandProfileForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('brand_dashboard')
    else:
        form = BrandProfileForm(instance=request.user)

    return render(request, 'authentication/brand_profile.html', {'form': form})

@login_required
def influencer_profile_view(request):
    """Allow influencer users to manage their profile"""
    if request.user.user_type != 'influencer':
        messages.error(request, 'Only influencer users can access this page.')
        return redirect('home')

    if request.method == 'POST':
        form = InfluencerProfileForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('influencer_dashboard')
    else:
        form = InfluencerProfileForm(instance=request.user)

    return render(request, 'authentication/influencer_profile.html', {'form': form})

def logout_view(request):
    """Logout user and redirect to home page"""
    logout(request)
    messages.success(request, 'You have been logged out successfully!')
    return redirect('home')

