from django.conf.urls.defaults import *

from django.conf import settings

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    url(r'^rcdata/$', 'rcdata.views.index'),
    
    url(r'^rcdata/trackdata/$', 'trackdata.views.trackdata'),    
    url(r'^rcdata/trackdata/(?P<track_id>\d+)/$', 'trackdata.views.trackdetail'),
    url(r'^rcdata/trackdata/(?P<track_id>\d+)/(?P<time_frame>month|6months|alltime)/$', 'trackdata.views.trackdetail_data'),    
    
    url(r'^rcdata/trackdata/(?P<track_id>\d+)/recentresultshistory/$', 'trackdata.views.recentresultshistory'),
    url(r'^rcdata/trackdata/(?P<track_id>\d+)/recentresultshistory/(?P<race_date>\d{4}-\d{1,2}-\d{2})/$', 'trackdata.views.recentresultshistory_data'),
    
    url(r'^rcdata/myresults/$', 'rcdata.views.myresults'),
    
    url(r'^processresults/$', 'processresults.views.index'),
    
    #url(r'^polls/(?P<poll_id>\d+)/$', 'polls.views.detail'),

    # Example:
    # (r'^mysite/', include('mysite.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # (r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
)

if settings.DEBUG:
    # static files (images, css, javascript, etc.)
    urlpatterns += patterns('',
        (r'^media/(?P<path>.*)$', 'django.views.static.serve', {
        'document_root': settings.MEDIA_ROOT}))