from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.http import JsonResponse
from django.utils import timezone
from django.core.mail import send_mail
from django.views.decorators.http import require_POST
from django.contrib.auth.models import User

from .models import (
    ProjectMilestone, MilestoneNotification,
    Invoice, InvoiceItem,
    ChatRoom, ChatMessage,
    BookingSlot, Booking,
)
from dashboard.models import ClientProject
from agreement.models import Agreement


def is_admin(user):
    return user.is_authenticated and user.is_staff


def admin_required(view_func):
    return login_required(login_url='/accounts/login/')(
        user_passes_test(is_admin, login_url='/accounts/login/')(view_func)
    )


# ══════════════════════════════════════════════════════════════════
# 1. PROJECT MILESTONES
# ══════════════════════════════════════════════════════════════════

@admin_required
def milestone_list(request, project_pk):
    project = get_object_or_404(ClientProject, pk=project_pk)
    milestones = project.milestones.all()
    return render(request, 'features/milestones.html', {
        'project': project,
        'milestones': milestones,
    })


@admin_required
def milestone_add(request, project_pk):
    project = get_object_or_404(ClientProject, pk=project_pk)
    if request.method == 'POST':
        title = request.POST.get('title', '').strip()
        description = request.POST.get('description', '').strip()
        due_date = request.POST.get('due_date') or None
        order = request.POST.get('order', 0)
        if title:
            m = ProjectMilestone.objects.create(
                project=project, title=title,
                description=description, due_date=due_date, order=order
            )
            messages.success(request, f'Milestone "{m.title}" added.')
    return redirect('milestone_list', project_pk=project_pk)


@admin_required
def milestone_update(request, pk):
    m = get_object_or_404(ProjectMilestone, pk=pk)
    if request.method == 'POST':
        new_status = request.POST.get('status', m.status)
        old_status = m.status
        m.status = new_status
        if new_status == 'completed' and old_status != 'completed':
            m.completed_at = timezone.now()
            # Notify client via MilestoneNotification (legacy)
            MilestoneNotification.objects.create(
                milestone=m,
                user=m.project.client,
                message=f'✅ Milestone completed: "{m.title}" for project "{m.project.title}".'
            )
            # ── Persistent notification ────────────────────────────────
            try:
                from notifications.models import Notification
                Notification.send(
                    recipient=m.project.client,
                    title=f'Milestone completed: "{m.title}"',
                    message=f'Project: {m.project.title}',
                    notif_type='milestone',
                    url=f'/features/my-milestones/{m.project.pk}/',
                )
            except Exception:
                pass
            # Email client
            try:
                send_mail(
                    subject=f'Milestone Completed — {m.title}',
                    message=(
                        f'Hi {m.project.client.get_full_name() or m.project.client.username},\n\n'
                        f'Great news! The milestone "{m.title}" for your project '
                        f'"{m.project.title}" has been completed.\n\n'
                        f'View your project: https://weblancehub.in/panel/projects/\n\n'
                        f'— Weblance Team'
                    ),
                    from_email='Weblance <infoweblance01@gmail.com>',
                    recipient_list=[m.project.client.email],
                    fail_silently=True,
                )
            except Exception:
                pass
        m.save()
        messages.success(request, f'Milestone updated to {m.get_status_display()}.')
    return redirect('milestone_list', project_pk=m.project.pk)


@admin_required
def milestone_delete(request, pk):
    m = get_object_or_404(ProjectMilestone, pk=pk)
    project_pk = m.project.pk
    m.delete()
    messages.success(request, 'Milestone deleted.')
    return redirect('milestone_list', project_pk=project_pk)


@login_required
def client_milestones(request, project_pk):
    """Client view of their project milestones."""
    project = get_object_or_404(ClientProject, pk=project_pk, client=request.user)
    milestones = project.milestones.all()
    # Mark notifications as read
    MilestoneNotification.objects.filter(
        milestone__project=project, user=request.user, is_read=False
    ).update(is_read=True)
    return render(request, 'features/client_milestones.html', {
        'project': project,
        'milestones': milestones,
    })


