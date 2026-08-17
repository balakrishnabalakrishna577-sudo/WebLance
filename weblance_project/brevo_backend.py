"""
weblance_project/brevo_backend.py
──────────────────────────────────
Custom Django email backend using Brevo REST API (HTTPS port 443).
Bypasses all SMTP port restrictions on Render free tier.

Usage in settings.py:
    EMAIL_BACKEND = 'weblance_project.brevo_backend.BrevoAPIBackend'
    BREVO_API_KEY = os.environ.get('BREVO_API_KEY', '')
"""

import json
import logging
import urllib.request
import urllib.error
from email.mime.base import MIMEBase
from django.core.mail.backends.base import BaseEmailBackend
from django.conf import settings

logger = logging.getLogger(__name__)

BREVO_API_URL = 'https://api.brevo.com/v3/smtp/email'


def _get_api_key():
    return getattr(settings, 'BREVO_API_KEY', '')


class BrevoAPIBackend(BaseEmailBackend):
    """
    Django email backend that sends via Brevo REST API.
    Works on Render free tier — uses HTTPS port 443 only.
    """

    def open(self):
        return True

    def close(self):
        pass

    def send_messages(self, email_messages):
        if not email_messages:
            return 0

        api_key = _get_api_key()
        if not api_key:
            logger.error('BrevoAPIBackend: BREVO_API_KEY is not set.')
            if self.fail_silently:
                return 0
            raise RuntimeError('BREVO_API_KEY is not configured.')

        sent = 0
        for msg in email_messages:
            try:
                if self._send(msg, api_key):
                    sent += 1
            except Exception as exc:
                logger.error('BrevoAPIBackend: send failed — %s', exc)
                if not self.fail_silently:
                    raise
        return sent

    def _send(self, msg, api_key):
        # ── Recipients ──────────────────────────────────────────────
        to_list = [{'email': addr} for addr in (msg.to or [])]
        if not to_list:
            return False

        # ── Sender ──────────────────────────────────────────────────
        from_email = msg.from_email or getattr(settings, 'DEFAULT_FROM_EMAIL', '')
        if '<' in from_email and '>' in from_email:
            name_part, addr_part = from_email.split('<', 1)
            sender = {
                'name':  name_part.strip().strip('"'),
                'email': addr_part.strip().rstrip('>'),
            }
        else:
            sender = {'name': 'Weblance', 'email': from_email.strip()}

        # ── Body ────────────────────────────────────────────────────
        html_body  = None
        plain_body = msg.body or ''

        # Check for HTML alternative
        if hasattr(msg, 'alternatives'):
            for content, mimetype in msg.alternatives:
                if mimetype == 'text/html':
                    html_body = content
                    break

        payload = {
            'sender':      sender,
            'to':          to_list,
            'subject':     msg.subject or '(no subject)',
            'textContent': plain_body,
        }
        if html_body:
            payload['htmlContent'] = html_body

        # ── CC / BCC ─────────────────────────────────────────────────
        if msg.cc:
            payload['cc'] = [{'email': a} for a in msg.cc]
        if msg.bcc:
            payload['bcc'] = [{'email': a} for a in msg.bcc]

        # ── Attachments ──────────────────────────────────────────────
        if msg.attachments:
            import base64
            attachments = []
            for att in msg.attachments:
                if isinstance(att, MIMEBase):
                    content = att.get_payload(decode=True)
                    name    = att.get_filename() or 'attachment'
                elif isinstance(att, tuple) and len(att) >= 2:
                    name, content = att[0], att[1]
                    if isinstance(content, str):
                        content = content.encode()
                else:
                    continue
                attachments.append({
                    'name':    name,
                    'content': base64.b64encode(content).decode(),
                })
            if attachments:
                payload['attachment'] = attachments

        # ── Send ─────────────────────────────────────────────────────
        data = json.dumps(payload).encode('utf-8')
        req  = urllib.request.Request(
            BREVO_API_URL,
            data=data,
            headers={
                'accept':       'application/json',
                'api-key':      api_key,
                'content-type': 'application/json',
            },
            method='POST',
        )

        try:
            resp   = urllib.request.urlopen(req, timeout=20)
            result = json.loads(resp.read().decode())
            logger.info('BrevoAPIBackend: sent to %s — messageId=%s',
                        [a['email'] for a in to_list],
                        result.get('messageId', '?'))
            return True
        except urllib.error.HTTPError as e:
            body = e.read().decode()
            logger.error('BrevoAPIBackend: HTTP %s — %s', e.code, body)
            raise RuntimeError(f'Brevo API error {e.code}: {body}')
