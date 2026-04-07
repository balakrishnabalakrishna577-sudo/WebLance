from django.db import models

class WebsiteRequest(models.Model):
    WEBSITE_TYPE_CHOICES = [
        ('business', 'Business Website'),
        ('ecommerce', 'E-Commerce Website'),
        ('landing', 'Landing Page'),
        ('custom', 'Custom Website'),
    ]
    
    BUDGET_CHOICES = [
        ('low', 'Below ₹10,000'),
        ('medium', '₹10,000 - ₹25,000'),
        ('high', '₹25,000 - ₹50,000'),
        ('premium', 'Above ₹50,000'),
    ]
    
    STATUS_CHOICES = [
        ('new', 'New'),
        ('received', 'Received'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
    ]

    name = models.CharField(max_length=100)
    business_name = models.CharField(max_length=200)
    phone = models.CharField(max_length=20)
    email = models.EmailField()
    website_type = models.CharField(max_length=20, choices=WEBSITE_TYPE_CHOICES)
    budget = models.CharField(max_length=20, choices=BUDGET_CHOICES)
    description = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='new')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Request from {self.business_name} by {self.name}"
