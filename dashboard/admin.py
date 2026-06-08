from django.contrib import admin
from .models import ClientProject, ProjectUpdate, ProjectFile, ProjectMessage, ProjectReview


@admin.register(ProjectReview)
class ProjectReviewAdmin(admin.ModelAdmin):
    list_display  = ('project', 'client', 'rating', 'title', 'is_public', 'created_at')
    list_filter   = ('rating', 'is_public')
    search_fields = ('project__title', 'client__username', 'body')
    readonly_fields = ('created_at', 'updated_at')


admin.site.register(ClientProject)
admin.site.register(ProjectUpdate)
admin.site.register(ProjectFile)
admin.site.register(ProjectMessage)
