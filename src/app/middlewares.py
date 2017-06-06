from django.conf import settings as project_settings

from tenant_schemas.middleware import TenantMiddleware


class CustomTenantMiddleware(TenantMiddleware):

    def hostname_from_request(self, request):
        return project_settings.DOMAIN