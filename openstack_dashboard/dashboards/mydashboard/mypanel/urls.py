from django.conf.urls import patterns  # noqa
from django.conf.urls import url  # noqa

from openstack_dashboard.dashboards.mydashboard.mypanel import views


urlpatterns = patterns('',
    url(r'^$', views.IndexView.as_view(), name='index'),
    url(r'^\?tab=mypanel_tabs_tab$', views.IndexView.as_view (), name='mypanel_tabs'),
)
