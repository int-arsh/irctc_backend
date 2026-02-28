from pymongo import MongoClient
from datetime import datetime
import os

_mongo_client = None

def get_mongo_db():
    """Singleton MongoDB client with connection reuse"""
    global _mongo_client
    if _mongo_client is None:
        mongo_uri = os.getenv('MONGO_URI', 'mongodb://localhost:27017/')
        _mongo_client = MongoClient(mongo_uri)
    db_name = os.getenv('MONGO_DB_NAME', 'irctc_logs')
    return _mongo_client[db_name]

def log_search_request(user_id, source, destination, execution_time, result_count):
    """
    Log train search request to MongoDB.
    Failure in logging should not affect API response.
    """
    try:
        db = get_mongo_db()
        log_entry = {
            'endpoint': '/api/trains/search/',
            'user_id': user_id,
            'params': {
                'source': source,
                'destination': destination
            },
            'execution_time_ms': execution_time,
            'result_count': result_count,
            'timestamp': datetime.utcnow()
        }
        db.search_logs.insert_one(log_entry)
    except Exception as e:
        # Log failure should not break API
        print(f"MongoDB logging failed: {e}")