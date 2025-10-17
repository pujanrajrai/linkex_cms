# views.py
import requests
from django.conf import settings
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponse
from django.contrib import messages
from django.shortcuts import render, redirect
from .forms import LoginForm  # Import your LoginForm


def user_login(request):
    context = {'RECAPTCHA_SITE_KEY': settings.RECAPTCHA_SITE_KEY}
    form = LoginForm(request.POST or None)
    if request.user.is_authenticated:
        return redirect('accounts:pages:user:list')

    if request.method == 'POST':
        if form.is_valid():
            email = form.cleaned_data['email'].lower()
            password = form.cleaned_data['password']

            user = authenticate(request, email=email, password=password)
            if user is not None:
                if user.is_blocked:
                    messages.error(request, "Your account is blocked.")
                elif user.agency and user.agency.is_blocked:
                    messages.error(request, "Your agency is blocked.")
                else:
                    login(request, user)
                    if user.role == 'admin':
                        return redirect('accounts:pages:user:list')
                    else:
                        agency = user.agency
                        return redirect('accounts:pages:agency:detail', pk=agency.id)
            else:
                context["email"] = email
                messages.error(request, "Invalid email or password.")
        else:
            messages.error(
                request, "Invalid form submission. Please try again.")

    context.update({'form': form})
    return render(request, 'accounts/auth/login.html', context)


def user_logout(request):
    logout(request)
    return redirect('accounts:pages:auth:login')
