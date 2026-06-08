from django.db import models
from django.contrib.auth.models import User
from dashboard.models import ClientProject
from agreement.models import Agreement


# ══════════════════════════════════════════════════════════════════
# 1. PROJECT MILESTONES — Live Progress Tracker
# ══════════════════════════════════════════════════════════════════

class ProjectMilestone(models.Model):
    STATUS_CHOICES = [
        ('pending',     'Pending'),
        ('in_progress', 'In Progress'),
        ('completed',   'Completed'),
        ('blocked',     'Blocked'),
    ]
    project     = models.ForeignKey(ClientProject, on_delete=models.CASCADE, related_name='milestones')
    title       = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    status      = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    order       = models.PositiveIntegerField(default=0)
    due_date    = models.DateField(null=True, blank=True)
    completed_at= models.DateTimeField(null=True, blank=True)
    created_at  = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['order', 'created_at']

    def __str__(self):
        return f'{self.project.title} — {self.title}'


class MilestoneNotification(models.Model):
    milestone   = models.ForeignKey(ProjectMilestone, on_delete=models.CASCADE, related_name='notifications')
    user        = models.ForeignKey(User, on_delete=models.CASCADE)
    message     = models.TextField()
    is_read     = models.BooleanField(default=False)
    created_at  = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'Notification for {self.user.username}: {self.milestone.title}'


# ══════════════════════════════════════════════════════════════════
# 2. INVOICE GENERATOR
# ══════════════════════════════════════════════════════════════════

class Invoice(models.Model):
    STATUS_CHOICES = [
        ('draft',    'Draft'),
        ('sent',     'Sent'),
        ('paid',     'Paid'),
        ('overdue',  'Overdue'),
        ('cancelled','Cancelled'),
    ]
    invoice_number = models.CharField(max_length=50, unique=True)
    agreement      = models.ForeignKey(Agreement, on_delete=models.SET_NULL, null=True, blank=True, related_name='invoices')
    project        = models.ForeignKey(ClientProject, on_delete=models.SET_NULL, null=True, blank=True, related_name='invoices')
    client_name    = models.CharField(max_length=200)
    client_email   = models.EmailField()
    client_phone   = models.CharField(max_length=30, blank=True)
    client_address = models.TextField(blank=True)
    title          = models.CharField(max_length=300)
    description    = models.TextField(blank=True)
    amount         = models.DecimalField(max_digits=12, decimal_places=2)
    tax_percent    = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    discount       = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    status         = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    due_date       = models.DateField(null=True, blank=True)
    paid_at        = models.DateTimeField(null=True, blank=True)
    notes          = models.TextField(blank=True)
    created_by     = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='invoices_created')
    created_at     = models.DateTimeField(auto_now_add=True)
    updated_at     = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'INV-{self.invoice_number} | {self.client_name}'

    @property
    def tax_amount(self):
        return (self.amount * self.tax_percent) / 100

    @property
    def total_amount(self):
        return self.amount + self.tax_amount - self.discount

    @property
    def short_id(self):
        return f'WL-INV-{self.invoice_number}'


class InvoiceItem(models.Model):
    invoice     = models.ForeignKey(Invoice, on_delete=models.CASCADE, related_name='items')
    description = models.CharField(max_length=300)
    quantity    = models.DecimalField(max_digits=10, decimal_places=2, default=1)
    unit_price  = models.DecimalField(max_digits=12, decimal_places=2)

    @property
    def total(self):
        return self.quantity * self.unit_price

    def __str__(self):
        return f'{self.description} x{self.quantity}'


# ══════════════════════════════════════════════════════════════════
# 3. CLIENT PORTAL CHAT
# ══════════════════════════════════════════════════════════════════

class ChatRoom(models.Model):
    project    = models.OneToOneField(ClientProject, on_delete=models.CASCADE, related_name='chat_room')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Chat: {self.project.title}'

    @property
    def unread_count_for_client(self):
        return self.messages.filter(is_read=False, sender__is_staff=True).count()

    @property
    def unread_count_for_admin(self):
        return self.messages.filter(is_read=False, sender__is_staff=False).count()


class ChatMessage(models.Model):
    room       = models.ForeignKey(ChatRoom, on_delete=models.CASCADE, related_name='messages')
    sender     = models.ForeignKey(User, on_delete=models.CASCADE)
    message    = models.TextField()
    attachment = models.FileField(upload_to='chat_attachments/%Y/%m/', blank=True, null=True)
    is_read    = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f'{self.sender.username}: {self.message[:50]}'


# ══════════════════════════════════════════════════════════════════
# 4. BOOKING / APPOINTMENT SYSTEM
# ══════════════════════════════════════════════════════════════════

class BookingSlot(models.Model):
    """Admin defines available time slots."""
    date       = models.DateField()
    start_time = models.TimeField()
    end_time   = models.TimeField()
    is_booked  = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['date', 'start_time']
        unique_together = ['date', 'start_time']

    def __str__(self):
        return f'{self.date} {self.start_time}–{self.end_time}'


class Booking(models.Model):
    STATUS_CHOICES = [
        ('pending',   'Pending'),
        ('confirmed', 'Confirmed'),
        ('cancelled', 'Cancelled'),
        ('completed', 'Completed'),
    ]
    slot          = models.OneToOneField(BookingSlot, on_delete=models.CASCADE, related_name='booking')
    user          = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='bookings')
    name          = models.CharField(max_length=200)
    email         = models.EmailField()
    phone         = models.CharField(max_length=30, blank=True)
    service       = models.CharField(max_length=200, blank=True)
    message       = models.TextField(blank=True)
    status        = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    meeting_link  = models.URLField(blank=True, help_text='Google Meet / Zoom link')
    cancel_reason = models.TextField(blank=True, help_text='Reason provided by client when cancelling')
    created_at    = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.name} — {self.slot.date} {self.slot.start_time}'


# ══════════════════════════════════════════════════════════════════
# 5. PROJECT TIME TRACKER
# ══════════════════════════════════════════════════════════════════

class TimeLog(models.Model):
    """Admin logs work sessions against a project."""
    CATEGORY_CHOICES = [
        ('design',      'Design'),
        ('development', 'Development'),
        ('testing',     'Testing'),
        ('meeting',     'Meeting / Call'),
        ('revision',    'Revision'),
        ('deployment',  'Deployment'),
        ('other',       'Other'),
    ]

    project     = models.ForeignKey(ClientProject, on_delete=models.CASCADE, related_name='time_logs')
    logged_by   = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='time_logs')
    category    = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='development')
    description = models.TextField(blank=True)
    hours       = models.DecimalField(max_digits=6, decimal_places=2, help_text='Hours worked (e.g. 1.5)')
    log_date    = models.DateField()
    created_at  = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-log_date', '-created_at']

    def __str__(self):
        return f'{self.project.title} — {self.hours}h ({self.category}) on {self.log_date}'

    @property
    def minutes(self):
        return int(self.hours * 60)
