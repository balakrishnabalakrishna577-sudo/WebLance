from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from pricing.models import PricingPlan


class ClientProject(models.Model):
    STATUS_CHOICES = [
        ('planning',    'Planning'),
        ('design',      'Design'),
        ('development', 'Development'),
        ('testing',     'Testing'),
        ('delivered',   'Delivered'),
    ]
    client       = models.ForeignKey(User, on_delete=models.CASCADE, related_name='projects')
    title        = models.CharField(max_length=200)
    description  = models.TextField(blank=True)
    status       = models.CharField(max_length=20, choices=STATUS_CHOICES, default='planning')
    progress     = models.PositiveIntegerField(default=0, help_text='0-100%')
    plan         = models.ForeignKey(PricingPlan, on_delete=models.SET_NULL, null=True, blank=True, related_name='projects')
    start_date   = models.DateField(null=True, blank=True)
    deadline     = models.DateField(null=True, blank=True)
    created_at   = models.DateTimeField(auto_now_add=True)
    updated_at   = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.title} — {self.client.username}'


class ProjectUpdate(models.Model):
    project    = models.ForeignKey(ClientProject, on_delete=models.CASCADE, related_name='updates')
    message    = models.TextField()
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'Update for {self.project.title}'


class ProjectFile(models.Model):
    project    = models.ForeignKey(ClientProject, on_delete=models.CASCADE, related_name='files')
    name       = models.CharField(max_length=200)
    file       = models.FileField(upload_to='project_files/%Y/%m/')
    uploaded_by= models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    uploaded_at= models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class ProjectMessage(models.Model):
    project    = models.ForeignKey(ClientProject, on_delete=models.CASCADE, related_name='messages')
    sender     = models.ForeignKey(User, on_delete=models.CASCADE)
    message    = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_read    = models.BooleanField(default=False)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f'Message from {self.sender.username}'


class ProjectReview(models.Model):
    """One review per client per project, only when project is delivered."""
    RATING_CHOICES = [(i, str(i)) for i in range(1, 6)]

    project    = models.OneToOneField(ClientProject, on_delete=models.CASCADE, related_name='review')
    client     = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews')
    rating     = models.PositiveSmallIntegerField(
                    choices=RATING_CHOICES,
                    validators=[MinValueValidator(1), MaxValueValidator(5)]
                 )
    title      = models.CharField(max_length=120, blank=True)
    body       = models.TextField()
    is_public  = models.BooleanField(default=True, help_text='Show on public pages')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.client.username} — {self.rating}★ on {self.project.title}'

    @property
    def star_range(self):
        return range(1, 6)
