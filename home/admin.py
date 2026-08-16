from django.contrib import admin
from django.utils import timezone
from .models import Testimonial, UserProfile, Offer


@admin.register(Offer)
class OfferAdmin(admin.ModelAdmin):
    list_display  = ('title', 'badge_text', 'discount_percent', 'valid_until',
                     'is_active', 'is_expired_display', 'order', 'created_at')
    list_editable = ('is_active', 'order')
    list_filter   = ('is_active', 'badge_color')
    search_fields = ('title', 'description', 'badge_text')
    date_hierarchy = 'created_at'
    ordering      = ('order', '-created_at')
    fieldsets = (
        ('Content', {
            'fields': ('title', 'description', 'badge_text', 'badge_color', 'discount_percent'),
        }),
        ('Call to Action', {
            'fields': ('cta_label', 'cta_url'),
        }),
        ('Visibility', {
            'fields': ('is_active', 'valid_until', 'order'),
        }),
    )

    @admin.display(boolean=True, description='Expired?')
    def is_expired_display(self, obj):
        return obj.is_expired


@admin.register(Testimonial)
class TestimonialAdmin(admin.ModelAdmin):
    list_display  = ('name', 'role', 'rating', 'is_active', 'order')
    list_editable = ('is_active', 'order')
    list_filter   = ('is_active', 'rating')
    search_fields = ('name', 'role', 'text')


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display  = ('user', 'phone')
    search_fields = ('user__username', 'user__email', 'phone')
