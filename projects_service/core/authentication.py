"""
Custom DRF authentication that reads from JWT middleware-set request attributes.
The JWT middleware already validates the token and sets request.user_id.
This class bridges that into DRF's authentication system.
"""
from django.contrib.auth.models import AnonymousUser
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed


class _JWTUser:
    """Minimal user-like object for DRF compatibility."""
    def __init__(self, user_id, corporate_id=None, is_service_call=False):
        self.id = user_id
        self.pk = user_id
        self.user_id = user_id
        self.corporate_id = corporate_id
        self.is_service_call = is_service_call
        self.is_authenticated = True
        self.is_anonymous = False
        self.is_active = True

    def __str__(self):
        return str(self.user_id)


class JWTMiddlewareAuthentication(BaseAuthentication):
    """
    Reads authentication state set by JWTAuthenticationMiddleware.
    The middleware already validated the JWT token; this just exposes
    the result to DRF's permission system.
    """

    def authenticate(self, request):
        # Middleware sets user_id if token was valid
        user_id = getattr(request, 'user_id', None)
        is_service_call = getattr(request, 'is_service_call', False)

        if user_id is None and not is_service_call:
            # Middleware didn't set user_id — token was missing or invalid
            # Return None to let DRF fall through to other authenticators
            # (the middleware already returned 401 for bad tokens, so this
            # path means the request was already rejected)
            return None

        corporate_id = getattr(request, 'corporate_id', None)
        user = _JWTUser(user_id, corporate_id, is_service_call)
        return (user, None)

    def authenticate_header(self, request):
        return 'Bearer realm="projects"'
