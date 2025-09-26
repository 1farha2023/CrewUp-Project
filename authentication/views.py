<<<<<<< HEAD
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.contrib import messages
from .forms import CustomUserCreationForm
from .models import CustomUser

def signup_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Account created successfully!')
            return redirect('home')
    else:
        form = CustomUserCreationForm()
    return render(request, 'authentication/signup.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        remember_me = request.POST.get('remember_me')
        
        # Authenticate using email
        user = authenticate(request, username=email, password=password)
        
        if user is not None:
            login(request, user)
            
            # Set session expiry based on remember me
            if not remember_me:
                request.session.set_expiry(0)  # Session expires when browser closes
            
            messages.success(request, f'Welcome back, {user.username}!')
            
            # Redirect to appropriate dashboard based on user type
            if user.role == 'BRAND_OWNER':
                return redirect('brand_dashboard')
            elif user.role == 'INFLUENCER':
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
=======
from django.shortcuts import render,redirect

# Create your views here.
def login_view(request):
    error = None
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        
        if email == 'a@gmail.com' and password == '1234':
            # Redirect to dashboard template in admin folder
            return redirect('dashboard')  # We'll create this url name below
        else:
            error = "Invalid email or password"
    
    return render(request, 'authentication/login.html', {'error': error})

def signup_view(request):
    return render(request, 'authentication/signup.html')

def forget_password_view(request):
    return render(request, 'authentication/forget_password.html')
>>>>>>> f074d2f1517a89854def9b484246dec45cb57890
