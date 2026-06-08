import uuid
from django.db import models


class BotSession(models.Model):
    """One session per visitor (identified by a UUID stored in their browser)."""
    session_id  = models.UUIDField(default=uuid.uuid4, unique=True, db_index=True)
    visitor_ip  = models.GenericIPAddressField(null=True, blank=True)
    user_agent  = models.TextField(blank=True)
    page_url    = models.URLField(max_length=500, blank=True)
    started_at  = models.DateTimeField(auto_now_add=True)
    last_active = models.DateTimeField(auto_now=True)
    is_read     = models.BooleanField(default=False)   # admin has viewed it

    class Meta:
        ordering = ['-last_active']

    def __str__(self):
        return f'Session {str(self.session_id)[:8]} — {self.started_at:%d %b %Y %H:%M}'

    @property
    def message_count(self):
        return self.messages.count()

    @property
    def user_message_count(self):
        return self.messages.filter(role='user').count()


class BotMessage(models.Model):
    ROLE_CHOICES = [('user', 'User'), ('bot', 'Bot')]

    session    = models.ForeignKey(BotSession, on_delete=models.CASCADE, related_name='messages')
    role       = models.CharField(max_length=4, choices=ROLE_CHOICES)
    text       = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f'[{self.role}] {self.text[:60]}'
