from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver


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
