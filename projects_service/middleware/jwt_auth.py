import jwt
import logging
from django.conf import settings
from django.http import JsonResponse
from projects_service.services.user_cache_service import UserCacheService

logger = logging.getLogger(__name__)

PUBLIC_PATHS = ["/admin/", "/static/", "/media/", "/health/"]

SERVICE_TO_SERVICE_PATHS = [
    "/api/projects/",
    "/api/tasks/",
    "/api/timelog/",
    "/api/issues/",
]


class JWTAuthenticationMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        path = request.path_info

        if any(path.startswith(p) for p in PUBLIC_PATHS):
            return self.get_response(request)

        service_key = request.headers.get("X-Service-Key")
        if service_key and any(path.startswith(p) for p in SERVICE_TO_SERVICE_PATHS):
            if service_key == settings.PROJECTS_SERVICE_SECRET:
                request.user_id = None
                request.corporate_id = request.headers.get("X-Corporate-Id")
                request.is_service_call = True
                return self.get_response(request)
            return JsonResponse({"error": "Invalid service key"}, status=401)

        auth_header = request.headers.get("Authorization", "")
        if not auth_header.startswith("Bearer "):
            return JsonResponse({"error": "Authentication required"}, status=401)

        token = auth_header.split(" ", 1)[1]
        try:
            payload = jwt.decode(
                token,
                settings.JWT_SECRET_KEY,
                algorithms=["HS256"],
                options={"verify_iss": True},
                issuer="quidpath-backend",
            )
        except jwt.ExpiredSignatureError:
            return JsonResponse({"error": "Token expired"}, status=401)
        except jwt.InvalidTokenError as e:
            return JsonResponse({"error": f"Invalid token: {e}"}, status=401)

        request.user_id = payload.get("user_id")
        request.corporate_id = payload.get("corporate_id")
        request.user_roles = payload.get("roles", [])
        request.is_service_call = False

        cache_svc = UserCacheService()
        request.user_data = cache_svc.get_user(request.user_id, request.corporate_id)
        request.corporate_data = cache_svc.get_corporate(request.corporate_id)

        return self.get_response(request)
