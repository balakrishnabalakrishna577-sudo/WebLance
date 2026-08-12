import re
import json
import random
import time
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, JsonResponse
from django.conf import settings
from django.core.mail import send_mail, EmailMultiAlternatives
from django.views.decorators.http import require_POST
from portfolio.models import PortfolioItem
from home.captcha import generate_captcha_text, generate_captcha_image
from home.models import UserProfile
from dashboard.models import ProjectReview


# ── Helpers ────────────────────────────────────────────────────────

def _is_valid_email(email):
    pattern = r'^[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


def _is_valid_phone(phone):
    pattern = r'^\+?[0-9]{10,15}$'
    return bool(re.match(pattern, phone.replace(' ', '').replace('-', '')))


# ── Public pages ───────────────────────────────────────────────────

def home(request):
    portfolio_items = PortfolioItem.objects.all()[:6]
    reviews = ProjectReview.objects.filter(
        is_public=True, project__status='delivered'
    ).select_related('client', 'project').order_by('-created_at')[:18]
    return render(request, 'home/home.html', {
        'portfolio_items': portfolio_items,
        'reviews': reviews,
    })


def privacy_policy(request):
    return render(request, 'home/privacy_policy.html')


def health_check(request):
    return HttpResponse('ok', content_type='text/plain')


def clear_cookie_flag(request):
    if request.method == 'POST':
        request.session.pop('show_cookie_banner', None)
    return HttpResponse('ok')


def captcha_image(request):
    text = generate_captcha_text(6)
    request.session['captcha_text'] = text.upper()
    request.session.modified = True
    img_bytes = generate_captcha_image(text)
    response = HttpResponse(img_bytes, content_type='image/png')
    response['Cache-Control'] = 'no-store, no-cache, must-revalidate'
    response['Pragma'] = 'no-cache'
    return response


# ── Login ──────────────────────────────────────────────────────────

def custom_login(request):
    if request.user.is_authenticated:
        if request.user.is_staff:
            return redirect('/panel/')
        return redirect('client_dashboard')

    error = None
    next_url = request.POST.get('next', '') or request.GET.get('next', '')

    if request.method == 'POST':
        username      = request.POST.get('username', '').strip()
        password      = request.POST.get('password', '')
        captcha_input = request.POST.get('captcha_input', '').strip().upper()
        captcha_stored = request.session.get('captcha_text', '').upper()

        if not captcha_input or captcha_input != captcha_stored:
            error = 'Incorrect security code. Please try again.'
        else:
            user = authenticate(request, username=username, password=password)
            if user:
                login(request, user)
                request.session['show_cookie_banner'] = True
                request.session.pop('captcha_text', None)
                if next_url and next_url != '/' and not next_url.startswith('/accounts/login'):
                    return redirect(next_url)
                if user.is_staff:
                    return redirect('/panel/')
                return redirect('client_dashboard')
            else:
                error = 'Invalid username or password.'

        request.session.pop('captcha_text', None)

    return render(request, 'account/login.html', {'error': error, 'next': next_url})


# ── OTP ────────────────────────────────────────────────────────────

