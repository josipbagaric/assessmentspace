"""app URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.10/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url, include
from django.contrib import admin

from api import urls as api_urls
from interviews import urls as interviews_urls
from support import urls as support_urls

import landing.views

from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import RedirectView

urls = [

    # top-level pages
    url('^$', landing.views.index, name='home'),

    url('^app/', include(interviews_urls, namespace="interviews")),
    url('^support/', include(support_urls, namespace="support")),

    url(r'^admin/', admin.site.urls) if settings.ADMIN_ENABLED else None,

    url(r'^tinymce/', include('tinymce.urls')),
    url(r'^markdown/', include('django_markdown.urls')),

    # user creation and auth
    url('^', include('django.contrib.auth.urls')),
    url('^accounts/profile', RedirectView.as_view(url='/app/dashboard/'), name='initial'),

    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    url(r'^api/v1/', include(api_urls, namespace="api")),

]

urlpatterns = [u for u in urls if u != None] + \
    static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
