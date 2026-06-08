from django.db import models
from django.contrib.auth.models import User


class Notification(models.Model):
    """
    Persistent, per-user notification record.

    TYPE choices map to icon + colour in the UI.
    """
    TYPE_CHOICES = [
        ('project_update',  'Project Update'),
        ('milestone',       'Milestone'),
        ('message',         'Message'),
        ('invoice',         'Invoice'),
        ('booking',         'Booking'),
        ('agreement',       'Agreement'),
        ('quote',           'Quote Request'),
        ('review',          'Review'),
        ('system',          'System'),
    ]

    recipient   = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    notif_type  = models.CharField(max_length=30, choices=TYPE_CHOICES, default='system')
    title       = models.CharField(max_length=200)
    message     = models.TextField(blank=True)
    url         = models.CharField(max_length=500, blank=True, help_text='Link to navigate to on click')
    is_read     = models.BooleanField(default=False)
    created_at  = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        indexes  = [
            models.Index(fields=['recipient', 'is_read']),
            models.Index(fields=['recipient', 'created_at']),
        ]

    def __str__(self):
        return f'[{self.notif_type}] {self.title} → {self.recipient.username}'

    # ── Convenience class-method to create a notification ──────────
    @classmethod
    def send(cls, recipient, title, message='', notif_type='system', url=''):
        """
        Create a notification for a single user.
        Usage:
            Notification.send(user, 'Project updated', 'Your project is now in Testing.', 'project_update', '/panel/projects/project/5/')
        """
        return cls.objects.create(
            recipient=recipient,
            title=title,
            message=message,
            notif_type=notif_type,
            url=url,
        )

    @classmethod
    def send_to_staff(cls, title, message='', notif_type='system', url=''):
        """Broadcast a notification to all staff users."""
        staff = User.objects.filter(is_staff=True, is_active=True)
        objs = [
            cls(recipient=u, title=title, message=message, notif_type=notif_type, url=url)
            for u in staff
        ]
        cls.objects.bulk_create(objs)

    # ── Icon / colour helpers used in templates ─────────────────────
    ICON_MAP = {
        'project_update': ('fas fa-bell',           '#6366F1'),
        'milestone':      ('fas fa-tasks',           '#10B981'),
        'message':        ('fas fa-comment-dots',    '#6366F1'),
        'invoice':        ('fas fa-file-invoice',    '#F59E0B'),
        'booking':        ('fas fa-calendar-check',  '#10B981'),
        'agreement':      ('fas fa-file-contract',   '#F59E0B'),
        'quote':          ('fas fa-rocket',          '#6366F1'),
        'review':         ('fas fa-star',            '#F59E0B'),
        'system':         ('fas fa-info-circle',     '#818CF8'),
    }

    @property
    def icon(self):
        return self.ICON_MAP.get(self.notif_type, ('fas fa-bell', '#6366F1'))[0]

    @property
    def color(self):
        return self.ICON_MAP.get(self.notif_type, ('fas fa-bell', '#6366F1'))[1]
