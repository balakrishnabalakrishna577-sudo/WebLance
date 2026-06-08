from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.core.paginator import Paginator
from .models import Notification


# ── Full notifications page ────────────────────────────────────────

@login_required
def notification_list(request):
    """Full-page notifications list with filter tabs."""
    filter_tab = request.GET.get('filter', 'all')

    qs = Notification.objects.filter(recipient=request.user)
    if filter_tab == 'unread':
        qs = qs.filter(is_read=False)
    elif filter_tab == 'read':
        qs = qs.filter(is_read=True)

    paginator = Paginator(qs, 20)
    page_obj  = paginator.get_page(request.GET.get('page', 1))

    unread_count = Notification.objects.filter(recipient=request.user, is_read=False).count()

    return render(request, 'notifications/list.html', {
        'page_obj':     page_obj,
        'filter_tab':   filter_tab,
        'unread_count': unread_count,
    })


# ── Mark single notification as read ──────────────────────────────

@login_required
@require_POST
def mark_read(request, pk):
    notif = get_object_or_404(Notification, pk=pk, recipient=request.user)
    notif.is_read = True
    notif.save(update_fields=['is_read'])

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        unread = Notification.objects.filter(recipient=request.user, is_read=False).count()
        return JsonResponse({'ok': True, 'unread_count': unread})

    # Redirect to the notification's URL if available
    return redirect(notif.url or 'notification_list')


# ── Mark all as read ───────────────────────────────────────────────

@login_required
@require_POST
def mark_all_read(request):
    Notification.objects.filter(recipient=request.user, is_read=False).update(is_read=True)

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'ok': True, 'unread_count': 0})

    return redirect('notification_list')


# ── Delete single notification ─────────────────────────────────────

@login_required
@require_POST
def delete_notification(request, pk):
    notif = get_object_or_404(Notification, pk=pk, recipient=request.user)
    notif.delete()

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        unread = Notification.objects.filter(recipient=request.user, is_read=False).count()
        return JsonResponse({'ok': True, 'unread_count': unread})

    return redirect('notification_list')


# ── Clear all notifications ────────────────────────────────────────

@login_required
@require_POST
def clear_all(request):
    Notification.objects.filter(recipient=request.user).delete()

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'ok': True, 'unread_count': 0})

    return redirect('notification_list')


# ── AJAX: get unread count + latest items for navbar bell ─────────

@login_required
def api_unread_count(request):
    """Lightweight poll endpoint — returns count + latest 8 items."""
    qs = Notification.objects.filter(recipient=request.user).order_by('-created_at')[:8]
    unread = Notification.objects.filter(recipient=request.user, is_read=False).count()

    items = [{
        'id':         n.pk,
        'type':       n.notif_type,
        'title':      n.title,
        'message':    n.message,
        'url':        n.url,
        'is_read':    n.is_read,
        'icon':       n.icon,
        'color':      n.color,
        'time':       n.created_at.strftime('%d %b, %H:%M'),
    } for n in qs]

    return JsonResponse({'unread_count': unread, 'items': items})
