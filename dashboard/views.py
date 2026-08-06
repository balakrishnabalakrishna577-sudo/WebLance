from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from django.contrib import messages
from django.views.decorators.http import require_POST
from .models import ClientProject, ProjectUpdate, ProjectFile, ProjectMessage, ProjectReview
from pricing.models import PricingPlan


# ── Decorator: staff-only views ────────────────────────────────────
def admin_required(view_func):
    """Restrict view to logged-in staff users."""
    return login_required(login_url='/accounts/login/')(
        user_passes_test(lambda u: u.is_staff, login_url='/accounts/login/')(view_func)
    )


# ── Client views ───────────────────────────────────────────────────

@login_required
def client_dashboard(request):
    projects = ClientProject.objects.filter(client=request.user).select_related('plan')
    # Also show quote requests submitted with this user's email
    from requestsite.models import WebsiteRequest
    from features.models import Booking
    from django.db.models import Q
    quote_requests = WebsiteRequest.objects.filter(
        Q(user=request.user) | Q(email=request.user.email)
    ).exclude(status='cancelled').order_by('-created_at').distinct()
    bookings = Booking.objects.filter(
        Q(user=request.user) | Q(email=request.user.email)
    ).exclude(status='cancelled').select_related('slot').order_by('-created_at').distinct()
    return render(request, 'dashboard/dashboard.html', {
        'projects': projects,
        'quote_requests': quote_requests,
        'bookings': bookings,
    })


@login_required
def project_detail(request, pk):
    project = get_object_or_404(ClientProject, pk=pk, client=request.user)
    updates = project.updates.all()
    files   = project.files.all()
    msgs    = project.messages.all()

    # Mark incoming messages as read
    msgs.filter(is_read=False).exclude(sender=request.user).update(is_read=True)

    if request.method == 'POST':
        msg_text = request.POST.get('message', '').strip()
        if msg_text:
            ProjectMessage.objects.create(project=project, sender=request.user, message=msg_text)
            return redirect('project_detail', pk=pk)

    # Existing review (if any)
    try:
        existing_review = project.review
    except ProjectReview.DoesNotExist:
        existing_review = None

    return render(request, 'dashboard/project_detail.html', {
        'project':         project,
        'updates':         updates,
        'files':           files,
        'msgs':            msgs,
        'plan':            project.plan,
        'existing_review': existing_review,
        'can_review':      project.status == 'delivered',
    })


# ── Admin views ────────────────────────────────────────────────────

@admin_required
def admin_projects(request):
    projects = ClientProject.objects.select_related('client', 'plan').all()
    clients  = User.objects.filter(is_staff=False)
    return render(request, 'dashboard/admin_projects.html', {
        'projects': projects,
        'clients':  clients,
    })


@admin_required
def admin_project_create(request):
    if request.method == 'POST':
        client_id = request.POST.get('client')
        client    = get_object_or_404(User, pk=client_id)
        plan_id   = request.POST.get('plan') or None
        plan      = get_object_or_404(PricingPlan, pk=plan_id) if plan_id else None

        # Clamp progress to 0-100
        try:
            progress = max(0, min(100, int(request.POST.get('progress', 0))))
        except (ValueError, TypeError):
            progress = 0

        project = ClientProject.objects.create(
            client      = client,
            title       = request.POST.get('title', '').strip(),
            description = request.POST.get('description', '').strip(),
            status      = request.POST.get('status', 'planning'),
            progress    = progress,
            plan        = plan,
            start_date  = request.POST.get('start_date') or None,
            deadline    = request.POST.get('deadline') or None,
        )
        messages.success(request, f'Project "{project.title}" created.')
        return redirect('admin_project_detail', pk=project.pk)

    clients = User.objects.filter(is_staff=False)
    plans   = PricingPlan.objects.all()
    return render(request, 'dashboard/admin_project_form.html', {
        'clients': clients,
        'plans':   plans,
    })


@admin_required
def admin_project_detail(request, pk):
    project = get_object_or_404(ClientProject, pk=pk)

    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'update_progress':
            try:
                progress = max(0, min(100, int(request.POST.get('progress', project.progress))))
            except (ValueError, TypeError):
                progress = project.progress
            plan_id      = request.POST.get('plan') or None
            project.plan = get_object_or_404(PricingPlan, pk=plan_id) if plan_id else None
            old_status   = project.status
            project.progress = progress
            project.status   = request.POST.get('status', project.status)
            project.save()
            # ── Notify client on status change ─────────────────────────
            if project.status != old_status:
                try:
                    from notifications.models import Notification
                    Notification.send(
                        recipient=project.client,
                        title=f'Project status updated: "{project.title}"',
                        message=f'Status changed to {project.get_status_display()} ({progress}% complete).',
                        notif_type='project_update',
                        url=f'/panel/projects/project/{project.pk}/',
                    )
                except Exception:
                    pass
            messages.success(request, 'Progress updated.')

        elif action == 'add_update':
            msg = request.POST.get('message', '').strip()
            if msg:
                ProjectUpdate.objects.create(project=project, message=msg, created_by=request.user)
                # ── Notify the client ──────────────────────────────────
                try:
                    from notifications.models import Notification
                    Notification.send(
                        recipient=project.client,
                        title=f'New update on "{project.title}"',
                        message=(msg[:80] + '…') if len(msg) > 80 else msg,
                        notif_type='project_update',
                        url=f'/panel/projects/project/{project.pk}/',
                    )
                except Exception:
                    pass
                messages.success(request, 'Update added.')

        elif action == 'upload_file':
            f = request.FILES.get('file')
            if f:
                ProjectFile.objects.create(
                    project=project, name=f.name,
                    file=f, uploaded_by=request.user,
                )
                messages.success(request, 'File uploaded.')

        elif action == 'send_message':
            msg = request.POST.get('message', '').strip()
            if msg:
                ProjectMessage.objects.create(project=project, sender=request.user, message=msg)
                # ── Notify the client ──────────────────────────────────
                try:
                    from notifications.models import Notification
                    Notification.send(
                        recipient=project.client,
                        title=f'New message on "{project.title}"',
                        message=(msg[:80] + '…') if len(msg) > 80 else msg,
                        notif_type='message',
                        url=f'/panel/projects/project/{project.pk}/',
                    )
                except Exception:
                    pass

        return redirect('admin_project_detail', pk=pk)

    return render(request, 'dashboard/admin_project_detail.html', {
        'project': project,
        'updates': project.updates.all(),
        'files':   project.files.all(),
        'msgs':    project.messages.all(),
        'plans':   PricingPlan.objects.all(),
        'review':  getattr(project, 'review', None),
    })


