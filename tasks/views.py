from django.shortcuts import render
from rest_framework import viewsets, filters
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.throttling import UserRateThrottle
from rest_framework.decorators import api_view, authentication_classes, permission_classes, throttle_classes
from rest_framework.response import Response
from django.core.cache import cache
from rest_framework.throttling import ScopedRateThrottle
from .models import Task, AuditLog
from .serializers import TaskSerializer
from .lambda_simulation import send_task_completion_notification  # Import for direct notification logic

class TaskViewSet(viewsets.ModelViewSet):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        task = serializer.save(assigned_to=self.request.user)
        AuditLog.objects.create(task=task, changed_by=self.request.user, change_type='created')

    def perform_update(self, serializer):
        # Handle `.update()` scenarios that bypass `.save()`
        task = self.get_object()
        old_status = task.status  # Store current status before updating
        task = serializer.save()

        # Check if status changed to 'completed' and trigger notification
        if old_status != 'completed' and task.status == 'completed':
            send_task_completion_notification(task.id, task.title)

        AuditLog.objects.create(task=task, changed_by=self.request.user, change_type='updated')

    def perform_destroy(self, instance):
        AuditLog.objects.create(task=instance, changed_by=self.request.user, change_type='deleted')
        instance.delete()

@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
@throttle_classes([ScopedRateThrottle])
def rate_limited_view(request):
    cache_key = f"rate_limit:{request.user.id}"
    count = cache.get(cache_key, 0)

    if count >= 5:
        return Response({"detail": "Rate limit exceeded. Try again later."}, status=429)

    # Improved cache logic to ensure consistency
    cache.set(cache_key, count + 1, timeout=60)

    return Response({"message": "This is a rate-limited endpoint."})
