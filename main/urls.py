from django.urls import path
from . import views


urlpatterns = [
    path('', views.index, name="index"),
    path('engulfing/', views.engulfing, name="engulfing"),
    path('<time_frame>/long/', views.long, name="long"),
    path('<time_frame>/short/', views.short, name="short"),
]
