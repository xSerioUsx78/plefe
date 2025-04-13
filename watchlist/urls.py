from rest_framework.routers import DefaultRouter
from django.urls import path, include
from . import views

router = DefaultRouter()

router.register("task/user", views.TaskUserViewSet, "task_user")
router.register("task/coin", views.TaskCoinViewSet, "task_coin")
router.register("task/checklist", views.TaskChecklistViewSet, "task_checklist")
router.register("task", views.TaskViewSet, "task")

urlpatterns = [
    path('v1/watchlist/', include(router.urls))
]