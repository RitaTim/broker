from django.conf.urls import patterns, include, url, static
from django.conf import settings
from django.contrib import admin


admin.autodiscover()

urlpatterns = patterns('',
       # Examples:
       # url(r'^$', 'testss.views.home', name='home'),
       # url(r'^testss/', include('testss.foo.urls')),

       # Uncomment the admin/doc line below to enable admin documentation:
       # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

       # Uncomment the next line to enable the admin:
       url(r'^', include(admin.site.urls)),
)

if settings.DEBUG:
    import debug_toolbar
    urlpatterns += patterns(
        '',
        url(r'^media/(?P<path>.*)$', 'django.views.static.serve', {
            'document_root': settings.MEDIA_ROOT,
        }),
        url(r'^__debug__/', include(debug_toolbar.urls)),
    )