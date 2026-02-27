from django.db import models

class Train(models.Model):
    train_number = models.CharField(max_length=10, unique=True)
    name = models.CharField(max_length=100)
    source = models.CharField(max_length=100)
    destination = models.CharField(max_length=100)
    departure_time = models.TimeField()
    arrival_time = models.TimeField()
    total_seats = models.IntegerField()
    available_seats = models.IntegerField()
    
    class Meta:
        db_table = 'trains'
        indexes = [
            models.Index(fields=['source', 'destination']),
        ]
    
    def __str__(self):
        return f"{self.train_number} - {self.name}"