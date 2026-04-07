from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django import forms
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from portfolio.models import PortfolioItem
from home.models import Testimonial


class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=False, widget=forms.EmailInput(attrs={'autocomplete': 'email'}))

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')


def home(request):
    portfolio_items = PortfolioItem.objects.all()[:6]
    testimonials = Testimonial.objects.filter(is_active=True)
    return render(request, 'home/home.html', {
        'portfolio_items': portfolio_items,
        'testimonials': testimonials,
    })


def register(request):
    if request.user.is_authenticated:
        return redirect('home')
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f'Welcome to WEBLANCE, {user.username}!')
            return redirect('home')
        else:
            messages.error(request, 'Please fix the errors below.')
    else:
        form = RegisterForm()
    return render(request, 'registration/register.html', {'form': form})


@require_POST
def clear_cookie_flag(request):
    request.session.pop('show_cookie_banner', None)
    return JsonResponse({'ok': True})