# ══════════════════════════════════════════════════════════════════
# 2. INVOICE GENERATOR
# ══════════════════════════════════════════════════════════════════

@admin_required
def invoice_list(request):
    invoices = Invoice.objects.select_related('created_by').all()
    return render(request, 'features/invoice_list.html', {'invoices': invoices})


@admin_required
def invoice_create(request):
    agreements = Agreement.objects.all()
    projects = ClientProject.objects.all()

    if request.method == 'POST':
        # Auto-generate invoice number
        last = Invoice.objects.order_by('-id').first()
        num = str((last.id + 1) if last else 1).zfill(4)

        agr_id = request.POST.get('agreement') or None
        proj_id = request.POST.get('project') or None
        agr = Agreement.objects.get(pk=agr_id) if agr_id else None
        proj = ClientProject.objects.get(pk=proj_id) if proj_id else None

        inv = Invoice.objects.create(
            invoice_number=num,
            agreement=agr,
            project=proj,
            client_name=request.POST.get('client_name', ''),
            client_email=request.POST.get('client_email', ''),
            client_phone=request.POST.get('client_phone', ''),
            client_address=request.POST.get('client_address', ''),
            title=request.POST.get('title', ''),
            description=request.POST.get('description', ''),
            amount=request.POST.get('amount', 0),
            tax_percent=request.POST.get('tax_percent', 0),
            discount=request.POST.get('discount', 0),
            due_date=request.POST.get('due_date') or None,
            notes=request.POST.get('notes', ''),
            created_by=request.user,
        )

        # Add line items
        descs = request.POST.getlist('item_desc')
        qtys = request.POST.getlist('item_qty')
        prices = request.POST.getlist('item_price')
        for d, q, p in zip(descs, qtys, prices):
            if d.strip():
                InvoiceItem.objects.create(invoice=inv, description=d, quantity=q, unit_price=p)

        messages.success(request, f'Invoice {inv.short_id} created.')
        return redirect('invoice_detail', pk=inv.pk)

    return render(request, 'features/invoice_form.html', {
        'agreements': agreements,
        'projects': projects,
        'title': 'New Invoice',
    })


@admin_required
def invoice_from_agreement(request, agr_pk):
    """Auto-create invoice from an agreement."""
    agr = get_object_or_404(Agreement, pk=agr_pk)
    last = Invoice.objects.order_by('-id').first()
    num = str((last.id + 1) if last else 1).zfill(4)

    inv = Invoice.objects.create(
        invoice_number=num,
        agreement=agr,
        client_name=agr.client_name,
        client_email=agr.client_email,
        client_phone=agr.client_phone,
        client_address=agr.client_address,
        title=f'{agr.get_project_type_display()} — {agr.project_title}',
        description=agr.description[:500],
        amount=agr.advance_amount,
        due_date=agr.start_date,
        notes=f'Advance payment ({agr.advance_percent}%) for agreement {agr.short_ref}',
        created_by=request.user,
    )
    InvoiceItem.objects.create(
        invoice=inv,
        description=f'Advance Payment ({agr.advance_percent}%) — {agr.project_title}',
        quantity=1,
        unit_price=agr.advance_amount,
    )
    messages.success(request, f'Invoice {inv.short_id} auto-generated from agreement.')
    return redirect('invoice_detail', pk=inv.pk)


@admin_required
def invoice_detail(request, pk):
    inv = get_object_or_404(Invoice, pk=pk)
    return render(request, 'features/invoice_detail.html', {'inv': inv})


@admin_required
def invoice_status(request, pk):
    inv = get_object_or_404(Invoice, pk=pk)
    if request.method == 'POST':
        new_status = request.POST.get('status', inv.status)
        inv.status = new_status
        if new_status == 'paid':
            inv.paid_at = timezone.now()
        inv.save()
        messages.success(request, f'Invoice marked as {inv.get_status_display()}.')
    return redirect('invoice_detail', pk=pk)


