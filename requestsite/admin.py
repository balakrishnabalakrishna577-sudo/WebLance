from django.contrib import admin
from .models import WebsiteRequest


@admin.register(WebsiteRequest)
class WebsiteRequestAdmin(admin.ModelAdmin):
    list_display  = ('business_name', 'name', 'email', 'website_type', 'budget', 'status', 'created_at')
    list_filter   = ('status', 'website_type', 'budget')
    search_fields = ('name', 'business_name', 'email')
    readonly_fields = ('cancel_reason',)
    fieldsets = (
        (None, {'fields': ('user', 'name', 'business_name', 'phone', 'email', 'website_type', 'budget', 'selected_plan', 'description', 'status', 'proposal', 'selected_template')}),
        ('Cancellation', {'fields': ('cancel_reason',), 'classes': ('collapse',)}),
    )
