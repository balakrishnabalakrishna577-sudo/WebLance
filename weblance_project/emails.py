"""
weblance_project/emails.py
──────────────────────────
Central email helpers for WEBLANCE.
All outgoing transactional emails are defined here so the HTML template
stays consistent and is easy to update in one place.

Usage:
    from weblance_project.emails import send_welcome, send_booking_confirmation, \
        send_project_update, send_project_status_change
"""

import logging
from django.core.mail import EmailMultiAlternatives
from django.conf import settings

logger = logging.getLogger(__name__)

FROM_EMAIL  = 'Weblance <infoweblance01@gmail.com>'
SITE_URL    = getattr(settings, 'SITE_URL', 'https://weblancehub.in')
DASHBOARD_URL = f'{SITE_URL}/panel/projects/'
WA_LINK     = 'https://wa.me/917892934437'


# ── Internal HTML building blocks ─────────────────────────────────

def _header():
    return """
    <tr>
      <td style="background:linear-gradient(135deg,#6366F1,#4F46E5);
                 padding:22px 40px;text-align:center;">
        <span style="font-size:20px;font-weight:900;letter-spacing:3px;
                     color:#fff;text-transform:uppercase;">
          WEB<span style="opacity:.85">LANCE</span>
        </span>
      </td>
    </tr>
    <tr>
      <td style="height:4px;background:linear-gradient(90deg,#4F46E5,#6366F1,#818CF8);"></td>
    </tr>"""


def _footer():
    return f"""
    <tr>
      <td style="background:linear-gradient(135deg,#6366F1,#4F46E5);
                 padding:20px 40px;text-align:center;border-top:1px solid rgba(255,255,255,.1);">
        <p style="margin:0 0 4px;color:#fff;font-size:13px;font-weight:700;
                  letter-spacing:1px;">WEBLANCE</p>
        <p style="margin:0;color:rgba(255,255,255,.65);font-size:11px;">
          Devanahalli, Karnataka, India &nbsp;|&nbsp;
          infoweblance01@gmail.com &nbsp;|&nbsp; +91 7892934437
        </p>
      </td>
    </tr>"""


def _wrap(body_rows: str) -> str:
    """Wrap body rows in the full responsive email shell."""
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width,initial-scale=1">
</head>
<body style="margin:0;padding:0;background:#f4f6fb;
             font-family:'Segoe UI',Helvetica,Arial,sans-serif;">
<table width="100%" cellpadding="0" cellspacing="0" border="0"
       style="background:#f4f6fb;padding:40px 0;">
  <tr><td align="center">
    <table width="600" cellpadding="0" cellspacing="0" border="0"
           style="max-width:600px;width:100%;background:#ffffff;
                  border-radius:12px;overflow:hidden;
                  box-shadow:0 4px 24px rgba(0,0,0,.10);">
      {_header()}
      {body_rows}
      {_footer()}
    </table>
  </td></tr>
