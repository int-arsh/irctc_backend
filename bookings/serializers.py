from rest_framework import serializers
from .models import Booking
from trains.serializers import TrainSerializer

class BookingCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Booking
        fields = ('train', 'num_seats')
    
    def validate_num_seats(self, value):
        if value <= 0:
            raise serializers.ValidationError("Number of seats must be positive")
        if value > 10:
            raise serializers.ValidationError("Cannot book more than 10 seats at once")
        return value

class BookingSerializer(serializers.ModelSerializer):
    train = TrainSerializer(read_only=True)
    
    class Meta:
        model = Booking
        fields = ('id', 'train', 'num_seats', 'status', 'booking_date')
        read_only_fields = ('id', 'status', 'booking_date')