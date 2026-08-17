from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.core.mail import send_mail, EmailMultiAlternatives
from django.conf import settings
from .models import WebsiteRequest
from .forms import WebsiteRequestForm
from .proposal_generator import generate_proposal
import json
import logging

logger = logging.getLogger(__name__)

TYPE_MAP = {
    # plain slugs
    'website':      'website',
    'ecommerce':    'ecommerce',
    'seo':          'seo',
    'redesign':     'redesign',
    'landing':      'landing',
    'maintenance':  'maintenance',
    'portfolio':    'portfolio',
    'blog':         'blog',
    'education':    'education',
    'restaurant':   'restaurant',
    'realestate':   'realestate',
    'hospital':     'hospital',
    'webapp':       'webapp',
    'college':      'college',
    'academic':     'academic',
    'miniproject':  'miniproject',
    'custom':       'custom',
    # display labels
    'website development':          'website',
    'e-commerce website':           'ecommerce',
    'e-commerce development':       'ecommerce',
    'seo optimization':             'seo',
    'website redesign':             'redesign',
    'landing page':                 'landing',
    'website maintenance':          'maintenance',
    'portfolio website':            'portfolio',
    'blog / news website':          'blog',
    'school / education website':   'education',
    'restaurant website':           'restaurant',
    'real estate website':          'realestate',
    'hospital / clinic website':    'hospital',
    'web application development':  'webapp',
    'college project':              'college',
    'academic project':             'academic',
    'mini project':                 'miniproject',
    'custom project':               'custom',
    # legacy
    'business':                     'website',
    'business website':             'website',
    'starter':                      'website',
    'starter website':              'website',
    'premium':                      'custom',
    'custom website development':   'custom',
    'web design':                   'website',
}

BUDGET_MAP = {
    'starter':    'low',
    'business':   'medium',
    'e-commerce': 'high',
    'premium':    'premium',
}


def _send_client_greeting(obj):
    """DEPRECATED — kept for reference only. Use _send_admin_notification instead."""

