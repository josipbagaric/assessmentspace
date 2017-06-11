from django.conf import settings

from tenant_schemas.middleware import TenantMiddleware


class CustomTenantMiddleware(TenantMiddleware):

    def hostname_from_request(self, request):
        hostname = settings.DOMAIN
        print(hostname)
        return hostname
