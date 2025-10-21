from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.contrib.auth.views import LoginView
from django.urls import reverse_lazy
from django.views.generic import CreateView
from django.contrib import messages
from .forms import SignUpForm, LoginForm
from .models import User

class SignUpView(CreateView):
    form_class = SignUpForm
    template_name = 'authentication/signup.html'
    success_url = reverse_lazy('home')

    def form_valid(self, form):
        response = super().form_valid(form)
        login(self.request, self.object)
        messages.success(self.request, 'Account created successfully!')
        return response

    def form_invalid(self, form):
        messages.error(self.request, 'Error creating account. Please check your input.')
        return super().form_invalid(form)

class CustomLoginView(LoginView):
    form_class = LoginForm
    template_name = 'authentication/login.html'
    
    def get_success_url(self):
        user = self.request.user
        if user.role == User.Role.ADMIN:
            return reverse_lazy('admin-dashboard')
        elif user.role == User.Role.BRAND_OWNER:
            return reverse_lazy('brand-dashboard')
        return reverse_lazy('influencer-dashboard')

    def form_invalid(self, form):
        messages.error(self.request, 'Invalid username or password.')
        return super().form_invalid(form)
