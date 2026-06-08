from django.contrib import admin
from .models import Booking, BookingSlot, ProjectMilestone, Invoice, InvoiceItem, ChatRoom, ChatMessage, TimeLog


@admin.register(BookingSlot)
class BookingSlotAdmin(admin.ModelAdmin):
    list_display = ('date', 'start_time', 'end_time', 'is_booked')
    list_filter  = ('is_booked', 'date')


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display  = ('name', 'email', 'slot', 'service', 'status', 'created_at')
    list_filter   = ('status',)
    search_fields = ('name', 'email', 'service')
    readonly_fields = ('cancel_reason',)
    fieldsets = (
        (None, {'fields': ('slot', 'user', 'name', 'email', 'phone', 'service', 'message', 'meeting_link', 'status')}),
        ('Cancellation', {'fields': ('cancel_reason',), 'classes': ('collapse',)}),
    )


@admin.register(TimeLog)
class TimeLogAdmin(admin.ModelAdmin):
    list_display  = ('project', 'category', 'hours', 'log_date', 'logged_by', 'description')
    list_filter   = ('category', 'log_date')
    search_fields = ('project__title', 'description')
    date_hierarchy = 'log_date'


admin.site.register(ProjectMilestone)
admin.site.register(Invoice)
admin.site.register(InvoiceItem)
admin.site.register(ChatRoom)
admin.site.register(ChatMessage)
