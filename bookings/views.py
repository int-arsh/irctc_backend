from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.db import transaction
from trains.models import Train
from .models import Booking
from .serializers import BookingCreateSerializer, BookingSerializer

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_booking(request):
    """
    Create booking with race condition handling using select_for_update().
    This locks the train row during the transaction to prevent double-booking.
    """
    serializer = BookingCreateSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    train_id = serializer.validated_data['train'].id
    num_seats = serializer.validated_data['num_seats']
    
    try:
        with transaction.atomic():
            # Lock the train row for update (prevents race condition)
            train = Train.objects.select_for_update().get(id=train_id)
            
            # Check seat availability
            if train.available_seats < num_seats:
                return Response(
                    {'error': f'Only {train.available_seats} seats available'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Deduct seats
            train.available_seats -= num_seats
            train.save()
            
            # Create booking
            booking = Booking.objects.create(
                user=request.user,
                train=train,
                num_seats=num_seats,
                status='confirmed'
            )
            
            return Response(
                BookingSerializer(booking).data,
                status=status.HTTP_201_CREATED
            )
    
    except Train.DoesNotExist:
        return Response(
            {'error': 'Train not found'},
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        return Response(
            {'error': 'Booking failed', 'detail': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def my_bookings(request):
    """Get all bookings for the logged-in user with train details"""
    bookings = Booking.objects.filter(user=request.user).select_related('train')
    serializer = BookingSerializer(bookings, many=True)
    return Response({
        'count': bookings.count(),
        'results': serializer.data
    })