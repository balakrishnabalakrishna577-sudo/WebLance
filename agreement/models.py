import uuid
from django.db import models
from django.contrib.auth.models import User


class Agreement(models.Model):
    PROJECT_CHOICES = [
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
        ('college',     'College Project Website'),
        ('miniproject', 'Mini Project'),
        ('custom',      'Custom Project'),
    ]
    STATUS_CHOICES = [
        ('draft',    'Draft'),
        ('sent',     'Sent to Client'),
        ('signed',   'Signed'),
        ('active',   'Active'),
        ('completed','Completed'),
        ('cancelled','Cancelled'),
    ]

    # Unique reference
    ref_id       = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)

    # Created by
    created_by   = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='agreements')

    # Client details
    client_name  = models.CharField(max_length=200)
    company_name = models.CharField(max_length=200, blank=True)
    client_email = models.EmailField()
    client_phone = models.CharField(max_length=30, blank=True)
    client_address = models.TextField(blank=True)

    # Project details
    project_type    = models.CharField(max_length=20, choices=PROJECT_CHOICES)
    project_title   = models.CharField(max_length=300)
    description     = models.TextField()
    start_date      = models.DateField()
    end_date        = models.DateField()

    # Payment
    total_cost      = models.DecimalField(max_digits=12, decimal_places=2)
    advance_percent = models.PositiveIntegerField(default=50, help_text="Advance payment %")
    payment_terms   = models.TextField(blank=True)

    # Extra
    additional_terms = models.TextField(blank=True)

    # Status & meta
    status       = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    created_at   = models.DateTimeField(auto_now_add=True)
    updated_at   = models.DateTimeField(auto_now=True)

    # Signature fields
    client_signed    = models.BooleanField(default=False)
    client_signed_at = models.DateTimeField(null=True, blank=True)
    weblance_signed  = models.BooleanField(default=False)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"AGR-{str(self.ref_id)[:8].upper()} | {self.client_name}"

    @property
    def advance_amount(self):
        return (self.total_cost * self.advance_percent) / 100

    @property
    def balance_amount(self):
        return self.total_cost - self.advance_amount

    @property
    def short_ref(self):
        return f"WL-{str(self.ref_id)[:8].upper()}"
