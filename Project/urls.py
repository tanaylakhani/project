from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.views.debug import default_urlconf

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'Project.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^admin/', include(admin.site.urls)),
    url(r'^$', default_urlconf),
    url('^api_places/', 'views.api_v1_canvas'),
) + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

if settings.DEBUG:
    urlpatterns += patterns('django.contrib.staticfiles.views',
        url(r'^static/(?P<path>.*)$', 'serve'),
    )
