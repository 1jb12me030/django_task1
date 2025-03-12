from django.db import models
from .lambda_simulation import send_task_completion_notification
# Create your models here.
from django.contrib.auth.models import User

class Task(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
    ]
    
    title = models.CharField(max_length=200)
    description = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    assigned_to = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title
    def save(self, *args, **kwargs):
        if self.pk:  # Only check for updates (not new entries)
            old_task = Task.objects.get(pk=self.pk)
            if old_task.status != 'completed' and self.status == 'completed':
                # Function is called when task status changes to 'completed'
                send_task_completion_notification(self.id, self.title)
        super().save(*args, **kwargs)

class AuditLog(models.Model):
    CHANGE_TYPES = [
        ('created', 'Created'),
        ('updated', 'Updated'),
        ('deleted', 'Deleted'),
    ]

    task = models.ForeignKey(Task, on_delete=models.CASCADE)
    changed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    change_type = models.CharField(max_length=20, choices=CHANGE_TYPES)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.task.title} - {self.change_type}"