@admin_required
def invoice_send(request, pk):
    inv = get_object_or_404(Invoice, pk=pk)
    if request.method == 'POST':
        try:
            send_mail(
                subject=f'Invoice {inv.short_id} from Weblance',
                message=(
                    f'Dear {inv.client_name},\n\n'
                    f'Please find your invoice details below.\n\n'
                    f'Invoice: {inv.short_id}\n'
                    f'Title: {inv.title}\n'
                    f'Amount: Rs.{inv.total_amount:,.2f}\n'
                    f'Due Date: {inv.due_date.strftime("%d %b %Y") if inv.due_date else "—"}\n\n'
                    f'Payment methods: UPI, NEFT, Razorpay\n'
                    f'Contact: +91 7892934437 | infoweblance01@gmail.com\n\n'
                    f'— Weblance Team'
                ),
                from_email='Weblance <infoweblance01@gmail.com>',
                recipient_list=[inv.client_email],
                fail_silently=False,
            )
            inv.status = 'sent'
            inv.save()
            messages.success(request, f'Invoice sent to {inv.client_email}.')
        except Exception as e:
            messages.error(request, f'Email failed: {e}')
    return redirect('invoice_detail', pk=pk)


@admin_required
def invoice_delete(request, pk):
    inv = get_object_or_404(Invoice, pk=pk)
    inv.delete()
    messages.success(request, 'Invoice deleted.')
    return redirect('invoice_list')


# ══════════════════════════════════════════════════════════════════
# 3. CLIENT PORTAL CHAT
# ══════════════════════════════════════════════════════════════════

@login_required
def chat_room(request, project_pk):
    if request.user.is_staff:
        project = get_object_or_404(ClientProject, pk=project_pk)
    else:
        project = get_object_or_404(ClientProject, pk=project_pk, client=request.user)

    room, _ = ChatRoom.objects.get_or_create(project=project)

    # Mark messages as read BEFORE fetching (separate querysets)
    if request.user.is_staff:
        ChatMessage.objects.filter(
            room=room, is_read=False, sender__is_staff=False
        ).update(is_read=True)
    else:
        ChatMessage.objects.filter(
            room=room, is_read=False, sender__is_staff=True
        ).update(is_read=True)

    # Handle POST (fallback non-AJAX send)
    if request.method == 'POST':
        text = request.POST.get('message', '').strip()
        if text:
            ChatMessage.objects.create(room=room, sender=request.user, message=text)
            return redirect('chat_room', project_pk=project_pk)

    msgs = room.messages.select_related('sender').all()

    return render(request, 'features/chat.html', {
        'project': project,
        'room': room,
        'msgs': msgs,
    })


@admin_required
def chat_list(request):
    """Admin: list all chat rooms with unread counts."""
    rooms = ChatRoom.objects.select_related('project__client').all()
    return render(request, 'features/chat_list.html', {'rooms': rooms})


@login_required
def progress_poll(request, project_pk):
    """Return live project progress as JSON for client polling."""
    from django.http import JsonResponse
    if request.user.is_staff:
        project = get_object_or_404(ClientProject, pk=project_pk)
    else:
        project = get_object_or_404(ClientProject, pk=project_pk, client=request.user)
    return JsonResponse({
        'progress': project.progress,
        'status':   project.status,
        'status_display': project.get_status_display(),
    })


@login_required
def client_chat_list(request):
    """Client: list their own chat rooms (one per project)."""
    if request.user.is_staff:
        return redirect('chat_list')
    projects = ClientProject.objects.filter(client=request.user)
    # Ensure a ChatRoom exists for each project
    rooms = []
    for p in projects:
        room, _ = ChatRoom.objects.get_or_create(project=p)
        rooms.append(room)
    return render(request, 'features/client_chat_list.html', {'rooms': rooms})