def _send_service_greeting(obj):
    """Send a greeting email to the client immediately after service quote submission."""
    service_label = obj.selected_plan or obj.get_website_type_display()
    html = f"""<!DOCTYPE html>
<html lang="en">
<head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1"></head>
<body style="margin:0;padding:0;background:#ffffff;font-family:'Segoe UI',Helvetica,Arial,sans-serif;">
<table width="100%" cellpadding="0" cellspacing="0" border="0" style="background:#ffffff;padding:40px 0;">
<tr><td align="center">
<table width="600" cellpadding="0" cellspacing="0" border="0"
       style="max-width:600px;width:100%;background:#ffffff;border-radius:12px;overflow:hidden;box-shadow:0 4px 24px rgba(0,0,0,.1);">

  <tr><td style="background:linear-gradient(135deg,#6366F1,#818CF8);padding:24px 40px;text-align:center;">
    <span style="font-size:22px;font-weight:900;letter-spacing:3px;color:#fff;text-transform:uppercase;">WEB<span style="color:#fff;opacity:.85;">LANCE</span></span>
  </td></tr>
  <tr><td style="height:4px;background:linear-gradient(90deg,#4F46E5,#6366F1,#818CF8);"></td></tr>

  <tr><td style="background:#F8F9FF;padding:40px;text-align:center;border-bottom:1px solid #E2E8F0;">
    <div style="font-size:48px;margin-bottom:12px;">🚀</div>
    <h1 style="margin:0 0 12px;color:#1E293B;font-size:24px;font-weight:900;">We've Got Your Request, {obj.name}!</h1>
    <p style="margin:0 auto;color:#475569;font-size:15px;line-height:1.7;max-width:440px;">
      Thank you for reaching out to <strong style="color:#6366F1;">WEBLANCE</strong>. Your quote request for
      <strong style="color:#1E293B;">{service_label}</strong> has been received and our team will get back to you within <strong style="color:#6366F1;">24 hours</strong>.
    </p>
  </td></tr>

  <tr><td style="padding:32px 40px;">
    <h2 style="margin:0 0 16px;font-size:13px;font-weight:700;text-transform:uppercase;letter-spacing:1px;
               color:#0a0a0a;border-bottom:2px solid #4F46E5;padding-bottom:8px;display:inline-block;">
      Your Request Details
    </h2>
    <table width="100%" cellpadding="0" cellspacing="0" border="0"
           style="background:#FAFBFF;border-radius:10px;border:1px solid #E2E8F0;overflow:hidden;">
      <tr>
        <td style="padding:10px 16px;color:#64748B;font-size:12px;font-weight:600;width:38%;border-bottom:1px solid #E2E8F0;">Name</td>
        <td style="padding:10px 16px;color:#1E293B;font-size:12px;font-weight:700;border-bottom:1px solid #E2E8F0;">{obj.name}</td>
      </tr>
      <tr style="background:#ffffff;">
        <td style="padding:10px 16px;color:#64748B;font-size:12px;font-weight:600;border-bottom:1px solid #E2E8F0;">Business</td>
        <td style="padding:10px 16px;color:#1E293B;font-size:12px;font-weight:700;border-bottom:1px solid #E2E8F0;">{obj.business_name}</td>
      </tr>
      <tr>
        <td style="padding:10px 16px;color:#64748B;font-size:12px;font-weight:600;border-bottom:1px solid #E2E8F0;">Service</td>
        <td style="padding:10px 16px;color:#4F46E5;font-size:12px;font-weight:800;border-bottom:1px solid #E2E8F0;">{service_label}</td>
      </tr>
      <tr style="background:#ffffff;">
        <td style="padding:10px 16px;color:#64748B;font-size:12px;font-weight:600;border-bottom:1px solid #E2E8F0;">Phone</td>
        <td style="padding:10px 16px;color:#1E293B;font-size:12px;font-weight:700;border-bottom:1px solid #E2E8F0;">{obj.phone}</td>
      </tr>
      <tr>
        <td style="padding:10px 16px;color:#64748B;font-size:12px;font-weight:600;">Budget</td>
        <td style="padding:10px 16px;color:#1E293B;font-size:12px;font-weight:700;">{obj.get_budget_display()}</td>
      </tr>
    </table>
  </td></tr>

  <tr><td style="padding:0 40px 32px;">
    <h2 style="margin:0 0 16px;font-size:13px;font-weight:700;text-transform:uppercase;letter-spacing:1px;
               color:#0a0a0a;border-bottom:2px solid #4F46E5;padding-bottom:8px;display:inline-block;">
      What Happens Next?
    </h2>
    <table width="100%" cellpadding="0" cellspacing="0" border="0">
      <tr>
        <td width="40" style="vertical-align:top;padding-right:14px;padding-bottom:14px;">
          <div style="width:32px;height:32px;background:#4F46E5;border-radius:50%;text-align:center;line-height:32px;color:#fff;font-weight:900;font-size:13px;">1</div>
        </td>
        <td style="vertical-align:top;padding-bottom:14px;">
          <div style="color:#1E293B;font-size:13px;font-weight:700;margin-bottom:3px;">Review &amp; Analysis</div>
          <div style="color:#475569;font-size:12px;line-height:1.6;">Our team reviews your requirements and prepares a custom proposal.</div>
        </td>
      </tr>
      <tr>
        <td width="40" style="vertical-align:top;padding-right:14px;padding-bottom:14px;">
          <div style="width:32px;height:32px;background:#4F46E5;border-radius:50%;text-align:center;line-height:32px;color:#fff;font-weight:900;font-size:13px;">2</div>
        </td>
        <td style="vertical-align:top;padding-bottom:14px;">
          <div style="color:#1E293B;font-size:13px;font-weight:700;margin-bottom:3px;">Consultation Call</div>
          <div style="color:#475569;font-size:12px;line-height:1.6;">We contact you within <strong>24 hours</strong> to discuss your project in detail.</div>
        </td>
      </tr>
      <tr>
        <td width="40" style="vertical-align:top;padding-right:14px;">
          <div style="width:32px;height:32px;background:#4F46E5;border-radius:50%;text-align:center;line-height:32px;color:#fff;font-weight:900;font-size:13px;">3</div>
        </td>
        <td style="vertical-align:top;">
          <div style="color:#1E293B;font-size:13px;font-weight:700;margin-bottom:3px;">Proposal &amp; Kickoff</div>
          <div style="color:#475569;font-size:12px;line-height:1.6;">We send a detailed proposal with timeline, pricing, and design options.</div>
        </td>
      </tr>
    </table>
  </td></tr>

  <tr><td style="padding:0 40px 32px;text-align:center;">
    <a href="https://wa.me/917892934437?text=Hi%20Weblance!%20I%20just%20submitted%20a%20quote%20request%20for%20{service_label.replace(' ','%20')}"
       style="display:inline-block;background:linear-gradient(135deg,#6366F1,#4F46E5);color:#fff;font-weight:800;font-size:14px;padding:13px 32px;border-radius:50px;text-decoration:none;margin:4px;">
      💬 Chat on WhatsApp
    </a>
    <a href="tel:+917892934437"
       style="display:inline-block;background:#ffffff;color:#1E293B;font-weight:700;font-size:14px;padding:13px 24px;border-radius:50px;text-decoration:none;border:1.5px solid #C7D2FE;margin:4px;">
      📞 +91 7892934437
    </a>
  </td></tr>

  <tr><td style="background:linear-gradient(135deg,#6366F1,#4F46E5);padding:20px 40px;text-align:center;">
    <p style="margin:0 0 5px;color:#fff;font-size:13px;font-weight:700;letter-spacing:1px;">WEB<span style="color:#fff;opacity:.85;">LANCE</span></p>
    <p style="margin:0;color:rgba(255, 255, 255, 1);font-size:11px;">Devanahalli, Karnataka, India &nbsp;|&nbsp; infoweblance01@gmail.com &nbsp;|&nbsp; +91 7892934437</p>
  </td></tr>

</table>
</td></tr>
</table>
</body>
</html>"""

    plain = (
        f"Hi {obj.name},\n\n"
        f"Thank you for your quote request! We've received your enquiry for {service_label}.\n\n"
        f"REQUEST DETAILS\n{'='*40}\n"
        f"Business : {obj.business_name}\n"
        f"Service  : {service_label}\n"
        f"Phone    : {obj.phone}\n"
        f"Budget   : {obj.get_budget_display()}\n\n"
        f"WHAT HAPPENS NEXT\n{'='*40}\n"
        f"1. Our team reviews your requirements\n"
        f"2. We contact you within 24 hours\n"
        f"3. We send a detailed proposal\n\n"
        f"WhatsApp : wa.me/917892934437\n"
        f"Phone    : +91 7892934437\n"
        f"Email    : infoweblance01@gmail.com\n\n"
        f"— Weblance Team"
    )
    try:
        msg = EmailMultiAlternatives(
            subject=f'We received your quote request — {service_label} | Weblance',
            body=plain,
            from_email='Weblance <infoweblance01@gmail.com>',
            to=[obj.email],
        )
        msg.attach_alternative(html, 'text/html')
        msg.send(fail_silently=True)
        logger.info(f'Service greeting sent to {obj.email}')
    except Exception as e:
        logger.error(f'Service greeting failed: {e}')

