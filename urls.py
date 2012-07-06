from django.conf.urls.defaults import *

from django.conf import settings

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    url(r'^$', 'rcstats.rcdata.views.index'),    
    url(r'^faq$', 'rcstats.rcdata.views.faq'),
    url(r'^ranking$', 'rcstats.ranking.views.ranking'),
    url(r'^login/$', 'rcstats.uploadresults.views.login_user'),    
    url(r'^upload_start/$', 'rcstats.uploadresults.views.upload_start'),
    
    url(r'^accounts/login/$', 'django.contrib.auth.views.login'),
    
    url(r'^trackdata/$', 'rcstats.trackdata.views.trackdata'),    
    url(r'^trackdata/(?P<track_id>\d+)/$', 'rcstats.trackdata.views.trackdetail'),
    url(r'^trackdata/(?P<track_id>\d+)/(?P<time_frame>month|6months|alltime)/$', 'rcstats.trackdata.views.trackdetail_data'),    
    
    url(r'^trackdata/(?P<track_id>\d+)/recentresultshistory/$', 'rcstats.trackdata.views.recentresultshistory'),
    url(r'^trackdata/(?P<track_id>\d+)/recentresultshistory/(?P<race_date>\d{4}-\d{1,2}-\d{2})/$', 'rcstats.trackdata.views.recentresultshistory_data'),
    
    url(r'^myresults/$', 'rcstats.myresults.views.myresults'),
    url(r'^myresults/(?P<racer_id>\d+)/$', 'rcstats.myresults.views.generalstats'),
        
    url(r'^displayresults/(?P<race_detail_id>\d+)/$', 'rcstats.displayresults.views.singleraceresult'),
    url(r'^displayresults/singleracedetailed/(?P<race_detail_id>\d+)/$', 'rcstats.displayresults.views.singleracedetailed'),
    
    url(r'^displayresults/singleracerlaps/(?P<race_detail>\d+)/(?P<racer_id>\d+)/$', 'rcstats.displayresults.views.singleracerlaps'),

    url(r'^admin/', include(admin.site.urls)),
)

if settings.DEBUG:
    # static files (images, css, javascript, etc.)
    urlpatterns += patterns('',
        (r'^media/(?P<path>.*)$', 'django.views.static.serve', {
        'document_root': settings.MEDIA_ROOT}))