@login_required
def chat_send(request, room_pk):
    """AJAX message send."""
    room = get_object_or_404(ChatRoom, pk=room_pk)
    if not request.user.is_staff and room.project.client != request.user:
        return JsonResponse({'ok': False, 'error': 'Forbidden'}, status=403)
    if request.method == 'POST':
        text = request.POST.get('message', '').strip()
        if not text:
            return JsonResponse({'ok': False, 'error': 'Empty message'})
        msg = ChatMessage.objects.create(room=room, sender=request.user, message=text)
        return JsonResponse({
            'ok':       True,
            'id':       msg.pk,
            'message':  msg.message,
            'sender':   msg.sender.username,
            'is_staff': msg.sender.is_staff,
            'time':     msg.created_at.strftime('%d %b, %H:%M'),
        })
    return JsonResponse({'ok': False, 'error': 'Method not allowed'})


@login_required
def chat_poll(request, room_pk):
    """Poll for new messages since a given ID. Also marks incoming as read."""
    room = get_object_or_404(ChatRoom, pk=room_pk)
    # Security: only room participants can poll
    if not request.user.is_staff and room.project.client != request.user:
        return JsonResponse({'messages': []}, status=403)

    since_id = int(request.GET.get('since', 0))
    new_msgs = room.messages.filter(pk__gt=since_id).select_related('sender')

    # Mark the OTHER side's messages as read when polled
    if request.user.is_staff:
        new_msgs.filter(is_read=False, sender__is_staff=False).update(is_read=True)
    else:
        new_msgs.filter(is_read=False, sender__is_staff=True).update(is_read=True)

    data = [{
        'id':       m.pk,
        'message':  m.message,
        'sender':   m.sender.username,
        'is_staff': m.sender.is_staff,
        'time':     m.created_at.strftime('%d %b, %H:%M'),
    } for m in new_msgs]
    return JsonResponse({'messages': data})


# ── AI Smart Reply ─────────────────────────────────────────────────

@login_required
def chat_ai_reply(request, room_pk):
    """
    Admin-only: generate 3 AI-suggested replies based on recent chat history.
    Uses Gemini AI with a fallback to rule-based suggestions.
    """
    if not request.user.is_staff:
        return JsonResponse({'error': 'Admin only'}, status=403)

    room = get_object_or_404(ChatRoom, pk=room_pk)
    project = room.project

    # Fetch last 10 messages for context
    recent = room.messages.select_related('sender').order_by('-created_at')[:10]
    recent = list(reversed(recent))

    if not recent:
        return JsonResponse({'suggestions': [
            f'Hi {project.client.first_name or project.client.username}! How can I help you today?',
            f'Your project "{project.title}" is progressing well. Do you have any questions?',
            'Feel free to ask if you need any updates or have concerns.',
        ]})

    # Build conversation transcript
    transcript = '\n'.join([
        f'{"Admin" if m.sender.is_staff else "Client"}: {m.message}'
        for m in recent
    ])

    last_client_msg = next(
        (m.message for m in reversed(recent) if not m.sender.is_staff), ''
    )

    suggestions = _generate_ai_suggestions(
        transcript=transcript,
        last_client_msg=last_client_msg,
        project_title=project.title,
        project_status=project.get_status_display(),
        client_name=project.client.first_name or project.client.username,
    )

    return JsonResponse({'suggestions': suggestions})


def _generate_ai_suggestions(transcript, last_client_msg, project_title, project_status, client_name):
    """Generate 3 smart reply suggestions using Gemini AI, with rule-based fallback."""
    import os
    from django.conf import settings

    api_key = getattr(settings, 'GEMINI_API_KEY', '') or os.environ.get('GEMINI_API_KEY', '')

    if api_key and api_key != 'YOUR_GEMINI_API_KEY_HERE':
        try:
            from google import genai
            from google.genai import types

            prompt = f"""You are a professional web development agency assistant at Weblance.
Generate exactly 3 short, professional reply suggestions for the admin to send to the client.

Project: {project_title}
Status: {project_status}
Client name: {client_name}

Recent conversation:
{transcript}

Rules:
- Each suggestion must be 1-2 sentences max
- Be professional, friendly, and helpful
- Address the client's last message directly
- Return ONLY a JSON array of 3 strings, nothing else
- Example: ["Reply 1", "Reply 2", "Reply 3"]"""

            client = genai.Client(api_key=api_key)
            models = ['gemini-2.0-flash-lite', 'gemini-2.0-flash', 'gemini-2.5-flash']

            for model_name in models:
                try:
                    response = client.models.generate_content(
                        model=model_name,
                        contents=prompt,
                        config=types.GenerateContentConfig(
                            temperature=0.7,
                            max_output_tokens=300,
                        ),
                    )
                    import json, re
                    text = response.text.strip()
                    # Extract JSON array
                    match = re.search(r'\[.*?\]', text, re.DOTALL)
                    if match:
                        suggestions = json.loads(match.group())
                        if isinstance(suggestions, list) and len(suggestions) >= 3:
                            return [str(s).strip() for s in suggestions[:3]]
                except Exception:
                    continue
        except Exception:
            pass

    # Rule-based fallback
    return _rule_based_suggestions(last_client_msg, project_title, project_status, client_name)


