import time
import datetime

from dateutil.relativedelta import relativedelta

from django.template import Context, loader
from django.shortcuts import render_to_response, get_object_or_404
from django.http import HttpResponse, Http404
from django.db import connection
from django.utils import simplejson

from rcdata.models import SupportedTrackName



def trackdata(request):
    tracklist = SupportedTrackName.objects.all()

    return render_to_response('trackdata.html', {'track_list':tracklist})

def trackdetail(request, track_id):
    p = get_object_or_404(SupportedTrackName, pk=track_id)
    
    ctx = Context({'trackname':p.trackkey})
    return render_to_response('trackdatadetail.html', ctx)
    

def trackdetail_data(request, track_id, time_frame='alltime'):
    p = get_object_or_404(SupportedTrackName, pk=track_id)
    
    if (time_frame not in ('alltime', 'month', '6months')):
        raise Http404
    
    sqltimefilter = ''
    filterdatestr = 'All Time'
    if (time_frame == 'month'):
        filterdate = datetime.datetime.now() + relativedelta(months=-1)
        filterdatestr = time.strftime('%a, %d %b %Y', filterdate.timetuple())
        dbdate = time.strftime('%Y-%m-%d %H:%M:%S-01', filterdate.timetuple())
        sqltimefilter = "AND rdetails.racedate > '" + dbdate + "'"
    elif (time_frame == '6months'):
        filterdate = datetime.datetime.now() + relativedelta(months=-6)
        filterdatestr = time.strftime('%a, %d %b %Y', filterdate.timetuple())
        dbdate = time.strftime('%Y-%m-%d %H:%M:%S-01', filterdate.timetuple())
        sqltimefilter = "AND rdetails.racedate > '" + dbdate + "'"
    
    cursor = connection.cursor()
    sqlquery = '''SELECT SUM(racedata.finalpos), racedata.racerpreferredname  FROM
      (
      SELECT rresults.raceid_id, rid.racerpreferredname, rresults.finalpos FROM
        rcdata_racerid as rid,
        rcdata_singleraceresults as rresults
        WHERE rresults.racerid_id = rid.id AND
            rresults.finalpos = 1    
      ) as racedata,
    rcdata_singleracedetails as rdetails
    WHERE rdetails.id = racedata.raceid_id AND
      rdetails.trackkey_id = %(trackkey)s
      ''' + sqltimefilter + '''
    /* This is were we would filter out by track id and racelength */
    GROUP BY racedata.racerpreferredname
    ORDER BY SUM(racedata.finalpos) desc
    LIMIT 100;'''
       
    cursor.execute(sqlquery, {'trackkey':p.trackkey.id})
    topwins = cursor.fetchall()

    querytoplaps = '''SELECT SUM(racedata.lapcount), racedata.racerpreferredname  FROM
      (
      SELECT rresults.raceid_id, rid.racerpreferredname, rresults.lapcount FROM
        rcdata_racerid as rid,
        rcdata_singleraceresults as rresults
        WHERE rresults.racerid_id = rid.id
      ) as racedata,
    rcdata_singleracedetails as rdetails
    WHERE rdetails.id = racedata.raceid_id AND
      rdetails.trackkey_id = %(trackkey)s
      ''' + sqltimefilter + '''
    /* This is were we would filter out by track id and racelength */
    GROUP BY racedata.racerpreferredname
    ORDER BY SUM(racedata.lapcount) desc
    LIMIT 100;'''
       
    cursor.execute(querytoplaps, {'trackkey':p.trackkey.id})
    toplaps = cursor.fetchall()
    
    
    topwins_jsdata = simplejson.dumps(topwins)
    toplaps_jsdata = simplejson.dumps(toplaps)
      
    ctx = Context({'filterdate':filterdatestr,
                   'tabid':time_frame, # For this to work with tabs, I need unique id's for each datatable
                   'topwins':topwins_jsdata, 
                   'toplaps':toplaps_jsdata})
    return render_to_response('trackdatadetail_data.html', ctx)
        
        
        
        
        