def _send_admin_notification(obj):
    """Notify admin of new request. Client email is sent after template selection."""
    try:
        send_mail(
            subject=f'[New Request] {obj.business_name} — {obj.get_website_type_display()}',
            message=(
                f'New website request received.\n\n'
                f'Name     : {obj.name}\n'
                f'Business : {obj.business_name}\n'
                f'Email    : {obj.email}\n'
                f'Phone    : {obj.phone}\n'
                f'Type     : {obj.get_website_type_display()}\n'
                f'Plan     : {obj.selected_plan or "—"}\n'
                f'Budget   : {obj.get_budget_display()}\n\n'
                f'Description:\n{obj.description}\n\n'
                f'Proposal email has been auto-sent to the client with the recommended template.'
            ),
            from_email='Weblance <infoweblance01@gmail.com>',
            recipient_list=['infoweblance01@gmail.com'],
            fail_silently=True,
        )
    except Exception as e:
        logger.error(f'Admin notification failed: {e}')


def request_website(request):
    plan    = request.GET.get('plan', '').strip()
    service = request.GET.get('service', '').strip()
    label   = plan or service

    preset_type   = TYPE_MAP.get(label.lower(), '')
    preset_budget = BUDGET_MAP.get(label.lower(), '')

    # ── Offer pre-fill ────────────────────────────────────────────
    offer_obj = None
    offer_id  = request.GET.get('offer', '').strip()
    if offer_id:
        try:
            from home.models import Offer
            from django.utils import timezone as tz
            o = Offer.objects.get(pk=offer_id, is_active=True)
            if not o.is_expired:
                offer_obj = o
                # Pre-fill type from offer if not already set by plan/service
                if not preset_type and o.service_type:
                    preset_type = o.service_type
        except Exception:
            pass

    if request.method == 'POST':
        form = WebsiteRequestForm(request.POST)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.selected_plan = request.POST.get('_selected_plan', '').strip()
            svc = request.POST.get('_service_label', '').strip()
            if svc and not obj.description.startswith(f'[Plan: {svc}]'):
                obj.description = f"[Plan: {svc}]\n\n{obj.description}"
            # Link to logged-in user
            if request.user.is_authenticated:
                obj.user = request.user
            # Generate proposal
            proposal_data = generate_proposal(obj.website_type, obj.business_name, obj.description)
            obj.proposal = json.dumps(proposal_data)

            # Auto-select the recommended template — skip the selection page
            templates = proposal_data.get('templates', [])
            best_id   = proposal_data.get('best_template', 1)
            best_tpl  = next((t for t in templates if t.get('id') == best_id), templates[0] if templates else None)
            if best_tpl:
                obj.selected_template = f"{best_tpl.get('name', 'Custom')} — {best_tpl.get('style', '')}"

            obj.save()

            # Send admin notification
            _send_admin_notification(obj)

            # ── Notify all staff about new quote request ───────────────
            try:
                from notifications.models import Notification
                Notification.send_to_staff(
                    title=f'New quote request: {obj.business_name}',
                    message=f'{obj.selected_plan or obj.get_website_type_display()} — {obj.name}',
                    notif_type='quote',
                    url='/panel/requests/',
                )
            except Exception:
                pass

            # Send client proposal email immediately (no template selection step)
            if best_tpl:
                colors = best_tpl.get('colors', {})
                dummy  = best_tpl.get('dummy', {})
                sections_str = ' | '.join(
                    f"{s.get('name','')}: {s.get('desc','')}"
                    for s in best_tpl.get('sections', [])
                )
                all_templates_for_email = [{
                    'id':          best_tpl.get('id', 1),
                    'name':        best_tpl.get('name', ''),
                    'style':       best_tpl.get('style', ''),
                    'primary':     colors.get('primary', '#4F46E5'),
                    'accent':      colors.get('accent', '#6366F1'),
                    'bg':          colors.get('bg', '#fff'),
                    'visual':      best_tpl.get('visual', ''),
                    'layout':      best_tpl.get('layout', ''),
                    'headline':    dummy.get('headline', ''),
                    'subheadline': dummy.get('subheadline', ''),
                    'cta':         dummy.get('cta', ''),
                    'sections':    sections_str,
                    'selected':    True,
                }]
                _send_template_selection_email(
                    obj,
                    best_tpl.get('name', 'Custom'),
                    best_tpl.get('style', ''),
                    all_templates_for_email,
                )

            messages.success(
                request,
                'Thank you! Your request has been received. '
                'Check your email for the full proposal — we\'ll be in touch within <strong>24 hours</strong>.'
            )
            if request.user.is_authenticated:
                return redirect('client_dashboard')
            return redirect('home')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = WebsiteRequestForm()

    return render(request, 'requestsite/request.html', {
        'form':          form,
        'selected_plan': label,
        'service_label': label,
        'preset_type':   preset_type,
        'preset_budget': preset_budget,
        'offer':         offer_obj,
    })