@require_POST
def send_otp(request):
    """Send a 6-digit OTP to the email and store it in session."""
    try:
        data  = json.loads(request.body)
        email = data.get('email', '').strip().lower()
    except (json.JSONDecodeError, AttributeError):
        return JsonResponse({'ok': False, 'error': 'Invalid request.'}, status=400)

    if not email or not _is_valid_email(email):
        return JsonResponse({'ok': False, 'error': 'Please enter a valid email address.'})

    if User.objects.filter(email__iexact=email).exists():
        return JsonResponse({'ok': False, 'error': 'An account with this email already exists.'})

    otp = str(random.randint(100000, 999999))
    request.session['otp_code']  = otp
    request.session['otp_email'] = email
    request.session['otp_time']  = str(time.time())
    request.session.modified = True

    plain = (
        f'Your Weblance verification code is: {otp}\n\n'
        f'Valid for 10 minutes. Do not share this code.\n\n— Weblance Team'
    )
    html = f"""
<div style="font-family:'Segoe UI',sans-serif;max-width:480px;margin:0 auto;
            background:#fff;border-radius:12px;overflow:hidden;
            box-shadow:0 4px 20px rgba(0,0,0,.08);">
  <div style="background:linear-gradient(135deg,#6366F1,#4F46E5);padding:20px 28px;text-align:center;">
    <span style="font-size:1.2rem;font-weight:900;letter-spacing:2px;color:#fff;">WEBLANCE</span>
  </div>
  <div style="padding:32px 28px;text-align:center;">
    <div style="font-size:2.2rem;margin-bottom:10px;">📧</div>
    <h2 style="margin:0 0 8px;color:#1E293B;font-size:1.1rem;">Email Verification</h2>
    <p style="color:#64748B;font-size:.88rem;margin:0 0 24px;">
      Use the code below to verify your email address.
    </p>
    <div style="background:#F1F5F9;border-radius:10px;padding:18px 24px;
                display:inline-block;margin-bottom:20px;">
      <span style="font-size:2rem;font-weight:900;letter-spacing:10px;
                   color:#4F46E5;font-family:monospace;">{otp}</span>
    </div>
    <p style="color:#94A3B8;font-size:.78rem;margin:0;">
      Valid for <strong>10 minutes</strong>. Do not share this code.
    </p>
  </div>
  <div style="background:#F8FAFF;padding:14px 28px;text-align:center;
              border-top:1px solid #E2E8F0;">
    <p style="margin:0;font-size:.72rem;color:#94A3B8;">
      If you didn't request this, you can safely ignore this email.
    </p>
  </div>
</div>"""

    try:
        msg = EmailMultiAlternatives(
            subject='Your Weblance Verification Code',
            body=plain,
            from_email='Weblance <infoweblance01@gmail.com>',
            to=[email],
        )
        msg.attach_alternative(html, 'text/html')
        msg.send(fail_silently=False)
        return JsonResponse({'ok': True})
    except Exception as e:
        import logging
        logging.getLogger(__name__).error(f'OTP send failed: {e}')
        return JsonResponse({'ok': False, 'error': 'Failed to send email. Please try again.'})


# ── Registration ───────────────────────────────────────────────────

def register(request):
    if request.method == 'POST':
        username  = request.POST.get('username', '').strip()
        email     = request.POST.get('email', '').strip().lower()
        phone     = request.POST.get('phone', '').strip()
        password1 = request.POST.get('password1', '')
        password2 = request.POST.get('password2', '')
        otp_input = request.POST.get('otp', '').strip()

        errors = []

        # Username
        if not username or len(username) < 3:
            errors.append('Username must be at least 3 characters.')
        elif User.objects.filter(username=username).exists():
            errors.append('Username already taken.')

        # Email
        if not email:
            errors.append('Email address is required.')
        elif not _is_valid_email(email):
            errors.append('Please enter a valid email address (e.g. name@gmail.com).')
        elif User.objects.filter(email__iexact=email).exists():
            errors.append('An account with this email already exists.')

        # Phone
        if not phone:
            errors.append('Mobile number is required.')
        elif not _is_valid_phone(phone):
            errors.append('Enter a valid mobile number (10–15 digits).')

        # Password
        if password1 != password2:
            errors.append('Passwords do not match.')
        elif len(password1) < 8:
            errors.append('Password must be at least 8 characters.')

        # OTP
        otp_stored   = request.session.get('otp_code', '')
        otp_email    = request.session.get('otp_email', '').lower()
        otp_time_str = request.session.get('otp_time', '0')

        if not otp_input:
            errors.append('Please verify your email — enter the OTP sent to your inbox.')
        elif email != otp_email:
            errors.append('OTP was sent to a different email. Please request a new OTP.')
        elif time.time() - float(otp_time_str) > 600:
            errors.append('OTP has expired. Please request a new one.')
        elif otp_input != otp_stored:
            errors.append('Incorrect OTP. Please check the code sent to your email.')

        if errors:
            for err in errors:
                messages.error(request, err)
            return render(request, 'account/signup.html', {
                'form_data': {'username': username, 'email': email, 'phone': phone}
            })

        # Clear OTP from session
        for k in ('otp_code', 'otp_email', 'otp_time'):
            request.session.pop(k, None)

        # Create user
        user = User.objects.create_user(username=username, email=email, password=password1)
        profile, _ = UserProfile.objects.get_or_create(user=user)
        profile.phone = phone
        profile.save()

        login(request, user)
        request.session['show_cookie_banner'] = True
        messages.success(request, f'Welcome, {username}! Your account has been created.')
        return redirect('client_dashboard')

    return render(request, 'account/signup.html')


# ── Profile edit ───────────────────────────────────────────────────

@login_required
def profile_edit(request):
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
