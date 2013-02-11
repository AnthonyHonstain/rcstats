from django.conf.urls.defaults import *
from django.views.generic.simple import direct_to_template
from registration.views import activate
from registration.views import register

from django.conf import settings

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    url(r'^$', 'rcstats.rcdata.views.index', name="index_url_name"),    
    url(r'^faq$', 'rcstats.rcdata.views.faq', name="faq_url_name"),
    
    url(r'^ranking$', 'rcstats.ranking.views.ranking', name="ranking_url_name"),
    url(r'^ranking/(?P<rankedclass_id>\d+)/$', 'rcstats.ranking.views.ranking_track_class', name="ranking_url_name"),
        
    url(r'^login/$', 'rcstats.uploadresults.views.login_user', name="upload_url_name"),    
    url(r'^upload_start/$', 'rcstats.uploadresults.views.upload_start', name="upload_url_name"),    
    url(r'^upload_start/(?P<upload_id>\d+)/$', 'rcstats.uploadresults.views.upload_validate', name="upload_url_name"),
    url(r'^accounts/login/$', 'django.contrib.auth.views.login', name="upload_url_name"),
    
    url(r'^trackdata/$', 'rcstats.trackdata.views.trackdata', name="trackdata_url_name"),    
    url(r'^trackdata/(?P<track_id>\d+)/$', 'rcstats.trackdata.views.trackdetail', name="trackdata_url_name"),
    url(r'^trackdata/(?P<track_id>\d+)/(?P<time_frame>month|6months|alltime)/$', 'rcstats.trackdata.views.trackdetail_data'),    
    
    url(r'^trackdata/(?P<track_id>\d+)/recentresultshistory/$', 'rcstats.trackdata.views.recentresultshistory'),
    url(r'^trackdata/(?P<track_id>\d+)/recentresultshistory/(?P<race_date>\d{4}-\d{1,2}-\d{2})/$', 'rcstats.trackdata.views.recentresultshistory_data'),
    url(r'^trackdata/(?P<track_id>\d+)/recentresultshistoryshare/(?P<race_date>\d{4}-\d{1,2}-\d{2})/$', 'rcstats.trackdata.views.recentresultshistory_share'),
    
    
    url(r'^myresults/$', 'rcstats.myresults.views.myresults', name='myresults_url_name'),
    url(r'^myresults/(?P<racer_id>\d+)/$', 'rcstats.myresults.views.generalstats', name='myresults_url_name'),
        
    url(r'^displayresults/(?P<race_detail_id>\d+)/$', 'rcstats.displayresults.views.singleraceresult'),
    url(r'^displayresults/singleracedetailed/(?P<race_detail_id>\d+)/$', 'rcstats.displayresults.views.singleracedetailed'),
    
    url(r'^displayresults/singleracerlaps/(?P<race_detail>\d+)/(?P<racer_id>\d+)/$', 'rcstats.displayresults.views.singleracerlaps'),

    url(r'^grappelli/', include('grappelli.urls')),
    url(r'^admin/', include(admin.site.urls)),  
    
    url(r'^activate/complete/$', direct_to_template, 
        {'template': 'registration/activation_complete.html'}, 
        name='registration_activation_complete'),
    # Activation keys get matched by \w+ instead of the more specific
    # [a-fA-F0-9]{40} because a bad activation key should still get to the view;
    # that way it can return a sensible "invalid key" message instead of a
    # confusing 404.
    url(r'^activate/(?P<activation_key>\w+)/$',
       activate,
       {'backend': 'registration.backends.default.DefaultBackend'},
       name='registration_activate'),
    url(r'^register/$',
       register,
       {'backend': 'registration.backends.default.DefaultBackend'},
       name='registration_register'),
    url(r'^register/complete/$',
       direct_to_template,
       {'template': 'registration/registration_complete.html'},
       name='registration_complete'),
    url(r'^register/closed/$',
       direct_to_template,
       {'template': 'registration/registration_closed.html'},
       name='registration_disallowed'),
    (r'', include('registration.auth_urls')),
)

if settings.DEBUG:
    # static files (images, css, javascript, etc.)
    urlpatterns += patterns('',
        (r'^media/(?P<path>.*)$', 'django.views.static.serve', {
        'document_root': settings.MEDIA_ROOT}))
