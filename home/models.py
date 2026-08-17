from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone


class Testimonial(models.Model):
    name = models.CharField(max_length=100)
    role = models.CharField(max_length=150, help_text="e.g. Owner, FashionHub India")
    initials = models.CharField(max_length=3, help_text="2-3 letter avatar initials, e.g. RK")
    text = models.TextField()
    rating = models.PositiveSmallIntegerField(default=5, choices=[(i, i) for i in range(1, 6)])
    is_active = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['order', '-created_at']

    def __str__(self):
        return f"{self.name} — {self.role}"

    def stars(self):
        return '★' * self.rating


class UserProfile(models.Model):
    """Extended profile for registered users."""
    user  = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    phone = models.CharField(max_length=20, blank=True, help_text='Mobile number')

    def __str__(self):
        return f'Profile: {self.user.username}'


# Auto-create profile when a new user is created
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.get_or_create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    try:
        instance.profile.save()
    except UserProfile.DoesNotExist:
        UserProfile.objects.create(user=instance)


# ── Offers ─────────────────────────────────────────────────────────

class Offer(models.Model):
    SERVICE_TYPE_CHOICES = [
        ('',            'Any Service (General Offer)'),
        ('website',     'Website Development'),
        ('ecommerce',   'E-Commerce Website'),
        ('seo',         'SEO Optimization'),
        ('redesign',    'Website Redesign'),
        ('landing',     'Landing Page'),
        ('maintenance', 'Website Maintenance'),
        ('portfolio',   'Portfolio Website'),
        ('blog',        'Blog / News Website'),
        ('education',   'School / Education Website'),
        ('restaurant',  'Restaurant Website'),
        ('realestate',  'Real Estate Website'),
        ('hospital',    'Hospital / Clinic Website'),
        ('webapp',      'Web Application Development'),
        ('college',     'College Project'),
        ('academic',    'Academic Project'),
        ('miniproject', 'Mini Project'),
        ('custom',      'Custom Project'),
    ]

    BADGE_COLOR_CHOICES = [
        ('saffron', '🟠 Saffron'),
        ('green',   '🟢 Green'),
        ('indigo',  '🟣 Indigo'),
        ('red',     '🔴 Red'),
        ('gold',    '🟡 Gold'),
    ]

    title            = models.CharField(max_length=200, help_text='e.g. Summer Special – 20% OFF')
    description      = models.TextField(help_text='Short description shown on the offer card.')
    service_type     = models.CharField(
        max_length=20, blank=True, default='',
        choices=SERVICE_TYPE_CHOICES,
        help_text='Which service this offer applies to. Leave blank = any service.'
    )
    badge_text       = models.CharField(max_length=60, blank=True, help_text='Small badge label, e.g. "Limited Time"')
    badge_color      = models.CharField(max_length=20, choices=BADGE_COLOR_CHOICES, default='indigo')
    discount_percent = models.PositiveSmallIntegerField(
        null=True, blank=True,
        help_text='Optional numeric discount %, e.g. 20 → shows "20% OFF"'
    )
    cta_label        = models.CharField(max_length=80, default='Claim Offer', help_text='Button text')
    cta_url          = models.CharField(max_length=300, default='/request-website/', help_text='Button link')
    valid_until      = models.DateField(null=True, blank=True, help_text='Leave blank for no expiry')
    is_active        = models.BooleanField(default=True, help_text='Only active offers are shown on the website')
    order            = models.PositiveIntegerField(default=0, help_text='Lower number = shown first')
    created_at       = models.DateTimeField(auto_now_add=True)
    updated_at       = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['order', '-created_at']
        verbose_name = 'Offer'
        verbose_name_plural = 'Offers'

    def __str__(self):
        return self.title

    @property
    def is_expired(self):
        if self.valid_until is None:
            return False
        return timezone.now().date() > self.valid_until

    @property
    def is_visible(self):
        """True only when active AND not expired."""
        return self.is_active and not self.is_expired
