from django.urls import path, include
from .views import rate_limited_view
from rest_framework.routers import DefaultRouter
from .views import TaskViewSet

router = DefaultRouter()
router.register(r'tasks', TaskViewSet, basename='task')


urlpatterns = [
    path('api/', include(router.urls)),
    path('rate-limited/', rate_limited_view, name='rate_limited')
]