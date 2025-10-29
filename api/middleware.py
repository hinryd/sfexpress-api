from django.http import JsonResponse
from django.utils import timezone
from .models import APIKey
import logging

logger = logging.getLogger(__name__)


class APIKeyAuthenticationMiddleware:
    """
    Middleware to authenticate API requests using API key in the Authorization header.
    Expected header format: Authorization: Bearer <api_key>
    """

    def __init__(self, get_response):
        self.get_response = get_response
        # Only these paths require API key authentication
        self.api_paths = [
            '/api/locations',
        ]

    def __call__(self, request):
        # Only check API key for specific API endpoints
        requires_api_key = any(request.path.startswith(path) for path in self.api_paths)

        if not requires_api_key:
            return self.get_response(request)

        # Get the authorization header
        auth_header = request.headers.get('Authorization', '')

        if not auth_header:
            return JsonResponse({
                'error': 'Authentication required',
                'message': 'Missing Authorization header'
            }, status=401)

        # Parse the authorization header
        parts = auth_header.split()
        if len(parts) != 2 or parts[0].lower() != 'bearer':
            return JsonResponse({
                'error': 'Invalid authentication',
                'message': 'Authorization header must be in format: Bearer <api_key>'
            }, status=401)

        api_key = parts[1]

        # Validate the API key
        try:
            api_key_obj = APIKey.objects.select_related('user').get(key=api_key, is_active=True)

            # Update last used timestamp
            api_key_obj.last_used = timezone.now()
            api_key_obj.save(update_fields=['last_used'])

            # Attach user to request
            request.user = api_key_obj.user
            request.api_key = api_key_obj

        except APIKey.DoesNotExist:
            return JsonResponse({
                'error': 'Invalid API key',
                'message': 'The provided API key is invalid or inactive'
            }, status=401)

        return self.get_response(request)
