from django.conf.urls.defaults import *

from django.conf import settings

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    url(r'^$', 'rcdata.views.index'),
    
    url(r'^faq$', 'faq.views.faq'),
    
    url(r'^trackdata/$', 'trackdata.views.trackdata'),    
    url(r'^trackdata/(?P<track_id>\d+)/$', 'trackdata.views.trackdetail'),
    url(r'^trackdata/(?P<track_id>\d+)/(?P<time_frame>month|6months|alltime)/$', 'trackdata.views.trackdetail_data'),    
    
    url(r'^trackdata/(?P<track_id>\d+)/recentresultshistory/$', 'trackdata.views.recentresultshistory'),
    url(r'^trackdata/(?P<track_id>\d+)/recentresultshistory/(?P<race_date>\d{4}-\d{1,2}-\d{2})/$', 'trackdata.views.recentresultshistory_data'),
    
    url(r'^myresults/$', 'myresults.views.myresults'),
    url(r'^myresults/(?P<racer_id>\d+)/$', 'myresults.views.generalstats'),
        
    url(r'^displayresults/(?P<race_detail>\d+)/$', 'displayresults.views.singleraceresult'),
    
    url(r'^displayresults/singleracerlaps/(?P<race_detail>\d+)/(?P<racer_id>\d+)/$', 'displayresults.views.singleracerlaps'),

    url(r'^admin/', include(admin.site.urls)),
)

if settings.DEBUG:
    # static files (images, css, javascript, etc.)
    urlpatterns += patterns('',
        (r'^media/(?P<path>.*)$', 'django.views.static.serve', {
        'document_root': settings.MEDIA_ROOT}))
