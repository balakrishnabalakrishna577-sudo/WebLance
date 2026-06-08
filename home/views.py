import requests
import base64
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.contrib import messages
from django.http import HttpResponse
from django.conf import settings
from portfolio.models import PortfolioItem
from home.captcha import generate_captcha_text, generate_captcha_image
from dashboard.models import ProjectReview


def home(request):
    portfolio_items = PortfolioItem.objects.all()[:6]
    reviews         = ProjectReview.objects.filter(
                          is_public=True,
                          project__status='delivered'
                      ).select_related('client', 'project').order_by('-created_at')[:8]
    return render(request, 'home/home.html', {
        'portfolio_items': portfolio_items,
        'reviews':         reviews,
    })


def register(request):
    if request.method == 'POST':
        username  = request.POST.get('username', '').strip()
        email     = request.POST.get('email', '').strip()
        password1 = request.POST.get('password1', '')
        password2 = request.POST.get('password2', '')

        # Basic validation
        if not username or len(username) < 3:
            messages.error(request, 'Username must be at least 3 characters.')
            return render(request, 'account/signup.html')
        if password1 != password2:
            messages.error(request, 'Passwords do not match.')
            return render(request, 'account/signup.html')
        if len(password1) < 8:
            messages.error(request, 'Password must be at least 8 characters.')
            return render(request, 'account/signup.html')
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already taken.')
            return render(request, 'account/signup.html')
        if email and User.objects.filter(email=email).exists():
            messages.error(request, 'An account with this email already exists.')
            return render(request, 'account/signup.html')

        user = User.objects.create_user(username=username, email=email, password=password1)
        login(request, user)
        request.session['show_cookie_banner'] = True
        messages.success(request, f'Welcome, {username}! Your account has been created.')
        return redirect('home')

    return render(request, 'account/signup.html')


def clear_cookie_flag(request):
    if request.method == 'POST':
        request.session.pop('show_cookie_banner', None)
    return HttpResponse('ok')


def health_check(request):
    """Lightweight keep-alive endpoint for Render ping cron job."""
    return HttpResponse('ok', content_type='text/plain')


def privacy_policy(request):
    return render(request, 'home/privacy_policy.html')


def captcha_image(request):
    """Generate and return a CAPTCHA image, storing the answer in session."""
    text = generate_captcha_text(6)
    request.session['captcha_text'] = text.upper()
    request.session.modified = True  # force session save
    img_bytes = generate_captcha_image(text)
    response = HttpResponse(img_bytes, content_type='image/png')
    response['Cache-Control'] = 'no-store, no-cache, must-revalidate'
    response['Pragma'] = 'no-cache'
    return response


def custom_login(request):
    """Login view with custom image CAPTCHA verification."""
    if request.user.is_authenticated:
        # Redirect staff to admin panel, clients to dashboard
        if request.user.is_staff:
            return redirect('/panel/')
        return redirect('client_dashboard')

    error = None
    next_url = request.POST.get('next', '') or request.GET.get('next', '')

    if request.method == 'POST':
        username       = request.POST.get('username', '').strip()
        password       = request.POST.get('password', '')
        captcha_input  = request.POST.get('captcha_input', '').strip().upper()
        captcha_stored = request.session.get('captcha_text', '').upper()

        # Validate CAPTCHA first
        if not captcha_input or captcha_input != captcha_stored:
            error = 'Incorrect security code. Please try again.'
        else:
            # CAPTCHA passed — now check credentials
            user = authenticate(request, username=username, password=password)
            if user:
                login(request, user)
                request.session['show_cookie_banner'] = True
                request.session.pop('captcha_text', None)
                # Redirect: use next param if safe, else role-based default
                if next_url and next_url != '/' and not next_url.startswith('/accounts/login'):
                    return redirect(next_url)
                if user.is_staff:
                    return redirect('/panel/')
                return redirect('client_dashboard')
            else:
                error = 'Invalid username or password.'

        # Always clear captcha after POST so image refreshes
        request.session.pop('captcha_text', None)

    return render(request, 'account/login.html', {
        'error': error,
        'next': next_url,
    })


def privacy_policy(request):
    return render(request, 'home/privacy_policy.html')