from django.db import models

class PortfolioItem(models.Model):
    CATEGORY_CHOICES = [
        ('business', 'Business Websites'),
        ('ecommerce', 'E-Commerce Websites'),
        ('landing', 'Landing Pages'),
    ]
    
    title = models.CharField(max_length=200)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    description = models.TextField()
    image = models.ImageField(upload_to='portfolio/%Y/%m/%d/')
    live_url = models.URLField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return self.title