@login_required
def cancel_booking(request, pk):
    """Client cancels their own booking."""
    from django.db.models import Q
    from features.models import Booking, BookingSlot
    booking = get_object_or_404(
        Booking,
        pk=pk
    )
    # Security: only the booking owner can cancel
    if booking.user != request.user and booking.email != request.user.email:
        messages.error(request, 'You are not authorised to cancel this booking.')
        return redirect('client_dashboard')

    if booking.status in ('pending', 'confirmed'):
        booking.status = 'cancelled'
        booking.cancel_reason = request.POST.get('cancel_reason', '').strip()
        booking.save()
        # Free up the slot
        slot = booking.slot
        slot.is_booked = False
        slot.save()
        messages.success(request, f'Booking for {slot.date.strftime("%d %B %Y")} has been cancelled.')
    else:
        messages.error(request, 'This booking cannot be cancelled.')
    return redirect('client_dashboard')


@login_required
def cancel_quote_request(request, pk):
    """Client cancels their own quote request."""
    from requestsite.models import WebsiteRequest
    from django.db.models import Q
    req = get_object_or_404(WebsiteRequest, pk=pk)
    # Security: only the request owner can cancel
    if req.user != request.user and req.email != request.user.email:
        messages.error(request, 'You are not authorised to cancel this request.')
        return redirect('client_dashboard')

    if req.status in ('new', 'received'):
        req.status = 'cancelled'
        req.cancel_reason = request.POST.get('cancel_reason', '').strip()
        req.save()
        messages.success(request, f'Quote request for "{req.business_name}" has been cancelled.')
    else:
        messages.error(request, 'This request cannot be cancelled (already in progress or completed).')
    return redirect('client_dashboard')


@admin_required
@require_POST
def delete_project_file(request, pk):
    """Admin deletes an uploaded project file."""
    file_obj = get_object_or_404(ProjectFile, pk=pk)
    project_pk = file_obj.project.pk
    # Delete the actual file from storage
    try:
        file_obj.file.delete(save=False)
    except Exception:
        pass
    file_obj.delete()
    messages.success(request, f'File "{file_obj.name}" deleted.')
    return redirect('admin_project_detail', pk=project_pk)


@admin_required
@require_POST
def admin_project_delete(request, pk):
    project = get_object_or_404(ClientProject, pk=pk)
    title = project.title
    project.delete()
    messages.success(request, f'Project "{title}" deleted.')
    return redirect('admin_projects')


# ── Review views ───────────────────────────────────────────────────

@login_required
@require_POST
def submit_review(request, pk):
    """Client submits or updates a review for a delivered project."""
    project = get_object_or_404(ClientProject, pk=pk, client=request.user)

    if project.status != 'delivered':
        messages.error(request, 'You can only review a delivered project.')
        return redirect('project_detail', pk=pk)

    rating = request.POST.get('rating', '').strip()
    title  = request.POST.get('review_title', '').strip()
    body   = request.POST.get('review_body', '').strip()

    if not rating or not body:
        messages.error(request, 'Please provide a rating and review text.')
        return redirect('project_detail', pk=pk)

    try:
        rating = int(rating)
        if not (1 <= rating <= 5):
            raise ValueError
    except ValueError:
        messages.error(request, 'Invalid rating value.')
        return redirect('project_detail', pk=pk)

    review, created = ProjectReview.objects.update_or_create(
        project=project,
        defaults={
            'client': request.user,
            'rating': rating,
            'title':  title,
            'body':   body,
        }
    )
    if created:
        messages.success(request, 'Thank you for your review!')
    else:
        messages.success(request, 'Your review has been updated.')
    return redirect('project_detail', pk=pk)


@login_required
@require_POST
def delete_review(request, pk):
    """Client deletes their own review."""
    project = get_object_or_404(ClientProject, pk=pk, client=request.user)
    try:
        project.review.delete()
        messages.success(request, 'Your review has been removed.')
    except ProjectReview.DoesNotExist:
        pass
    return redirect('project_detail', pk=pk)
