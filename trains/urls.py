from django.urls import path
from . import views

urlpatterns = [
    path('trains/search/', views.search_trains),
    path('trains/', views.create_train),
]