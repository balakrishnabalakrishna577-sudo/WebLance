from django.db import models

class PortfolioItem(models.Model):
    CATEGORY_CHOICES = [
        ('business',     'Business Websites'),
        ('ecommerce',    'E-Commerce Websites'),
        ('landing',      'Landing Pages'),
        ('seo',          'SEO Optimization'),
        ('redesign',     'Website Redesign'),
        ('maintenance',  'Website Maintenance'),
        ('portfolio',    'Portfolio Websites'),
        ('blog',         'Blog / News Websites'),
        ('education',    'School / Education Websites'),
        ('restaurant',   'Restaurant Websites'),
        ('realestate',   'Real Estate Websites'),
        ('hospital',     'Hospital / Clinic Websites'),
        ('webapp',       'Web Applications'),
        ('college',      'College Projects'),
        ('academic',     'Academic Projects'),
        ('miniproject',  'Mini Projects'),
        ('custom',       'Custom Projects'),
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
