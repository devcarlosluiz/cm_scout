import logging
from django.utils.deprecation import MiddlewareMixin

logger = logging.getLogger(__name__)


class AuditLogMiddleware(MiddlewareMixin):
    """Records user actions for audit trail."""

    TRACKED_METHODS = ('POST', 'PUT', 'PATCH', 'DELETE')
    EXCLUDED_PATHS = ('/admin/jsi18n/', '/static/', '/media/', '/__debug__/')

    def process_response(self, request, response):
        if request.method not in self.TRACKED_METHODS:
            return response

        if any(request.path.startswith(p) for p in self.EXCLUDED_PATHS):
            return response

        if not hasattr(request, 'user') or not request.user.is_authenticated:
            return response

        try:
            from apps.core.models import AuditLog
            AuditLog.objects.create(
                user=request.user,
                action=f'{request.method} {request.path}',
                resource=request.path,
                ip_address=self._get_client_ip(request),
                user_agent=request.META.get('HTTP_USER_AGENT', '')[:500],
            )
        except Exception as e:
            logger.warning(f'AuditLog error: {e}')

        return response

    def _get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0].strip()
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
