from django.contrib import admin

# Register your models here.
from .models import Task, AuditLog
@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ['title', 'status', 'assigned_to', 'created_at']
    list_filter = ['status']
    search_fields = ['title', 'description']
#admin.site.register(Task)
admin.site.register(AuditLog)