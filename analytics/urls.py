from django.urls import path
from . import views

urlpatterns = [
    path('analytics/top-routes/', views.top_routes),
]