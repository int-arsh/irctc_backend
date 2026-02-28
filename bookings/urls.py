from django.urls import path
from . import views

urlpatterns = [
    path('bookings/', views.create_booking),
    path('bookings/my/', views.my_bookings),
]