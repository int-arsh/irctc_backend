from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from core.mongo_utils import get_mongo_db

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def top_routes(request):
    
    try:
        db = get_mongo_db()
        
        pipeline = [
            {
                '$group': {
                    '_id': {
                        'source': '$params.source',
                        'destination': '$params.destination'
                    },
                    'search_count': {'$sum': 1}
                }
            },
            {'$sort': {'search_count': -1}},
            {'$limit': 5},
            {
                '$project': {
                    '_id': 0,
                    'route': {
                        '$concat': [
                            '$_id.source',
                            ' - ',
                            '$_id.destination'
                        ]
                    },
                    'search_count': 1
                }
            }
        ]
        
        results = list(db.search_logs.aggregate(pipeline))
        
        return Response({'top_routes': results})
    
    except Exception as e:
        return Response(
            {'error': 'Failed to fetch analytics', 'detail': str(e)},
            status=500
        )