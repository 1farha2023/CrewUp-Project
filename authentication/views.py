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