def _rule_based_suggestions(last_msg, project_title, project_status, client_name):
    """Smart rule-based reply suggestions when AI is unavailable."""
    import re
    msg = last_msg.lower()

    if re.search(r'\b(when|timeline|deadline|ready|complete|finish|done)\b', msg):
        return [
            f'Hi {client_name}, we are on track with "{project_title}". I will share a detailed timeline shortly.',
            f'The current status is {project_status}. We expect to complete the next milestone within the next few days.',
            f'Great question! Let me check the latest progress and get back to you with a precise date.',
        ]
    if re.search(r'\b(price|cost|payment|invoice|pay|amount|fee)\b', msg):
        return [
            f'Hi {client_name}, I will send you the invoice for the next milestone shortly.',
            f'The payment details are as per our agreement. Would you like me to resend the invoice?',
            f'Please check your email for the payment details. Let me know if you have any questions.',
        ]
    if re.search(r'\b(change|update|modify|edit|add|remove|feature|design)\b', msg):
        return [
            f'Hi {client_name}, noted! I will review the change request and update you within 24 hours.',
            f'That change is definitely possible. Let me assess the impact on the timeline and get back to you.',
            f'Thanks for the feedback! We will incorporate this into the next revision.',
        ]
    if re.search(r'\b(issue|problem|bug|error|broken|not working|fix)\b', msg):
        return [
            f'Hi {client_name}, I am looking into this right away. I will have an update for you shortly.',
            f'Thank you for reporting this. Our team will fix it and notify you once resolved.',
            f'I can see the issue. We will prioritize this fix and deploy it as soon as possible.',
        ]
    if re.search(r'\b(thank|thanks|great|good|awesome|perfect|happy)\b', msg):
        return [
            f'Thank you, {client_name}! It is a pleasure working with you on "{project_title}".',
            f'Glad to hear that! Please do not hesitate to reach out if you need anything.',
            f'We appreciate your kind words! We are committed to delivering the best results for you.',
        ]

    # Generic professional replies
    return [
        f'Hi {client_name}, thank you for your message. I will look into this and get back to you shortly.',
        f'Noted! The project "{project_title}" is currently in {project_status} stage. I will keep you updated.',
        f'Thank you for reaching out. Our team will address this within 24 hours.',
    ]


# ══════════════════════════════════════════════════════════════════
# 4. BOOKING / APPOINTMENT SYSTEM
# ══════════════════════════════════════════════════════════════════

