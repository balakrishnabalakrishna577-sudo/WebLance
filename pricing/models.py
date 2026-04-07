from django.db import models

class PricingPlan(models.Model):
    name = models.CharField(max_length=100)
    price = models.CharField(max_length=50)  # e.g. "₹15,000"
    description = models.CharField(max_length=200)
    features = models.TextField(help_text="One feature per line. Prefix with '-' to mark as unavailable.")
    delivery_time = models.CharField(max_length=100)
    is_popular = models.BooleanField(default=False)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return self.name

    def features_list(self):
        return [f.strip() for f in self.features.strip().splitlines() if f.strip()]
