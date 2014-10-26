from django.conf.urls import patterns, include, url
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    url(r'^$', 'seating_chart.views.home', name='home'),
    url(r'^seating_chart/', include('seating_chart.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),

    #The login view
    url(r'^login/$', 'django.contrib.auth.views.login', {'template_name': 'login.html'}),

    #The logout view
    url(r'^logout/$', 'django.contrib.auth.views.logout'),
)