</table>
</body>
</html>"""


def _send(subject: str, html: str, plain: str, to: list[str]) -> bool:
    """Send one email. Returns True on success, False on failure."""
    if not to or not any(to):
        return False
    try:
        msg = EmailMultiAlternatives(
            subject=subject,
            body=plain,
            from_email=FROM_EMAIL,
            to=to,
        )
        msg.attach_alternative(html, 'text/html')
        msg.send(fail_silently=False)
        logger.info('Email sent to %s — %s', to, subject)
        return True
    except Exception as exc:
        logger.error('Email failed to %s — %s — %s', to, subject, exc)
        return False


# ══════════════════════════════════════════════════════════════════
# 1.  WELCOME EMAIL  (sent once on first login)
# ══════════════════════════════════════════════════════════════════

def send_welcome(user) -> bool:
    """Send a welcome email to a newly-registered / first-login user."""
    if not user.email:
        return False

    name = user.get_full_name() or user.username
    body = f"""
    <tr>
      <td style="background:#F8F9FF;padding:40px;text-align:center;
                 border-bottom:1px solid #E2E8F0;">
        <div style="font-size:48px;margin-bottom:14px;">🎉</div>
        <h1 style="margin:0 0 12px;color:#1E293B;font-size:24px;font-weight:900;">
          Welcome to WEBLANCE, {name}!
        </h1>
        <p style="margin:0 auto;color:#475569;font-size:15px;line-height:1.7;
                  max-width:440px;">
          We're thrilled to have you on board. Your account is ready —
          explore your dashboard, track your projects, and reach out to us anytime.
        </p>
      </td>
    </tr>
    <tr>
      <td style="padding:32px 40px;">
        <h2 style="margin:0 0 16px;font-size:13px;font-weight:700;
                   text-transform:uppercase;letter-spacing:1px;color:#0f172a;
                   border-bottom:2px solid #4F46E5;padding-bottom:8px;
                   display:inline-block;">
          What You Can Do
        </h2>
        <table width="100%" cellpadding="0" cellspacing="0" border="0">
          <tr>
            <td width="40" style="vertical-align:top;padding-right:14px;padding-bottom:14px;">
              <div style="width:32px;height:32px;background:#EEF2FF;border-radius:50%;
                          text-align:center;line-height:32px;font-size:16px;">📊</div>
            </td>
            <td style="vertical-align:top;padding-bottom:14px;">
              <div style="color:#1E293B;font-size:13px;font-weight:700;margin-bottom:3px;">
                Track Your Projects
              </div>
              <div style="color:#475569;font-size:12px;line-height:1.6;">
                Monitor progress, view updates, and download files in real time.
              </div>
            </td>
          </tr>
          <tr>
            <td width="40" style="vertical-align:top;padding-right:14px;padding-bottom:14px;">
              <div style="width:32px;height:32px;background:#F0FDF4;border-radius:50%;
                          text-align:center;line-height:32px;font-size:16px;">💬</div>
            </td>
            <td style="vertical-align:top;padding-bottom:14px;">
              <div style="color:#1E293B;font-size:13px;font-weight:700;margin-bottom:3px;">
                Chat Directly With Our Team
              </div>
              <div style="color:#475569;font-size:12px;line-height:1.6;">
                Ask questions and share feedback through our built-in project chat.
              </div>
            </td>
          </tr>
          <tr>
            <td width="40" style="vertical-align:top;padding-right:14px;">
              <div style="width:32px;height:32px;background:#FEF9C3;border-radius:50%;
                          text-align:center;line-height:32px;font-size:16px;">📅</div>
            </td>
            <td style="vertical-align:top;">
              <div style="color:#1E293B;font-size:13px;font-weight:700;margin-bottom:3px;">
                Book a Free Consultation
              </div>
              <div style="color:#475569;font-size:12px;line-height:1.6;">
                Schedule a call with our team to discuss your requirements.
              </div>
            </td>
          </tr>
        </table>
      </td>
    </tr>
    <tr>
      <td style="padding:0 40px 32px;text-align:center;">
        <a href="{DASHBOARD_URL}"
           style="display:inline-block;background:linear-gradient(135deg,#6366F1,#4F46E5);
                  color:#fff;font-weight:800;font-size:14px;padding:13px 32px;
                  border-radius:50px;text-decoration:none;margin:4px;">
          🚀 Go to My Dashboard
        </a>
        <a href="{WA_LINK}"
           style="display:inline-block;background:#fff;color:#1E293B;font-weight:700;
                  font-size:14px;padding:13px 24px;border-radius:50px;text-decoration:none;
                  border:1.5px solid #C7D2FE;margin:4px;">
          💬 WhatsApp Us
        </a>
      </td>
    </tr>"""

    plain = (
        f"Hi {name},\n\n"
        f"Welcome to WEBLANCE! Your account is ready.\n\n"
        f"Dashboard : {DASHBOARD_URL}\n"
        f"WhatsApp  : {WA_LINK}\n"
        f"Phone     : +91 7892934437\n"
        f"Email     : infoweblance01@gmail.com\n\n"
        f"— Weblance Team"
    )

    return _send(
        subject=f'Welcome to WEBLANCE, {name}! 🎉',
        html=_wrap(body),
        plain=plain,
        to=[user.email],
    )


# ══════════════════════════════════════════════════════════════════
# 2.  BOOKING CONFIRMATION EMAIL
# ══════════════════════════════════════════════════════════════════

def send_booking_confirmation(booking) -> bool:
    """Send HTML booking confirmation to the client."""
    slot   = booking.slot
    name   = booking.name
    email  = booking.email
    if not email:
        return False

    svc_line = f'<br><strong>Service:</strong> {booking.service}' if booking.service else ''
    mtg_line = (
        f'<br><strong>Meeting Link:</strong> '
        f'<a href="{booking.meeting_link}" style="color:#6366F1;">{booking.meeting_link}</a>'
        if booking.meeting_link else ''
    )

    body = f"""
    <tr>
      <td style="background:#F8F9FF;padding:36px 40px;text-align:center;
                 border-bottom:1px solid #E2E8F0;">
        <div style="font-size:48px;margin-bottom:12px;">📅</div>
        <h1 style="margin:0 0 10px;color:#1E293B;font-size:22px;font-weight:900;">
          Booking Confirmed, {name}!
        </h1>
        <p style="margin:0 auto;color:#475569;font-size:14px;line-height:1.7;
                  max-width:440px;">
          Your consultation call with <strong style="color:#6366F1;">WEBLANCE</strong>
          is booked. We look forward to speaking with you!
        </p>
      </td>
    </tr>
    <tr>
      <td style="padding:28px 40px 0;">
        <h2 style="margin:0 0 14px;font-size:13px;font-weight:700;
                   text-transform:uppercase;letter-spacing:1px;color:#0f172a;
                   border-bottom:2px solid #4F46E5;padding-bottom:8px;
                   display:inline-block;">Booking Details</h2>
        <table width="100%" cellpadding="0" cellspacing="0" border="0"
               style="background:#FAFBFF;border-radius:10px;
                      border:1px solid #E2E8F0;overflow:hidden;">
          <tr>
            <td style="padding:10px 16px;color:#64748B;font-size:12px;
                       font-weight:600;width:40%;border-bottom:1px solid #E2E8F0;">Date</td>
            <td style="padding:10px 16px;color:#1E293B;font-size:12px;
                       font-weight:700;border-bottom:1px solid #E2E8F0;">
              {slot.date.strftime('%A, %d %B %Y')}
            </td>
          </tr>
          <tr style="background:#fff;">
            <td style="padding:10px 16px;color:#64748B;font-size:12px;
                       font-weight:600;border-bottom:1px solid #E2E8F0;">Time</td>
            <td style="padding:10px 16px;color:#1E293B;font-size:12px;
                       font-weight:700;border-bottom:1px solid #E2E8F0;">
              {slot.start_time.strftime('%I:%M %p')} – {slot.end_time.strftime('%I:%M %p')} IST
            </td>
          </tr>
          <tr>
            <td style="padding:10px 16px;color:#64748B;font-size:12px;
                       font-weight:600;border-bottom:1px solid #E2E8F0;">Name</td>
            <td style="padding:10px 16px;color:#1E293B;font-size:12px;
                       font-weight:700;border-bottom:1px solid #E2E8F0;">{name}</td>
          </tr>
          <tr style="background:#fff;">
            <td style="padding:10px 16px;color:#64748B;font-size:12px;
                       font-weight:600;">Service</td>
            <td style="padding:10px 16px;color:#4F46E5;font-size:12px;
                       font-weight:800;">
              {booking.service or 'General Consultation'}
            </td>
          </tr>
          {"<tr><td style='padding:10px 16px;color:#64748B;font-size:12px;font-weight:600;border-top:1px solid #E2E8F0;'>Meeting Link</td><td style='padding:10px 16px;font-size:12px;font-weight:700;border-top:1px solid #E2E8F0;'><a href='" + booking.meeting_link + "' style='color:#6366F1;'>" + booking.meeting_link + "</a></td></tr>" if booking.meeting_link else ""}
        </table>
      </td>
    </tr>
    <tr>
      <td style="padding:20px 40px 0;">
        <div style="background:#EEF2FF;border-radius:10px;padding:14px 18px;
                    border-left:4px solid #6366F1;">
          <p style="margin:0;color:#4F46E5;font-size:13px;font-weight:600;">
            📌 We'll send you the meeting link before the call.
            If you need to reschedule, reach out on WhatsApp or call us directly.
          </p>
        </div>
      </td>
    </tr>
    <tr>
      <td style="padding:28px 40px;text-align:center;">
        <a href="{WA_LINK}"
           style="display:inline-block;background:linear-gradient(135deg,#6366F1,#4F46E5);
                  color:#fff;font-weight:800;font-size:14px;padding:12px 28px;
                  border-radius:50px;text-decoration:none;margin:4px;">
          💬 WhatsApp Us
        </a>
        <a href="tel:+917892934437"
           style="display:inline-block;background:#fff;color:#1E293B;font-weight:700;
                  font-size:14px;padding:12px 22px;border-radius:50px;text-decoration:none;
                  border:1.5px solid #C7D2FE;margin:4px;">
          📞 +91 7892934437
        </a>
      </td>
    </tr>"""

    plain = (
        f"Hi {name},\n\n"
        f"Your consultation call with WEBLANCE is confirmed!\n\n"
        f"DATE   : {slot.date.strftime('%A, %d %B %Y')}\n"
        f"TIME   : {slot.start_time.strftime('%I:%M %p')} – {slot.end_time.strftime('%I:%M %p')} IST\n"
        f"SERVICE: {booking.service or 'General Consultation'}\n"
        + (f"LINK   : {booking.meeting_link}\n" if booking.meeting_link else "") +
        f"\nWe will send you the meeting link before the call.\n"
        f"WhatsApp : {WA_LINK}\n"
        f"Phone    : +91 7892934437\n\n"
        f"— Weblance Team"
    )

    return _send(
        subject='Consultation Booking Confirmed — WEBLANCE 📅',
        html=_wrap(body),
        plain=plain,
        to=[email],
    )


# ══════════════════════════════════════════════════════════════════
# 3.  PROJECT UPDATE EMAIL  (admin pushes a text update)
# ══════════════════════════════════════════════════════════════════

def send_project_update(project, update_message: str) -> bool:
    """Email the client when admin adds a project update."""
    client = project.client
    if not client.email:
        return False

    name = client.get_full_name() or client.username
    short = (update_message[:160] + '…') if len(update_message) > 160 else update_message
    proj_url = f'{SITE_URL}/panel/projects/project/{project.pk}/'

    body = f"""
    <tr>
      <td style="background:#F8F9FF;padding:36px 40px;text-align:center;
                 border-bottom:1px solid #E2E8F0;">
        <div style="font-size:44px;margin-bottom:12px;">📢</div>
        <h1 style="margin:0 0 10px;color:#1E293B;font-size:22px;font-weight:900;">
          New Update on Your Project
        </h1>
        <p style="margin:0 auto;color:#475569;font-size:14px;line-height:1.7;
                  max-width:440px;">
          Hi <strong>{name}</strong>, your Weblance team just posted a new update
          on <strong style="color:#6366F1;">{project.title}</strong>.
        </p>
      </td>
    </tr>
    <tr>
      <td style="padding:28px 40px 0;">
        <h2 style="margin:0 0 12px;font-size:13px;font-weight:700;
                   text-transform:uppercase;letter-spacing:1px;color:#0f172a;
                   border-bottom:2px solid #4F46E5;padding-bottom:8px;
                   display:inline-block;">Project Update</h2>
        <div style="background:#FAFBFF;border:1px solid #E2E8F0;border-radius:10px;
                    padding:18px 20px;border-left:4px solid #6366F1;">
          <p style="margin:0;color:#1E293B;font-size:14px;line-height:1.75;
                    white-space:pre-wrap;">{update_message}</p>
        </div>
      </td>
    </tr>
    <tr>
      <td style="padding:20px 40px 0;">
        <table width="100%" cellpadding="0" cellspacing="0" border="0"
               style="background:#FAFBFF;border-radius:10px;
                      border:1px solid #E2E8F0;overflow:hidden;">
          <tr>
            <td style="padding:10px 16px;color:#64748B;font-size:12px;
                       font-weight:600;width:40%;border-bottom:1px solid #E2E8F0;">
              Project
            </td>
            <td style="padding:10px 16px;color:#1E293B;font-size:12px;
                       font-weight:700;border-bottom:1px solid #E2E8F0;">
              {project.title}
            </td>
          </tr>
          <tr style="background:#fff;">
            <td style="padding:10px 16px;color:#64748B;font-size:12px;
                       font-weight:600;border-bottom:1px solid #E2E8F0;">Status</td>
            <td style="padding:10px 16px;color:#4F46E5;font-size:12px;
                       font-weight:800;border-bottom:1px solid #E2E8F0;">
              {project.get_status_display()}
            </td>
          </tr>
          <tr>
            <td style="padding:10px 16px;color:#64748B;font-size:12px;
                       font-weight:600;">Progress</td>
            <td style="padding:10px 16px;color:#1E293B;font-size:12px;
                       font-weight:700;">{project.progress}%</td>
          </tr>
        </table>
      </td>
    </tr>
    <tr>
      <td style="padding:28px 40px;text-align:center;">
        <a href="{proj_url}"
           style="display:inline-block;background:linear-gradient(135deg,#6366F1,#4F46E5);
                  color:#fff;font-weight:800;font-size:14px;padding:12px 32px;
                  border-radius:50px;text-decoration:none;margin:4px;">
          📊 View My Project
        </a>
        <a href="{WA_LINK}"
           style="display:inline-block;background:#fff;color:#1E293B;font-weight:700;
                  font-size:14px;padding:12px 22px;border-radius:50px;text-decoration:none;
                  border:1.5px solid #C7D2FE;margin:4px;">
          💬 WhatsApp Us
        </a>
      </td>
    </tr>"""

    plain = (
        f"Hi {name},\n\n"
        f"New update on your project '{project.title}':\n\n"
        f"{update_message}\n\n"
        f"Status   : {project.get_status_display()}\n"
        f"Progress : {project.progress}%\n"
        f"Dashboard: {proj_url}\n\n"
        f"— Weblance Team"
    )

    return _send(
        subject=f'Project Update: {project.title} — WEBLANCE',
        html=_wrap(body),
        plain=plain,
        to=[client.email],
    )


# ══════════════════════════════════════════════════════════════════
# 4.  PROJECT STATUS CHANGE EMAIL
# ══════════════════════════════════════════════════════════════════

def send_project_status_change(project, old_status: str) -> bool:
    """Email the client when admin changes project status."""
    client = project.client
    if not client.email:
        return False

    name      = client.get_full_name() or client.username
    new_label = project.get_status_display()
    old_label = dict(project.STATUS_CHOICES).get(old_status, old_status)
    proj_url  = f'{SITE_URL}/panel/projects/project/{project.pk}/'

    # Icon per status
    icons = {
        'planning':    '📋',
        'design':      '🎨',
        'development': '⚙️',
        'testing':     '🔍',
        'delivered':   '🚀',
    }
    icon = icons.get(project.status, '📌')

    congrats = ''
    if project.status == 'delivered':
        congrats = """
        <tr>
          <td style="padding:0 40px 20px;">
            <div style="background:#F0FDF4;border:1px solid #BBF7D0;border-radius:10px;
                        padding:16px 20px;border-left:4px solid #22C55E;text-align:center;">
              <p style="margin:0;color:#15803D;font-size:14px;font-weight:700;">
                🎉 Congratulations! Your project has been delivered.
                Please log in to review and leave feedback.
              </p>
            </div>
          </td>
        </tr>"""

    body = f"""
    <tr>
      <td style="background:#F8F9FF;padding:36px 40px;text-align:center;
                 border-bottom:1px solid #E2E8F0;">
        <div style="font-size:48px;margin-bottom:12px;">{icon}</div>
        <h1 style="margin:0 0 10px;color:#1E293B;font-size:22px;font-weight:900;">
          Project Status Updated
        </h1>
        <p style="margin:0 auto;color:#475569;font-size:14px;line-height:1.7;
                  max-width:440px;">
          Hi <strong>{name}</strong>, the status of your project
          <strong style="color:#6366F1;">{project.title}</strong> has been updated.
        </p>
      </td>
    </tr>
    <tr>
      <td style="padding:28px 40px 0;">
        <table width="100%" cellpadding="0" cellspacing="0" border="0"
               style="background:#FAFBFF;border-radius:10px;
                      border:1px solid #E2E8F0;overflow:hidden;">
          <tr>
            <td style="padding:10px 16px;color:#64748B;font-size:12px;
                       font-weight:600;width:40%;border-bottom:1px solid #E2E8F0;">Project</td>
            <td style="padding:10px 16px;color:#1E293B;font-size:12px;
                       font-weight:700;border-bottom:1px solid #E2E8F0;">{project.title}</td>
          </tr>
          <tr style="background:#fff;">
            <td style="padding:10px 16px;color:#64748B;font-size:12px;
                       font-weight:600;border-bottom:1px solid #E2E8F0;">Previous Status</td>
            <td style="padding:10px 16px;color:#94A3B8;font-size:12px;
                       font-weight:600;border-bottom:1px solid #E2E8F0;">{old_label}</td>
          </tr>
          <tr>
            <td style="padding:10px 16px;color:#64748B;font-size:12px;
                       font-weight:600;border-bottom:1px solid #E2E8F0;">New Status</td>
            <td style="padding:10px 16px;color:#4F46E5;font-size:13px;
                       font-weight:800;border-bottom:1px solid #E2E8F0;">{icon} {new_label}</td>
          </tr>
          <tr style="background:#fff;">
            <td style="padding:10px 16px;color:#64748B;font-size:12px;
                       font-weight:600;">Progress</td>
            <td style="padding:10px 16px;color:#1E293B;font-size:12px;
                       font-weight:700;">{project.progress}%</td>
          </tr>
        </table>
      </td>
    </tr>
    {congrats}
    <tr>
      <td style="padding:28px 40px;text-align:center;">
        <a href="{proj_url}"
           style="display:inline-block;background:linear-gradient(135deg,#6366F1,#4F46E5);
                  color:#fff;font-weight:800;font-size:14px;padding:12px 32px;
                  border-radius:50px;text-decoration:none;margin:4px;">
          📊 View My Project
        </a>
        <a href="{WA_LINK}"
           style="display:inline-block;background:#fff;color:#1E293B;font-weight:700;
                  font-size:14px;padding:12px 22px;border-radius:50px;text-decoration:none;
                  border:1.5px solid #C7D2FE;margin:4px;">
          💬 WhatsApp Us
        </a>
      </td>
    </tr>"""

    plain = (
        f"Hi {name},\n\n"
        f"The status of your project '{project.title}' has been updated.\n\n"
        f"Previous : {old_label}\n"
        f"New      : {new_label}\n"
        f"Progress : {project.progress}%\n"
        f"Dashboard: {proj_url}\n\n"
        + ("Congratulations! Your project has been delivered. Please log in to review it.\n\n"
           if project.status == 'delivered' else "") +
        f"— Weblance Team"
    )

    return _send(
        subject=f'Project Status: {project.title} → {new_label} — WEBLANCE',
        html=_wrap(body),
        plain=plain,
        to=[client.email],
    )
