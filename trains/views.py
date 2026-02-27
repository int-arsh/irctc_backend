from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from .models import Train
from .serializers import TrainSerializer

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def search_trains(request):
    source = request.query_params.get('source', '').strip()
    destination = request.query_params.get('destination', '').strip()
    
    if not source or not destination:
        return Response(
            {'error': 'Source and destination required'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Get limit and offset for pagination
    try:
        limit = int(request.query_params.get('limit', 10))
        offset = int(request.query_params.get('offset', 0))
    except ValueError:
        return Response(
            {'error': 'Invalid limit or offset'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    trains = Train.objects.filter(
        source__iexact=source,
        destination__iexact=destination,
        available_seats__gt=0
    )
    
    # Get count before slicing
    total_count = trains.count()
    
    # Apply pagination
    trains = trains[offset:offset+limit]
    
    serializer = TrainSerializer(trains, many=True)
    
    # TODO: Log to MongoDB here (execution time, params, user_id)
    
    return Response({
        'count': total_count,
        'results': serializer.data
    })

@api_view(['POST'])
@permission_classes([IsAdminUser])
def create_train(request):
    serializer = TrainSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)