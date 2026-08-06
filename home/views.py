import re
import requests
import base64
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.conf import settings
from portfolio.models import PortfolioItem
from home.captcha import generate_captcha_text, generate_captcha_image
from home.models import UserProfile
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


def _is_valid_email(email):
    """Basic RFC-5322 email format check."""
    pattern = r'^[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


def _is_valid_phone(phone):
    """Accept 10-15 digit phone numbers, optionally starting with +."""
    pattern = r'^\+?[0-9]{10,15}$'
    return bool(re.match(pattern, phone.replace(' ', '').replace('-', '')))


def register(request):
    if request.method == 'POST':
        username  = request.POST.get('username', '').strip()
        email     = request.POST.get('email', '').strip()
        phone     = request.POST.get('phone', '').strip()
        password1 = request.POST.get('password1', '')
        password2 = request.POST.get('password2', '')

        errors = []

        if not username or len(username) < 3:
            errors.append('Username must be at least 3 characters.')
        elif User.objects.filter(username=username).exists():
            errors.append('Username already taken.')

        # Email is required + must be valid format
        if not email:
            errors.append('Email address is required.')
        elif not _is_valid_email(email):
            errors.append('Please enter a valid email address (e.g. name@example.com).')
        elif User.objects.filter(email=email).exists():
            errors.append('An account with this email already exists.')

        # Phone is required + must be valid
        if not phone:
            errors.append('Mobile number is required.')
        elif not _is_valid_phone(phone):
            errors.append('Enter a valid mobile number (10–15 digits).')

        if password1 != password2:
            errors.append('Passwords do not match.')
        elif len(password1) < 8:
            errors.append('Password must be at least 8 characters.')

        if errors:
            for err in errors:
                messages.error(request, err)
            return render(request, 'account/signup.html', {
                'form_data': {'username': username, 'email': email, 'phone': phone}
            })

        user = User.objects.create_user(username=username, email=email, password=password1)
        # Save phone to profile (auto-created by signal)
        profile, _ = UserProfile.objects.get_or_create(user=user)
        profile.phone = phone
        profile.save()

        login(request, user)
        request.session['show_cookie_banner'] = True
        messages.success(request, f'Welcome, {username}! Your account has been created.')
        return redirect('client_dashboard')

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


@login_required
def profile_edit(request):
    """Client edits their own profile — name, email, phone, password."""
    user = request.user
    profile, _ = UserProfile.objects.get_or_create(user=user)

    if request.method == 'POST':
        first_name = request.POST.get('first_name', '').strip()
        last_name  = request.POST.get('last_name', '').strip()
        email      = request.POST.get('email', '').strip()
        phone      = request.POST.get('phone', '').strip()
        new_pass   = request.POST.get('new_password', '').strip()
        confirm    = request.POST.get('confirm_password', '').strip()

        errors = []

        if email and not _is_valid_email(email):
            errors.append('Please enter a valid email address.')
        elif email and email != user.email and User.objects.filter(email=email).exclude(pk=user.pk).exists():
            errors.append('This email is already used by another account.')

        if phone and not _is_valid_phone(phone):
            errors.append('Enter a valid mobile number (10–15 digits).')

        if new_pass:
            if len(new_pass) < 8:
                errors.append('New password must be at least 8 characters.')
            elif new_pass != confirm:
                errors.append('Passwords do not match.')

        if errors:
            for err in errors:
                messages.error(request, err)
        else:
            user.first_name = first_name
            user.last_name  = last_name
            if email:
                user.email = email
            if new_pass:
                user.set_password(new_pass)
            user.save()

            profile.phone = phone
            profile.save()

            if new_pass:
                from django.contrib.auth import update_session_auth_hash
                update_session_auth_hash(request, user)

            messages.success(request, 'Profile updated successfully.')
            return redirect('profile_edit')

    return render(request, 'account/profile_edit.html', {
        'user': user,
        'profile': profile,
    })
