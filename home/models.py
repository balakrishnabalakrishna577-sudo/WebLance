from django.db import models


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
