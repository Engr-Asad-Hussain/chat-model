from redis import Redis
from app.core.config import settings

# NOTE: Can be async redis
redis = Redis(host=settings.REDIS_HOST, port=settings.REDIS_PORT)
