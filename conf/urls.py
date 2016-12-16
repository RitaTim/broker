from django.conf.urls import patterns, include, url, static
from django.conf import settings
from django.contrib import admin
from django.views.static import serve

admin.autodiscover()

urlpatterns = patterns('',
        url(r"^broker/", include('broker.urls')),

        url(r'^', include(admin.site.urls)),
)

if settings.DEBUG:
    import debug_toolbar
    urlpatterns += patterns(
        '',
        url(r'^media/(?P<path>.*)$', serve, {
            'document_root': settings.MEDIA_ROOT,
        }),
        url(r'^__debug__/', include(debug_toolbar.urls)),
    )