from rest_framework.routers import DefaultRouter
from django.urls import path, include
from .views import LogViewSet

router = DefaultRouter()

# router.register("event", LogEventViewSet, "logevent_activity")
router.register("", LogViewSet, "log_activity")

urlpatterns = [
    path('', include(router.urls))
]