@login_required
def website_proposal(request, pk):
    obj = get_object_or_404(WebsiteRequest, pk=pk)
    try:
        proposal = json.loads(obj.proposal) if obj.proposal else {}
    except (json.JSONDecodeError, ValueError):
        proposal = {}

    if not proposal:
        proposal = generate_proposal(obj.website_type, obj.business_name, obj.description)

    return render(request, 'requestsite/proposal.html', {
        'req': obj,
        'proposal': proposal,
        'templates': proposal.get('templates', []),
        'best_id': proposal.get('best_template', 1),
        'best_reason': proposal.get('best_reason', ''),
    })


@login_required
@require_POST
def select_template(request, pk):
    obj = get_object_or_404(WebsiteRequest, pk=pk)
    template_name  = request.POST.get('template_name', '').strip()
    template_style = request.POST.get('template_style', '').strip()

    if not template_name:
        return redirect('website_proposal', pk=pk)

    obj.selected_template = f"{template_name} — {template_style}"
    obj.save(update_fields=['selected_template'])

    # Load all templates from saved proposal JSON (most reliable source)
    all_templates = []
    try:
        proposal_data = json.loads(obj.proposal) if obj.proposal else {}
        for t in proposal_data.get('templates', []):
            colors = t.get('colors', {})
            sections_str = ' | '.join(
                f"{s.get('name','')}: {s.get('desc','')}"
                for s in t.get('sections', [])
            )
            dummy = t.get('dummy', {})
            all_templates.append({
                'id':          t.get('id', 0),
                'name':        t.get('name', ''),
                'style':       t.get('style', ''),
                'primary':     colors.get('primary', '#333'),
                'accent':      colors.get('accent', '#6366F1'),
                'bg':          colors.get('bg', '#fff'),
                'visual':      t.get('visual', ''),
                'layout':      t.get('layout', ''),
                'headline':    dummy.get('headline', ''),
                'subheadline': dummy.get('subheadline', ''),
                'cta':         dummy.get('cta', ''),
                'sections':    sections_str,
                'selected':    t.get('name', '') == template_name,
            })
    except (json.JSONDecodeError, ValueError):
        pass

    # Fallback: build minimal entry from POST if JSON missing
    if not all_templates:
        all_templates = [{
            'id': 1, 'name': template_name, 'style': template_style,
            'primary': '#4F46E5', 'accent': '#6366F1', 'bg': '#fff',
            'visual': '', 'layout': '', 'headline': '', 'subheadline': '',
            'cta': '', 'sections': '', 'selected': True,
        }]

    _send_template_selection_email(obj, template_name, template_style, all_templates)
    messages.success(request, f'Great choice! <strong>{template_name}</strong> confirmed. Check your email for the full proposal.')
    return redirect('client_dashboard')