def recentresults(request, track_id):
    
    p = get_object_or_404(SupportedTrackName, pk=track_id)
    
    '''
    Now I am faced with the problem of recreating the data that I already
    extracted. I need the most recent race result for each class that ran.
        What do I have to work with:
            DO THEY HAVE A-Main in title?
                brcr? - same as TRCR, at least for rcscoringpro data.
                trcr? - "main" in racedata, and the largest round number.
                    13.5 STOCK SHORT COURSE B Main  Round# 3, Race# 3
            What about older race formats
                    TACOMA R/C RACEWAY             08-22-2010                    
                    Best Heat Lap/Time for 2WD Stock: 
                       RYAN MATESA with    20/6:01.36                    
                               -- 2WD Stock - A  Main -- 
                    Pos Car Laps    time     name                id    avg.mph
                      1   2  27     8:11.29 DERRY TIEDEMAN        4     13.11
                      2   5  27     8:12.88 RYAN MATESA           6     13.07
            THERE IS NO Round information, but there is a title with 'Main' in it.
                    
    '''
    
    raceresults = []
    print "TRYING TO QUERY DEBUGGING"
    cursor = connection.cursor()
    sqlquery_raceids = '''SELECT rdetails.id, 
                                 rdetails.racedata, 
                                 rdetails.roundnumber, 
                                 rdetails.racenumber, 
                                 rdetails.racedate
     FROM
      rcdata_singleracedetails as rdetails,
      (SELECT rdetails_date.racedate::date as racedate FROM
        rcdata_singleracedetails as rdetails_date
        WHERE rdetails_date.trackkey_id = %(trackkey)s AND      
          rdetails_date.racedata ILIKE '%%main%%'
        GROUP BY rdetails_date.racedate::date
        ORDER BY rdetails_date.racedate::date desc
        LIMIT 1
      ) as recentracedate
    WHERE rdetails.trackkey_id = %(trackkey)s AND
      rdetails.racedata ILIKE '%%main%%' AND
      rdetails.racedate::date = recentracedate.racedate;'''
    
    cursor.execute(sqlquery_raceids, {'trackkey':p.trackkey.id})
    raceid_results = cursor.fetchall() 
    
    #print "raceid_results", raceid_results
    # An example of the raceid_results
    # raceid_results [
    #    (1712, u'Stock Buggy B Main', 3, 1, datetime.datetime(2012, 4, 13, 17, 3, 23)), 
    #    (1713, u'Modified Buggy B Main', 3, 2, datetime.datetime(20  .... ]
    
    for raceid in raceid_results:
            
        sqlquery = '''SELECT finalpos, rcdata_racerid.racerpreferredname, lapcount, racetime, fastlap, behind 
          FROM rcdata_singleraceresults,
              rcdata_racerid
          WHERE raceid_id = %(trackkey)s AND
              racerid_id = rcdata_racerid.id
          ORDER BY finalpos
          ;'''
        cursor.execute(sqlquery, {'trackkey':raceid[0]})
        individual_results = cursor.fetchall()
        
        formated_result = []
        
        for individual in individual_results:
            formated_result.append([
                                     individual[0], # final pos
                                     individual[1], # id
                                     individual[2], # lapcount
                                     str(individual[3]), # racetime
                                     str(individual[4]), #fastlap
                                     str(individual[5]) # behind              
                                     ])
            
                                
        jsdata = simplejson.dumps(formated_result)
        print "JSDATA", jsdata
        # Going to do extra formating here, to simplify the template.
        raceresults.append({'racedata':raceid[1],
                            'roundnumber':raceid[2],
                            'racenumber':raceid[3],
                            'racedate':raceid[4],
                            'tagid':raceid[0],
                            'individual_results':jsdata})
    
    print "RACERESULTS", raceresults    
    ctx = Context({'trackname':p.trackkey, 'raceresults':raceresults})
    return render_to_response('recentresults_data.html', ctx)