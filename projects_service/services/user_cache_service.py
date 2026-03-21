import requests
import logging
from django.core.cache import cache
from django.conf import settings

logger = logging.getLogger(__name__)

CACHE_TTL = 300


class UserCacheService:
    def get_user(self, user_id, corporate_id=None):
        if not user_id:
            return {}
        cache_key = f"user:{user_id}"
        try:
            data = cache.get(cache_key)
            if data:
                return data
            headers = {"X-Service-Key": settings.PROJECTS_SERVICE_SECRET}
            if corporate_id:
                headers["X-Corporate-Id"] = str(corporate_id)
            resp = requests.get(
                f"{settings.ERP_BACKEND_URL}/api/internal/users/{user_id}/",
                headers=headers,
                timeout=5,
            )
            if resp.status_code == 200:
                data = resp.json()
                cache.set(cache_key, data, CACHE_TTL)
                return data
        except Exception as e:
            logger.warning(f"Failed to fetch user {user_id}: {e}")
        return {}

    def get_corporate(self, corporate_id):
        if not corporate_id:
            return {}
        cache_key = f"corporate:{corporate_id}"
        try:
            data = cache.get(cache_key)
            if data:
                return data
            headers = {"X-Service-Key": settings.PROJECTS_SERVICE_SECRET}
            resp = requests.get(
                f"{settings.ERP_BACKEND_URL}/api/internal/corporates/{corporate_id}/",
                headers=headers,
                timeout=5,
            )
            if resp.status_code == 200:
                data = resp.json()
                cache.set(cache_key, data, CACHE_TTL)
                return data
        except Exception as e:
            logger.warning(f"Failed to fetch corporate {corporate_id}: {e}")
        return {}