def _send_template_selection_email(obj, selected_name, selected_style, all_templates):
    """Send ONE email to client with all 3 templates + selected highlighted, plus admin notification."""

    def _card(t):
        is_sel  = t['selected']
        border  = '#6366F1' if is_sel else '#e2e8f0'
        hd_bg   = '#EEF2FF' if is_sel else '#f8f9fa'
        hd_col  = '#4F46E5' if is_sel else '#1a1a2e'
        badge   = (' <span style="background:#6366F1;color:#fff;font-size:10px;font-weight:800;'
                   'padding:2px 8px;border-radius:20px;">&#10003; YOUR CHOICE</span>') if is_sel else ''
        sec_rows = ''
        for part in t.get('sections', '').split(' | '):
            if ':' in part:
                n, d = part.split(':', 1)
                sec_rows += (f'<tr><td style="padding:4px 0;color:#64748B;font-size:11px;'
                             f'width:80px;vertical-align:top;">{n.strip()}</td>'
                             f'<td style="padding:4px 0;color:#475569;font-size:11px;">{d.strip()}</td></tr>')
        sec_block = (f'<tr><td style="padding:10px 16px;border-bottom:1px solid #E2E8F0;">'
                     f'<span style="font-size:10px;font-weight:700;text-transform:uppercase;'
                     f'letter-spacing:.5px;color:#94A3B8;display:block;margin-bottom:5px;">Page Sections</span>'
                     f'<table width="100%" cellpadding="0" cellspacing="0" border="0">{sec_rows}</table>'
                     f'</td></tr>') if sec_rows else ''
        return (
            f'<table width="100%" cellpadding="0" cellspacing="0" border="0" '
            f'style="border:2px solid {border};border-radius:10px;overflow:hidden;margin-bottom:18px;">'
            f'<tr><td style="background:{hd_bg};padding:12px 16px;border-bottom:1px solid {border};">'
            f'<span style="font-size:14px;font-weight:800;color:{hd_col};">{t["name"]}</span>{badge}'
            f'<br><span style="font-size:11px;color:#888;">{t["style"]}</span>'
            f'&nbsp;&nbsp;'
            f'<span style="display:inline-block;width:12px;height:12px;border-radius:50%;background:{t["primary"]};border:1px solid rgba(0,0,0,.1);vertical-align:middle;"></span>'
            f'<span style="display:inline-block;width:12px;height:12px;border-radius:50%;background:{t["accent"]};border:1px solid rgba(0,0,0,.1);vertical-align:middle;margin-left:3px;"></span>'
            f'</td></tr>'
            f'<tr><td style="padding:10px 16px;background:#fafafa;border-bottom:1px solid #E2E8F0;">'
            f'<span style="font-size:11px;color:#555;font-style:italic;">{t["visual"]}</span></td></tr>'
            f'<tr><td style="padding:10px 16px;border-bottom:1px solid #E2E8F0;">'
            f'<span style="font-size:10px;font-weight:700;text-transform:uppercase;color:#94A3B8;">Layout</span><br>'
            f'<span style="font-size:11px;color:#444;">{t["layout"]}</span></td></tr>'
            f'{sec_block}'
            f'<tr><td style="padding:10px 16px;">'
            f'<span style="font-size:10px;font-weight:700;text-transform:uppercase;color:#94A3B8;display:block;margin-bottom:6px;">Sample Content</span>'
            f'<table width="100%" cellpadding="0" cellspacing="0" border="0">'
            f'<tr><td style="padding:3px 0;color:#64748B;font-size:11px;width:80px;">Headline</td>'
            f'<td style="padding:3px 0;color:#1E293B;font-size:11px;font-weight:700;">{t["headline"]}</td></tr>'
            f'<tr><td style="padding:3px 0;color:#64748B;font-size:11px;">Subheadline</td>'
            f'<td style="padding:3px 0;color:#475569;font-size:11px;">{t["subheadline"]}</td></tr>'
            f'<tr><td style="padding:3px 0;color:#64748B;font-size:11px;">CTA Button</td>'
            f'<td style="padding:3px 0;color:#4F46E5;font-size:11px;font-weight:700;">{t["cta"]}</td></tr>'
            f'</table></td></tr>'
            f'</table>'
        )

    # Only the selected template card for the email
    selected_card = next((t for t in all_templates if t['selected']), all_templates[0] if all_templates else None)
    cards_html = _card(selected_card) if selected_card else ''

    html = f"""<!DOCTYPE html>
<html lang="en">
<head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1"></head>
<body style="margin:0;padding:0;background:#ffffff;font-family:'Segoe UI',Helvetica,Arial,sans-serif;">
<table width="100%" cellpadding="0" cellspacing="0" border="0" style="background:#ffffff;padding:40px 0;">
<tr><td align="center">
<table width="620" cellpadding="0" cellspacing="0" border="0"
       style="max-width:620px;width:100%;background:#ffffff;border-radius:10px;overflow:hidden;box-shadow:0 2px 16px rgba(0,0,0,.08);">

  <tr><td style="background:linear-gradient(135deg,#6366F1,#818CF8);padding:22px 40px;text-align:center;">
    <table cellpadding="0" cellspacing="0" border="0" style="margin:0 auto;">
      <tr>
        <td style="padding-right:10px;vertical-align:middle;">
          <img src="{(settings.SITE_URL or "https://weblancehub.in").rstrip("/")}/static/images/logoweblance.png"
               alt="Weblance" width="40" height="40"
               style="border-radius:50%;display:block;border:2px solid rgba(255,255,255,.6);">
        </td>
        <td style="vertical-align:middle;">
          <span style="font-size:20px;font-weight:900;letter-spacing:3px;color:#fff;text-transform:uppercase;">WEB<span style="color:#fff;opacity:.85;">LANCE</span></span>
        </td>
      </tr>
    </table>
  </td></tr>
  <tr><td style="height:4px;background:linear-gradient(90deg,#4F46E5,#6366F1,#818CF8);"></td></tr>

  <tr><td style="background:#F8F9FF;padding:36px 40px;text-align:center;border-bottom:1px solid #E2E8F0;">
    <div style="font-size:42px;margin-bottom:10px;">🎨</div>
    <h1 style="margin:0 0 10px;color:#1E293B;font-size:22px;font-weight:800;">Your Website Proposal, {obj.name}!</h1>
    <p style="margin:0 auto;color:#475569;font-size:14px;line-height:1.7;max-width:460px;">
      Your request for <strong style="color:#1E293B;">{obj.business_name}</strong> has been received.
      Here are your <strong style="color:#6366F1;">3 custom design templates</strong> — your selected one is highlighted in indigo.
    </p>
  </td></tr>

  <!-- Request summary -->
  <tr><td style="padding:24px 40px 0;">
    <h2 style="margin:0 0 12px;color:#1E293B;font-size:13px;font-weight:700;text-transform:uppercase;
               letter-spacing:1px;border-bottom:2px solid #4F46E5;padding-bottom:7px;display:inline-block;">
      Your Request Summary
    </h2>
    <table width="100%" cellpadding="0" cellspacing="0" border="0"
           style="background:#FAFBFF;border-radius:8px;border:1px solid #E2E8F0;overflow:hidden;">
      <tr>
        <td style="padding:9px 14px;color:#64748B;font-size:12px;font-weight:600;width:40%;border-bottom:1px solid #E2E8F0;">Name</td>
        <td style="padding:9px 14px;color:#1E293B;font-size:12px;font-weight:700;border-bottom:1px solid #E2E8F0;">{obj.name}</td>
      </tr>
      <tr style="background:#ffffff;">
        <td style="padding:9px 14px;color:#64748B;font-size:12px;font-weight:600;border-bottom:1px solid #E2E8F0;">Business</td>
        <td style="padding:9px 14px;color:#1E293B;font-size:12px;font-weight:700;border-bottom:1px solid #E2E8F0;">{obj.business_name}</td>
      </tr>
      <tr>
        <td style="padding:9px 14px;color:#64748B;font-size:12px;font-weight:600;border-bottom:1px solid #E2E8F0;">Website Type</td>
        <td style="padding:9px 14px;color:#1E293B;font-size:12px;font-weight:700;border-bottom:1px solid #E2E8F0;">{obj.get_website_type_display()}</td>
      </tr>
      {'<tr style="background:#ffffff;"><td style="padding:9px 14px;color:#64748B;font-size:12px;font-weight:600;border-bottom:1px solid #E2E8F0;">Selected Plan</td><td style="padding:9px 14px;color:#4F46E5;font-size:12px;font-weight:700;border-bottom:1px solid #E2E8F0;">' + obj.selected_plan + '</td></tr>' if obj.selected_plan else ''}
      <tr>
        <td style="padding:9px 14px;color:#64748B;font-size:12px;font-weight:600;border-bottom:1px solid #E2E8F0;">Budget</td>
        <td style="padding:9px 14px;color:#1E293B;font-size:12px;font-weight:700;border-bottom:1px solid #E2E8F0;">{obj.get_budget_display()}</td>
      </tr>
      <tr style="background:#ffffff;">
        <td style="padding:9px 14px;color:#64748B;font-size:12px;font-weight:600;">Selected Template</td>
        <td style="padding:9px 14px;color:#4F46E5;font-size:13px;font-weight:800;">{selected_name} — {selected_style}</td>
      </tr>
    </table>
  </td></tr>

  <tr><td style="padding:24px 40px 0;">
    <h2 style="margin:0 0 14px;color:#1E293B;font-size:13px;font-weight:700;text-transform:uppercase;
               letter-spacing:1px;border-bottom:2px solid #4F46E5;padding-bottom:7px;display:inline-block;">
      Your Selected Design Template
    </h2>
    {cards_html}
  </td></tr>

  <tr><td style="padding:20px 40px 0;">
    <h2 style="margin:0 0 14px;color:#1E293B;font-size:13px;font-weight:700;text-transform:uppercase;
               letter-spacing:1px;border-bottom:2px solid #4F46E5;padding-bottom:7px;display:inline-block;">
      What Happens Next?
    </h2>
    <table width="100%" cellpadding="0" cellspacing="0" border="0">
      <tr>
        <td width="38" style="vertical-align:top;padding-right:12px;padding-bottom:12px;">
          <div style="width:30px;height:30px;background:#4F46E5;border-radius:50%;text-align:center;line-height:30px;color:#fff;font-weight:800;font-size:12px;">1</div>
        </td>
        <td style="vertical-align:top;padding-bottom:12px;">
          <div style="color:#1E293B;font-size:13px;font-weight:700;">Design Customisation</div>
          <div style="color:#475569;font-size:12px;line-height:1.5;">Our team customises the <strong>{selected_name}</strong> template with your brand colors and content.</div>
        </td>
      </tr>
      <tr>
        <td width="38" style="vertical-align:top;padding-right:12px;padding-bottom:12px;">
          <div style="width:30px;height:30px;background:#4F46E5;border-radius:50%;text-align:center;line-height:30px;color:#fff;font-weight:800;font-size:12px;">2</div>
        </td>
        <td style="vertical-align:top;padding-bottom:12px;">
          <div style="color:#1E293B;font-size:13px;font-weight:700;">Consultation Call</div>
          <div style="color:#475569;font-size:12px;line-height:1.5;">We contact you within <strong>24 hours</strong> to finalise content, features, and timeline.</div>
        </td>
      </tr>
      <tr>
        <td width="38" style="vertical-align:top;padding-right:12px;">
          <div style="width:30px;height:30px;background:#4F46E5;border-radius:50%;text-align:center;line-height:30px;color:#fff;font-weight:800;font-size:12px;">3</div>
        </td>
        <td style="vertical-align:top;">
          <div style="color:#1E293B;font-size:13px;font-weight:700;">Development Begins</div>
          <div style="color:#475569;font-size:12px;line-height:1.5;">We build your website and send regular progress updates until delivery.</div>
        </td>
      </tr>
    </table>
  </td></tr>

  <tr><td style="padding:28px 40px;text-align:center;">
    <a href="https://wa.me/917892934437?text=Hi%20Weblance!%20I%20selected%20the%20{selected_name.replace(' ','%20')}%20template%20for%20{obj.business_name.replace(' ','%20')}"
       style="display:inline-block;background:linear-gradient(135deg,#6366F1,#4F46E5);color:#fff;font-weight:800;font-size:14px;padding:12px 32px;border-radius:50px;text-decoration:none;margin:4px;">
      💬 Chat on WhatsApp
    </a>
    <a href="tel:+917892934437"
       style="display:inline-block;background:#ffffff;color:#1E293B;font-weight:700;font-size:14px;padding:12px 24px;border-radius:50px;text-decoration:none;border:1.5px solid #C7D2FE;margin:4px;">
      📞 +91 7892934437
    </a>
  </td></tr>

  <tr><td style="background:linear-gradient(135deg,#6366F1,#4F46E5);padding:20px 40px;text-align:center;border-top:1px solid rgba(255,255,255,.1);">
    <p style="margin:0 0 5px;color:#fff;font-size:13px;font-weight:700;letter-spacing:1px;">WEB<span style="color:#fff;opacity:.85;">LANCE</span></p>
    <p style="margin:0;color:rgba(255,255,255,.6);font-size:11px;">Devanahalli, Karnataka, India &nbsp;|&nbsp; infoweblance01@gmail.com &nbsp;|&nbsp; +91 7892934437</p>
  </td></tr>

</table>
</td></tr>
</table>
</body>
</html>"""

    plain = (
        f"Hi {obj.name},\n\n"
        f"Thank you for your request! Here is your complete website proposal.\n\n"
        f"REQUEST SUMMARY\n"
        f"{'='*40}\n"
        f"Business  : {obj.business_name}\n"
        f"Type      : {obj.get_website_type_display()}\n"
        f"Budget    : {obj.get_budget_display()}\n"
        f"Plan      : {obj.selected_plan or '—'}\n"
        f"Selected  : {selected_name} ({selected_style})\n\n"
        f"ALL 3 DESIGN TEMPLATES\n"
        f"{'='*40}\n"
    )
    for t in all_templates:
        mark = ' <-- YOUR CHOICE' if t['selected'] else ''
        plain += f"\n{t['id']}. {t['name']} ({t['style']}){mark}\n   Headline : {t['headline']}\n   CTA      : {t['cta']}\n"
    plain += (
        f"\nNEXT STEPS\n{'='*40}\n"
        f"1. Our team customises the {selected_name} template for your brand\n"
        f"2. We contact you within 24 hours to finalise details\n"
        f"3. Development begins after your approval\n\n"
        f"WhatsApp : wa.me/917892934437\n"
        f"Phone    : +91 7892934437\n"
        f"Email    : infoweblance01@gmail.com\n\n"
        f"— Weblance Team"
    )

    plain_admin = (
        f"Template Selected — Client Proposal Email Sent\n\n"
        f"Business : {obj.business_name}\n"
        f"Client   : {obj.name} <{obj.email}>\n"
        f"Phone    : {obj.phone}\n"
        f"Type     : {obj.get_website_type_display()}\n"
        f"Selected : {selected_name} ({selected_style})\n"
        f"Budget   : {obj.get_budget_display()}\n"
        f"Plan     : {obj.selected_plan or '—'}\n\n"
        f"Description:\n{obj.description[:400]}"
    )

    try:
        msg = EmailMultiAlternatives(
            subject=f'Your Website Proposal — {obj.business_name} | Weblance',
            body=plain,
            from_email='Weblance <infoweblance01@gmail.com>',
            to=[obj.email],
        )
        msg.attach_alternative(html, 'text/html')
        msg.send(fail_silently=False)

        send_mail(
            subject=f'[Template Selected] {obj.business_name} — {selected_name}',
            message=plain_admin,
            from_email='Weblance <infoweblance01@gmail.com>',
            recipient_list=['infoweblance01@gmail.com'],
            fail_silently=False,
        )
        logger.info(f'Proposal email sent to {obj.email}')
    except Exception as e:
        logger.error(f'Proposal email failed: {e}')


