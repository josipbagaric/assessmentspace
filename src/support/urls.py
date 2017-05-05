from django.conf.urls import url
from django.views.generic import TemplateView
from . import views

app_name = 'support'

urlpatterns = [

    #### DASHBOARD
    url(r'^$', views.support, name='support'),
    url('^faq/', TemplateView.as_view(template_name='support/options/faq.html'), name='faq'),
    url('^chat/', TemplateView.as_view(template_name='support/options/chat.html'), name='chat'),
    url('^call/', TemplateView.as_view(template_name='support/options/call.html'), name='call'),

]
