import io
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.http import HttpResponse, JsonResponse
from django.core.mail import EmailMessage
from django.conf import settings
from django.utils import timezone
from django.db.models import Q

from .models import Agreement
from .forms import AgreementForm
from .pdf_generator import generate_agreement_pdf


# ── Helpers ────────────────────────────────────────────────────────
def is_admin(user):
    return user.is_authenticated and user.is_staff


def admin_required(view_func):
    from django.contrib.auth.decorators import login_required, user_passes_test
    return login_required(login_url='/accounts/login/')(
        user_passes_test(is_admin, login_url='/accounts/login/')(view_func)
    )


def _base_url(request):
    """Return the best base URL for QR codes — prefers SITE_URL env var."""
    from django.conf import settings as dj_settings
    site_url = getattr(dj_settings, 'SITE_URL', '').rstrip('/')
    if site_url:
        return site_url
    return f"{request.scheme}://{request.get_host()}"


# ── Admin: List all agreements ─────────────────────────────────────
@admin_required
def agreement_list(request):
    qs = Agreement.objects.select_related('created_by').all()
    q = request.GET.get('q', '').strip()
    status = request.GET.get('status', '')
    if q:
        qs = qs.filter(
            Q(client_name__icontains=q) |
            Q(company_name__icontains=q) |
            Q(client_email__icontains=q) |
            Q(project_title__icontains=q)
        )
    if status:
        qs = qs.filter(status=status)
    return render(request, 'agreement/list.html', {
        'agreements': qs,
        'q': q,
        'status': status,
        'status_choices': Agreement.STATUS_CHOICES,
    })


# ── Admin: Create agreement ────────────────────────────────────────
@admin_required
def agreement_create(request):
    form = AgreementForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        agr = form.save(commit=False)
        agr.created_by = request.user
        agr.weblance_signed = True          # admin creates = Weblance signed
        agr.save()
        messages.success(request, f'Agreement {agr.short_ref} created.')
        return redirect('agreement_detail', pk=agr.pk)
    return render(request, 'agreement/form.html', {'form': form, 'title': 'New Agreement'})


# ── Admin: Edit agreement ──────────────────────────────────────────
@admin_required
def agreement_edit(request, pk):
    agr = get_object_or_404(Agreement, pk=pk)
    form = AgreementForm(request.POST or None, instance=agr)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Agreement updated.')
        return redirect('agreement_detail', pk=agr.pk)
    return render(request, 'agreement/form.html', {'form': form, 'title': 'Edit Agreement', 'agr': agr})


# ── Admin: Delete agreement ────────────────────────────────────────
@admin_required
def agreement_delete(request, pk):
    agr = get_object_or_404(Agreement, pk=pk)
    if request.method == 'POST':
        agr.delete()
        messages.success(request, 'Agreement deleted.')
        return redirect('agreement_list')
    return render(request, 'agreement/confirm_delete.html', {'agr': agr})


# ── Admin: Detail view ─────────────────────────────────────────────
@admin_required
def agreement_detail(request, pk):
    agr = get_object_or_404(Agreement, pk=pk)
    return render(request, 'agreement/detail.html', {'agr': agr})


# ── Admin: Update status ───────────────────────────────────────────
@admin_required
def agreement_status(request, pk):
    agr = get_object_or_404(Agreement, pk=pk)
    if request.method == 'POST':
        new_status = request.POST.get('status')
        if new_status in dict(Agreement.STATUS_CHOICES):
            agr.status = new_status
            agr.save()
            messages.success(request, f'Status updated to {agr.get_status_display()}.')
    return redirect('agreement_detail', pk=pk)


# ── Download PDF ───────────────────────────────────────────────────
@login_required
def agreement_pdf(request, pk):
    agr = get_object_or_404(Agreement, pk=pk)
    # Only admin or the agreement creator can download
    if not (request.user.is_staff or agr.created_by == request.user):
        messages.error(request, 'Access denied.')
        return redirect('home')
    pdf_bytes = generate_agreement_pdf(agr, base_url=_base_url(request))
    response = HttpResponse(pdf_bytes, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="Weblance_Agreement_{agr.short_ref}.pdf"'
    return response


# ── Send PDF via email ─────────────────────────────────────────────
@admin_required
def agreement_send_email(request, pk):
    agr = get_object_or_404(Agreement, pk=pk)
    if request.method == 'POST':
        try:
            pdf_bytes = generate_agreement_pdf(agr, base_url=_base_url(request))
            verify_url = f"{_base_url(request)}/agreement/verify/{agr.ref_id}/"
            email = EmailMessage(
                subject=f'Service Agreement from Weblance — {agr.short_ref}',
                body=(
                    f'Dear {agr.client_name},\n\n'
                    f'Please find attached your Service Agreement from Weblance.\n\n'
                    f'Agreement Reference: {agr.short_ref}\n'
                    f'Project: {agr.project_title}\n'
                    f'Total Cost: ₹{agr.total_cost:,.2f}\n\n'
                    f'You can verify this agreement online at:\n{verify_url}\n\n'
                    f'Please review and revert with any questions.\n\n'
                    f'Regards,\nBalakrishna\nWeblance\n+91 7892934437'
                ),
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[agr.client_email],
            )
            email.attach(
                f'Weblance_Agreement_{agr.short_ref}.pdf',
                pdf_bytes,
                'application/pdf'
            )
            email.send()
            agr.status = 'sent'
            agr.save()
            messages.success(request, f'Agreement sent to {agr.client_email}.')
        except Exception as e:
            messages.error(request, f'Email failed: {e}')
    return redirect('agreement_detail', pk=pk)


# ── Public: Verify agreement via QR ───────────────────────────────
def agreement_verify(request, ref_id):
    # Try full UUID first, then fall back to short_ref lookup
    try:
        agr = get_object_or_404(Agreement, ref_id=ref_id)
    except Exception:
        agr = get_object_or_404(Agreement, ref_id=ref_id)
    details = [
        ('Agreement Ref', agr.short_ref),
        ('Project Title', agr.project_title),
        ('Start Date', agr.start_date.strftime('%d %B %Y')),
        ('End Date', agr.end_date.strftime('%d %B %Y')),
    ]
    return render(request, 'agreement/verify.html', {'agr': agr, 'details': details})


# ── Client: Sign agreement ─────────────────────────────────────────
def agreement_sign(request, ref_id):
    agr = get_object_or_404(Agreement, ref_id=ref_id)
    if request.method == 'POST' and not agr.client_signed:
        agr.client_signed = True
        agr.client_signed_at = timezone.now()
        if agr.status == 'sent':
            agr.status = 'signed'
        agr.save()
        messages.success(request, 'Agreement signed successfully.')
    return redirect('agreement_verify', ref_id=ref_id)
