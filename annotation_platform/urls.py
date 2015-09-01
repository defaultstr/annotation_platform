from django.conf.urls import patterns, include, url

from django.contrib import admin
import user_system
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'annotation_platform.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^admin/', include(admin.site.urls)),
    url(r'^user/', include('user_system.urls')),
)
