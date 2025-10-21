
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
            # Authenticate the user before logging in
            from django.contrib.auth import authenticate
            authenticated_user = authenticate(request, username=user.username, password=form.cleaned_data['password1'])
            if authenticated_user:
                login(request, authenticated_user)

                # Redirect to appropriate dashboard based on user type
                if user.user_type == 'brand':
                    return redirect('brand_dashboard')
                elif user.user_type == 'influencer':
                    return redirect('influencer_dashboard')
                else:
                    return redirect('admin_dashboard')
            else:
                messages.error(request, 'Account created but login failed. Please try logging in manually.')
                return redirect('authentication:login')
        else:
            # Add specific error messages for common validation issues
            if 'email' in form.errors:
                messages.error(request, 'Please enter a valid email address.')
            if 'password2' in form.errors:
                messages.error(request, 'Passwords do not match. Please try again.')
            if 'username' in form.errors:
                messages.error(request, 'Username is already taken or contains invalid characters.')
            # Show other form errors
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{field}: {error}')
    else:
        form = CustomUserCreationForm()
    return render(request, 'authentication/signup.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        email_or_username = request.POST.get('email')
        password = request.POST.get('password')
        remember_me = request.POST.get('remember_me')

        # Validate required fields
        if not email_or_username or not password:
            messages.error(request, 'Please provide both email/username and password.')
            return render(request, 'authentication/login.html')

        # Try to find user by email or username
        from django.contrib.auth import get_user_model
        User = get_user_model()
        
        user = None
        # First try to find by email
        try:
            user_obj = User.objects.get(email__iexact=email_or_username)
            # Authenticate with username
            user = authenticate(request, username=user_obj.username, password=password)
        except User.DoesNotExist:
            # If not found by email, try username
            try:
                user_obj = User.objects.get(username__iexact=email_or_username)
                user = authenticate(request, username=user_obj.username, password=password)
            except User.DoesNotExist:
                pass

        if user is not None:
            # If user is inactive, prevent login
            if not user.is_active:
                messages.error(request, 'This account is inactive. Please contact support.')
                return render(request, 'authentication/login.html')

            login(request, user)

            # Set session expiry based on remember me
            if not remember_me:
                request.session.set_expiry(0)  # Session expires when browser closes

            # Redirect to appropriate dashboard based on user type
            if user.user_type == 'brand':
                return redirect('brand_dashboard')
            elif user.user_type == 'influencer':
                return redirect('influencer_dashboard')
            else:
                return redirect('admin_dashboard')
        else:
            # Generic message for invalid credentials
            messages.error(request, 'Invalid email/username or password. Please check your credentials and try again.')

    return render(request, 'authentication/login.html')

def forget_password_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        # Implement password reset logic here
        messages.success(request, 'Password reset link sent!')
        return redirect('authentication:login')
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
            return redirect('influencer_dashboard')
    else:
        form = InfluencerProfileForm(instance=request.user)

    return render(request, 'authentication/influencer_profile.html', {'form': form})

def logout_view(request):
    """Logout user and redirect to home page"""
    logout(request)
    return redirect('home')