@login_required
def booking_page(request):
    """Public booking page — login required."""
    from datetime import date
    today = date.today()
    slots = BookingSlot.objects.filter(
        date__gte=today, is_booked=False
    ).order_by('date', 'start_time')

    if request.method == 'POST':
        slot_id = request.POST.get('slot')
        slot = get_object_or_404(BookingSlot, pk=slot_id, is_booked=False)
        name  = request.POST.get('name', '').strip()
        email = request.POST.get('email', '').strip()
        phone = request.POST.get('phone', '').strip()
        service = request.POST.get('service', '').strip()
        msg   = request.POST.get('message', '').strip()

        if not name or not email:
            messages.error(request, 'Name and email are required.')
            return render(request, 'features/booking.html', {
                'slots': slots,
                'user_name': name,
                'user_email': email,
            })

        Booking.objects.create(
            slot=slot, name=name, email=email,
            phone=phone, service=service, message=msg,
            user=request.user if request.user.is_authenticated else None,
        )
        slot.is_booked = True
        slot.save()

        # ── Notify all staff about new booking ─────────────────────────
        try:
            from notifications.models import Notification
            Notification.send_to_staff(
                title=f'New booking: {name}',
                message=f'{slot.date.strftime("%d %b")} at {slot.start_time.strftime("%I:%M %p")} — {service or "Consultation"}',
                notif_type='booking',
                url='/features/bookings/admin/',
            )
        except Exception:
            pass

        # ── Confirmation email to client (HTML) ─────────────────────
        try:
            booking_obj = Booking.objects.select_related('slot').get(
                slot=slot, name=name, email=email
            )
            from weblance_project.emails import send_booking_confirmation
            send_booking_confirmation(booking_obj)
        except Exception:
            pass
        # Admin plain-text notification
        try:
            send_mail(
                subject=f'[New Booking] {name} — {slot.date}',
                message=(
                    f'New consultation booking:\n\n'
                    f'Name   : {name}\nEmail  : {email}\nPhone  : {phone}\n'
                    f'Service: {service}\nDate   : {slot.date}\n'
                    f'Time   : {slot.start_time}\nMessage: {msg}'
                ),
                from_email='Weblance <infoweblance01@gmail.com>',
                recipient_list=['infoweblance01@gmail.com'],
                fail_silently=True,
            )
        except Exception:
            pass

        messages.success(
            request,
            f'Booking confirmed for {slot.date.strftime("%d %B %Y")} at '
            f'{slot.start_time.strftime("%I:%M %p")}! Check your email.'
        )
        # Redirect logged-in users to dashboard so they see the booking immediately
        if request.user.is_authenticated and not request.user.is_staff:
            return redirect('client_dashboard')
        return redirect('booking_page')

    # Pre-fill form for logged-in users
    user_name  = ''
    user_email = ''
    user_phone = ''
    if request.user.is_authenticated:
        user_name  = request.user.get_full_name() or request.user.username
        user_email = request.user.email
        user_phone = getattr(request.user, 'phone', '')

    return render(request, 'features/booking.html', {
        'slots':      slots,
        'user_name':  user_name,
        'user_email': user_email,
        'user_phone': user_phone,
    })


@admin_required
def booking_admin(request):
    """Admin: manage bookings and slots."""
    bookings = Booking.objects.select_related('slot').order_by('-created_at')
    slots = BookingSlot.objects.order_by('date', 'start_time')
    return render(request, 'features/booking_admin.html', {
        'bookings': bookings,
        'slots': slots,
    })


@admin_required
def slot_add(request):
    if request.method == 'POST':
        date = request.POST.get('date')
        start = request.POST.get('start_time')
        end = request.POST.get('end_time')
        if date and start and end:
            BookingSlot.objects.get_or_create(date=date, start_time=start, defaults={'end_time': end})
            messages.success(request, 'Slot added.')
    return redirect('booking_admin')


@admin_required
def slot_delete(request, pk):
    slot = get_object_or_404(BookingSlot, pk=pk)
    slot.delete()
    messages.success(request, 'Slot deleted.')
    return redirect('booking_admin')


