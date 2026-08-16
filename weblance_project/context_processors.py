from django.conf import settings
from django.db.models import Q
from django.utils import timezone


def recaptcha_key(request):
    return {
        'RECAPTCHA_SITE_KEY': getattr(settings, 'RECAPTCHA_SITE_KEY', ''),
    }


def notifications(request):
    """
    Inject unread notification count + latest items for the navbar bell.
    """
    if not request.user.is_authenticated:
        return {'notif_count': 0, 'notif_items': []}

    try:
        from notifications.models import Notification as N
        qs = N.objects.filter(recipient=request.user).order_by('-created_at')[:8]
        unread = N.objects.filter(recipient=request.user, is_read=False).count()

        items = [{
            'id':      n.pk,
            'icon':    n.icon,
            'color':   n.color,
            'title':   n.title,
            'sub':     n.message,
            'time':    n.created_at,
            'url':     n.url,
            'is_read': n.is_read,
            'badge':   None if n.is_read else 'NEW',
        } for n in qs]

        return {
            'notif_count': unread,
            'notif_items': items,
        }
    except Exception:
        return {'notif_count': 0, 'notif_items': []}


def bot_unread(request):
    """Inject unread bot conversation count for the admin sidebar badge."""
    if not (request.user.is_authenticated and request.user.is_staff):
        return {'bot_unread_count': 0}
    try:
        from agent.models import BotSession
        return {'bot_unread_count': BotSession.objects.filter(is_read=False).count()}
    except Exception:
        return {'bot_unread_count': 0}


def active_offers(request):
    """
    Inject active, non-expired offers into every template context.
    Used by base.html to show an offer notification banner on all pages.
    """
    try:
        from home.models import Offer
        today = timezone.now().date()
        offers = Offer.objects.filter(is_active=True).filter(
            Q(valid_until__isnull=True) | Q(valid_until__gte=today)
        ).order_by('order', '-created_at')[:5]
        return {'global_offers': offers, 'global_offers_count': offers.count()}
    except Exception:
        return {'global_offers': [], 'global_offers_count': 0}
