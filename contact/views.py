from django.shortcuts import render, redirect
from django.contrib import messages
from django.core.mail import send_mail, EmailMultiAlternatives
from django.conf import settings
from .models import ContactMessage
from .forms import ContactForm
import logging

logger = logging.getLogger(__name__)

ADMIN_EMAIL = 'infoweblance01@gmail.com'

def contact(request):
    """Public contact form — no login required."""
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            obj = form.save(commit=False)
            # If "Other" selected, use the free-text value from hidden input
            bt = request.POST.get('business_type', '').strip()
            if bt == 'Other' or bt == '':
                custom = request.POST.get('business_type_other', '').strip()
                if custom:
                    obj.business_type = custom
            else:
                obj.business_type = bt
            obj.save()
            _send_contact_emails(obj)
            messages.success(request, 'Thank you for contacting WEBLANCE. We will get back to you within 24 hours.')
            return redirect('contact')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = ContactForm()
    return render(request, 'contact/contact.html', {'form': form})


def _send_contact_emails(obj):
    # Greeting to client
    html = f"""<!DOCTYPE html>
<html><head><meta charset="UTF-8"></head>
<body style="margin:0;padding:0;background:#ffffff;font-family:Arial,sans-serif;">
<table width="100%" cellpadding="0" cellspacing="0" style="background:#ffffff;padding:40px 0;">
<tr><td align="center">
<table width="600" cellpadding="0" cellspacing="0" style="max-width:600px;width:100%;background:#fff;border-radius:8px;overflow:hidden;box-shadow:0 2px 12px rgba(0,0,0,0.08);">
  <tr><td style="background:linear-gradient(135deg,#6366F1,#818CF8);padding:20px 40px;text-align:center;">
    <table cellpadding="0" cellspacing="0" style="margin:0 auto;"><tr>
      <td style="padding-right:10px;vertical-align:middle;">
        <img src="{(settings.SITE_URL or "https://weblancehub.in").rstrip("/")}/static/images/logoweblance.png" alt="Weblance" width="40" height="40" style="border-radius:50%;display:block;border:2px solid rgba(255,255,255,.6);">
      </td>
      <td style="vertical-align:middle;">
        <span style="font-size:20px;font-weight:900;letter-spacing:3px;color:#fff;">WEB<span style="color:#fff;opacity:.85;">LANCE</span></span>
      </td>
    </tr></table>
  </td></tr>
  <tr><td style="height:4px;background:linear-gradient(90deg,#4F46E5,#6366F1,#818CF8);"></td></tr>
  <tr><td style="background:#F8F9FF;padding:36px 40px;text-align:center;border-bottom:1px solid #E2E8F0;">
    <h1 style="margin:0 0 10px;color:#1E293B;font-size:24px;font-weight:800;">We received your message! 📩</h1>
    <p style="margin:0;color:#475569;font-size:14px;line-height:1.6;max-width:420px;margin:0 auto;">
      Hi <strong style="color:#1E293B;">{obj.name}</strong>, thank you for reaching out. Our team will reply within <strong style="color:#6366F1;">24 hours</strong>.
    </p>
  </td></tr>
  <tr><td style="padding:32px 40px;">
    <div style="background:#f8f9fa;border-radius:8px;padding:20px 24px;border-left:4px solid #4F46E5;margin-bottom:24px;">
      <div style="font-size:11px;font-weight:700;text-transform:uppercase;letter-spacing:1px;color:#4F46E5;margin-bottom:12px;">Your Message</div>
      <table width="100%" cellpadding="0" cellspacing="0">
        <tr><td style="padding:5px 0;color:#64748B;font-size:13px;width:35%;">Name</td><td style="padding:5px 0;color:#1E293B;font-weight:600;font-size:13px;">{obj.name}</td></tr>
        <tr><td style="padding:5px 0;color:#64748B;font-size:13px;">Email</td><td style="padding:5px 0;color:#1E293B;font-weight:600;font-size:13px;">{obj.email}</td></tr>
        {'<tr><td style="padding:5px 0;color:#64748B;font-size:13px;">Business</td><td style="padding:5px 0;color:#1E293B;font-weight:600;font-size:13px;">' + obj.business_type + '</td></tr>' if obj.business_type else ''}
        <tr><td style="padding:5px 0;color:#64748B;font-size:13px;vertical-align:top;">Message</td><td style="padding:5px 0;color:#1a1a2e;font-size:13px;line-height:1.5;">{obj.message[:200]}{'...' if len(obj.message) > 200 else ''}</td></tr>
      </table>
    </div>
    <div style="text-align:center;">
      <a href="https://weblancehub.in" style="display:inline-block;background:linear-gradient(135deg,#6366F1,#4F46E5);color:#fff;font-weight:800;font-size:14px;padding:12px 32px;border-radius:50px;text-decoration:none;">Visit Our Website &rarr;</a>
    </div>
  </td></tr>
  <tr><td style="background:linear-gradient(135deg,#6366F1,#4F46E5);padding:16px 40px;text-align:center;">
    <p style="margin:0;color:rgba(255,255,255,.7);font-size:11px;">© 2026 Weblance · +91 7892934437 · infoweblance01@gmail.com</p>
  </td></tr>
</table>
</td></tr>
</table>
</body></html>"""

    plain = f"Hi {obj.name},\n\nThank you for contacting Weblance! We received your message and will reply within 24 hours.\n\nRegards,\nWeblance Team\n+91 7892934437"

    try:
        # Client confirmation
        msg = EmailMultiAlternatives(
            subject='We received your message — Weblance',
            body=plain,
            from_email='Weblance <infoweblance01@gmail.com>',
            to=[obj.email],
        )
        msg.attach_alternative(html, 'text/html')
        msg.send(fail_silently=False)

        # Admin notification
        send_mail(
            subject=f'[New Contact] {obj.name} — {obj.business_type or "General"}',
            message=f'New contact message:\n\nName: {obj.name}\nEmail: {obj.email}\nPhone: {obj.phone}\nBusiness: {obj.business_type or "—"}\n\nMessage:\n{obj.message}',
            from_email='Weblance <infoweblance01@gmail.com>',
            recipient_list=[ADMIN_EMAIL],
            fail_silently=False,
        )
    except Exception as e:
        logger.error(f'Contact email failed: {e}')
