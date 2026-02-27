from rest_framework import serializers
from .models import Train

class TrainSerializer(serializers.ModelSerializer):
    class Meta:
        model = Train
        fields = '__all__'
    
    def validate(self, data):
        # Handle both create and update scenarios
        total_seats = data.get('total_seats', getattr(self.instance, 'total_seats', None))
        available_seats = data.get('available_seats', getattr(self.instance, 'available_seats', None))
        
        if total_seats is not None and available_seats is not None:
            if available_seats > total_seats:
                raise serializers.ValidationError(
                    "Available seats cannot exceed total seats"
                )
        
        return data