from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

# Map service slug → website_type choice
SERVICE_TYPE_MAP = {
    'custom-website':   'custom',
    'ecommerce':        'ecommerce',
    'seo-optimization': 'custom',
    'web-design':       'custom',
    'redesign':         'custom',
    'maintenance':      'custom',
}

SERVICE_LABEL_MAP = {
    'custom-website':   'Custom Website Development',
    'ecommerce':        'E-Commerce Development',
    'seo-optimization': 'SEO Optimization',
    'web-design':       'Web Design',
    'redesign':         'Website Redesign',
    'maintenance':      'Website Maintenance',
}


def service_quote(request):
    """Handle inline quote form on the services page. No login required."""
    if request.method != 'POST':
        return JsonResponse({'ok': False, 'error': 'Method not allowed'}, status=405)

    name          = request.POST.get('name', '').strip()
    business_name = request.POST.get('business_name', '').strip()
    phone         = request.POST.get('phone', '').strip()
    email         = request.POST.get('email', '').strip()
    budget        = request.POST.get('budget', 'medium').strip()
    description   = request.POST.get('description', '').strip()
    service_slug  = request.POST.get('service_slug', '').strip()

    # If user is logged in and email not provided, use their account email
    if not email and request.user.is_authenticated:
        email = request.user.email
    if not name and request.user.is_authenticated:
        name = request.user.get_full_name() or request.user.username

    # Basic validation
    errors = {}
    if not name:          errors['name']          = 'Name is required.'
    if not business_name: errors['business_name'] = 'Business name is required.'
    if not phone:         errors['phone']         = 'Phone is required.'
    if not email:         errors['email']         = 'Email is required.'
    if not description:   errors['description']   = 'Please describe your project.'
    if errors:
        return JsonResponse({'ok': False, 'errors': errors}, status=400)

    website_type  = SERVICE_TYPE_MAP.get(service_slug, 'custom')
    service_label = SERVICE_LABEL_MAP.get(service_slug, 'Website Service')

    obj = WebsiteRequest.objects.create(
        name=name,
        business_name=business_name,
        phone=phone,
        email=email,
        website_type=website_type,
        budget=budget,
        selected_plan=service_label,
        description=f"[Service: {service_label}]\n\n{description}",
        status='new',
    )

    # Send greeting to client
    _send_service_greeting(obj)
    # Notify admin
    _send_admin_notification(obj)

    # If user is logged in, redirect to their dashboard after success
    dashboard_url = '/panel/projects/' if request.user.is_authenticated else None

    return JsonResponse({
        'ok': True,
        'dashboard_url': dashboard_url,
        'message': f"Thank you, {name}! We've received your quote request for <strong>{service_label}</strong>. Check your email — we'll be in touch within 24 hours."
    })