@admin_required
def booking_status(request, pk):
    booking = get_object_or_404(Booking, pk=pk)
    if request.method == 'POST':
        booking.status = request.POST.get('status', booking.status)
        meeting_link = request.POST.get('meeting_link', '').strip()
        if meeting_link:
            booking.meeting_link = meeting_link
        booking.save()
        # Send meeting link to client if provided
        if meeting_link and booking.email:
            try:
                send_mail(
                    subject='Your Meeting Link — Weblance Consultation',
                    message=(
                        f'Hi {booking.name},\n\n'
                        f'Your consultation is confirmed!\n\n'
                        f'Date: {booking.slot.date.strftime("%d %B %Y")}\n'
                        f'Time: {booking.slot.start_time.strftime("%I:%M %p")}\n'
                        f'Meeting Link: {meeting_link}\n\n'
                        f'See you then!\n— Weblance Team'
                    ),
                    from_email='Weblance <infoweblance01@gmail.com>',
                    recipient_list=[booking.email],
                    fail_silently=True,
                )
            except Exception:
                pass
        # ── Persistent notification for logged-in client ───────────────
        if booking.user:
            try:
                from notifications.models import Notification
                if booking.status == 'confirmed':
                    msg = f'{booking.slot.date.strftime("%d %b")} at {booking.slot.start_time.strftime("%I:%M %p")}'
                    if meeting_link:
                        msg += ' — Meeting link ready!'
                    Notification.send(
                        recipient=booking.user,
                        title=f'Booking confirmed: {booking.service or "Consultation"}',
                        message=msg,
                        notif_type='booking',
                        url='/panel/projects/',
                    )
                elif booking.status == 'cancelled':
                    Notification.send(
                        recipient=booking.user,
                        title=f'Booking cancelled: {booking.service or "Consultation"}',
                        message=f'{booking.slot.date.strftime("%d %b")} at {booking.slot.start_time.strftime("%I:%M %p")}',
                        notif_type='booking',
                        url='/panel/projects/',
                    )
            except Exception:
                pass
        messages.success(request, 'Booking updated.')
    return redirect('booking_admin')


# ══════════════════════════════════════════════════════════════════
# 5. PROJECT TIME TRACKER
# ══════════════════════════════════════════════════════════════════

from .models import TimeLog
from django.db.models import Sum


@admin_required
def timelog_list(request, project_pk):
    """Admin: view & add time logs for a project."""
    project = get_object_or_404(ClientProject, pk=project_pk)
    logs = project.time_logs.select_related('logged_by').all()

    # Aggregates
    total_hours = logs.aggregate(t=Sum('hours'))['t'] or 0
    by_category = {}
    for cat, label in TimeLog.CATEGORY_CHOICES:
        hrs = logs.filter(category=cat).aggregate(t=Sum('hours'))['t'] or 0
        if hrs:
            by_category[label] = float(hrs)

    if request.method == 'POST':
        hours = request.POST.get('hours', '').strip()
        log_date = request.POST.get('log_date', '').strip()
        category = request.POST.get('category', 'development')
        description = request.POST.get('description', '').strip()
        if hours and log_date:
            try:
                TimeLog.objects.create(
                    project=project,
                    logged_by=request.user,
                    hours=hours,
                    log_date=log_date,
                    category=category,
                    description=description,
                )
                messages.success(request, f'{hours}h logged for "{project.title}".')
            except Exception as e:
                messages.error(request, f'Error: {e}')
        else:
            messages.error(request, 'Hours and date are required.')
        return redirect('timelog_list', project_pk=project_pk)

    return render(request, 'features/timelog.html', {
        'project': project,
        'logs': logs,
        'total_hours': total_hours,
        'by_category': by_category,
        'categories': TimeLog.CATEGORY_CHOICES,
    })


@admin_required
def timelog_delete(request, pk):
    log = get_object_or_404(TimeLog, pk=pk)
    project_pk = log.project.pk
    log.delete()
    messages.success(request, 'Time log deleted.')
    return redirect('timelog_list', project_pk=project_pk)


@login_required
def client_timelog(request, project_pk):
    """Client: read-only view of time spent on their project."""
    project = get_object_or_404(ClientProject, pk=project_pk, client=request.user)
    logs = project.time_logs.select_related('logged_by').all()
    total_hours = logs.aggregate(t=Sum('hours'))['t'] or 0
    by_category = {}
    for cat, label in TimeLog.CATEGORY_CHOICES:
        hrs = logs.filter(category=cat).aggregate(t=Sum('hours'))['t'] or 0
        if hrs:
            by_category[label] = float(hrs)
    return render(request, 'features/client_timelog.html', {
        'project': project,
        'logs': logs,
        'total_hours': total_hours,
        'by_category': by_category,
    })
