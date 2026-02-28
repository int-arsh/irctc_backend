from django.db import models
from django.conf import settings
from trains.models import Train

class Booking(models.Model):
    STATUS_CHOICES = [
        ('confirmed', 'Confirmed'),
        ('cancelled', 'Cancelled'),
    ]
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='bookings'
    )
    train = models.ForeignKey(
        Train, 
        on_delete=models.CASCADE, 
        related_name='bookings'
    )
    num_seats = models.PositiveIntegerField()  # Cannot be negative or zero
    status = models.CharField(
        max_length=20, 
        choices=STATUS_CHOICES, 
        default='confirmed'
    )
    booking_date = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'bookings'
        ordering = ['-booking_date']  # Latest bookings first
    
    def __str__(self):
        return f"Booking {self.id} - {self.user.email} - {self.train.train_number}"