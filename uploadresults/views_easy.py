'''
Created on April 2013

The revised uploader, I further stream lined the user scenario so that
you need to click less buttons to get the nights race results uploaded.

    This handles the bulk of the heavy lifting in the upload process, organizing them 
    for storage, validating and guiding the user, and pushing into the database.
    
    There is lots of special logic to collect and process metadata like ranking or
    fixing of the class names or racer names.

----------------------------------------------
SIMPLE OVERIVEW
----------------------------------------------
    STEP 1) easyupload_track
        - 
    STEP 2) easyupload_fileselect
        -
    STEP 3) easyupload_results
        - Take the stuff from part 2 and start uploading.

@author: Anthony Honstain
'''

from django.shortcuts import render_to_response, get_object_or_404
from django.contrib.auth import authenticate, login
from django.template import RequestContext

from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django import forms

from django.conf import settings
from models import EasyUploaderPrimaryRecord, EasyUploadRecord
from models import UploadRecord
from models import UploadedRaces
from process_singlerace import process_singlerace, FileAlreadyUploadedError
from rcstats.ranking.models import RankedClass
from rcstats.ranking.views import process_ranking 

from rcstats.rcdata.models import SupportedTrackName
from rcstats.rcdata.models import TrackName
from rcstats.rcdata.models import SingleRaceDetails
from rcstats.python_scripts.ProcessRawLaps.rcscoringprotxtparser import RCScoringProTXTParser

import hashlib
import logging
import os.path
import re
import sys
import time
import traceback


class UploadFileForm(forms.Form):
    #title = forms.CharField(max_length=50)
    file = forms.FileField()

@login_required(login_url='/login')
def easyupload_track(request):
    '''
    Initial page in the easy upload, provide a list of buttons (each track)
    that can be clicked to navigate to the next step.
    
    Step 1
    '''
    track_list = SupportedTrackName.objects.all().order_by('trackkey__trackname')
    return render_to_response('easyupload/easyupload_track.html', {'track_list':track_list}, context_instance=RequestContext(request))

@login_required(login_url='/login')
def easyupload_fileselect(request, track_id):
    '''
    The controller responsible for the file upload.
    
    Step 2
    
    I have modified the post to support multiple file at a single time. I have not attempted
    to user any fancy jquery, I am going to attempt the easy route.
    
    Example of request.FILES when I attempt multiple uploads.
        <MultiValueDict: {u'file': 
            [<InMemoryUploadedFile: 912503d1335331695-race-results-round3.txt (text/plain)>, 
            <InMemoryUploadedFile: 913274d1335482296-race-results-round1.txt (text/plain)>, 
            <InMemoryUploadedFile: 913275d1335482311-race-results-round2.txt (text/plain)>]}>
    Example when I request only a single file:
        <MultiValueDict: {u'file': 
        [<InMemoryUploadedFile: 912503d1335331695-race-results-round3.txt (text/plain)>]}>
    '''
    track = get_object_or_404(TrackName, pk=track_id)
    
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
                
        # What causes the form to not be valid? You can check by putting
        # {{ form.errors }} {{ form.non_field_errors }} in the template.
        
        if (form.is_valid() and 'file' in request.FILES):
            # Need to make sure the key used for FILES[ ] matches up with the
            # form in the template.
            
            # Example: print request.FILES
            # <MultiValueDict: {u'file': [<InMemoryUploadedFile: 912503d1335331695-race-results-round3.txt (text/plain)>, 
            #     <InMemoryUploadedFile: 913274d1335482296-race-results-round1.txt (text/plain)>, 
            #     <InMemoryUploadedFile: 913275d1335482311-race-results-round2.txt (text/plain)>]}>
            
            # Bug - This is not the ideal solution but I need quick 
            # way for this to work in production and in development.
            #     In the dev enviro, 'HTTP_X_FORWARD_FOR' is not a 
            #     key in request.META
            ip = "127.0.0.1" 
            if 'HTTP_X_FORWARDED_FOR' in request.META:
                ip = request.META['HTTP_X_FORWARDED_FOR']

            file_list = request.FILES.getlist('file')
            
            # First create a record for this upload action
            primary_record = EasyUploaderPrimaryRecord(user=request.user, 
                                                       ip=ip, 
                                                       filecount=len(file_list), 
                                                       filecountsucceed=0, 
                                                       uploadstart=time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()),
                                                       trackname=track)
            primary_record.save()

            # For reference http://stackoverflow.com/questions/851336/multiple-files-upload-using-same-input-name-in-django
            for inmem_file in file_list:
                _process_inmemmory_file(primary_record, ip, request.user, inmem_file)
                
            return HttpResponseRedirect('/easyupload_results/' + str(primary_record.id))
        else:
            error = "Failed to upload file."
            return render_to_response('easyupload/easyupload_fileselect.html',
                                      {'form':form, 'track': track, 'error_status': error}, 
                                      context_instance=RequestContext(request))

    else:
        form = UploadFileForm()
    return render_to_response('easyupload/easyupload_fileselect.html',
                              {'form': form, 'track': track},
                              context_instance=RequestContext(request))

def _process_inmemmory_file(primary_record, ip, user, inmem_file):
    '''
    Helper function for Step 2, we want the upload record to record each race that was uploaded.
    
    The input file will be written to disk and have a new record created for the file.
    
    primary_record: the EasyUploaderPrimaryRecord for the new upload record. 
    ip: the ip recorded with the upload
    user: the django user recorded in the request
    file: the InMemoryUploadedFile
    '''
    # Record the information we need about the fileupload. Not everything
    # is immediately recorded (we record the hash and local file name later).
    log_entry = EasyUploadRecord(uploadrecord=primary_record,
                                 origfilename=inmem_file.name,
                                 ip=ip,
                                 user=user,
                                 filesize=inmem_file.size,
                                 uploadstart=time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()),
                                 processed=False)
    log_entry.save()
    
    # Set the filename, for now I want to use the primary key, but in the future I may change it.
    # WARNING - do not use any user data for the filename.            
    md5hexdigest = _handle_uploaded_file(inmem_file, str(log_entry.id))
                            
    updatelog = EasyUploadRecord.objects.get(pk=log_entry.id)
    updatelog.filename = str(log_entry.id)
    updatelog.filemd5 = md5hexdigest
    updatelog.save()

def _handle_uploaded_file(f, filename):
    """
    Helper function for Step 2 - write the file to disk and calculate a hash on the data.
    """
    md5 = hashlib.md5()   
    with open(os.path.join(settings.MEDIA_USER_UPLOAD, filename), 'wb+') as destination:
        for chunk in f.chunks():
            destination.write(chunk)
            md5.update(chunk)
            
    # Note - we are using a hex digest here instead of plain 'digest'
    # so that we can store it as a string in the db without dealing with
    # encoding it.
    return md5.hexdigest()

@login_required(login_url='/login')
def easyupload_results(request, upload_id):
    """
    Final view to trigger the final generation of race results.
    
    Step 3
    """
    primary_upload_record = get_object_or_404(EasyUploaderPrimaryRecord, pk=upload_id)
    track = primary_upload_record.trackname
        
    # We have already recorded this file as processed, there is nothing more
    # this script can do at this point. It is likely a user error.
    if (primary_upload_record.filecount == primary_upload_record.filecountsucceed):
        general_error_message = "All of these files have been processed. It is likely that the races are already in the system. If they missing an administrator can probably fix the problem quickly."
        return render_to_response('upload_validate.html',
                                  {'general_error': True, 'general_error_message':general_error_message},
                                  context_instance=RequestContext(request))
    
    # TODO - move this up to a global so I reference it here and in the template and comment on it.
    upload_errors = ['Pass',
                     'Invalid filename - it is possible the upload to the server drive failed'
                     'Unable to parse the file - likely is has incompatible format'
                     'No races found in the file',
                     'There was no trackname/header set',
                     'Not all races in the file had the same trackname/header']
        
    upload_records = EasyUploadRecord.objects.filter(uploadrecord=primary_upload_record)
    
    prevalidated_file_races = []
    # =======================================================================
    # Primary loop - process each file uploaded.
    # =======================================================================
    for record in upload_records:
        prevalidated_races = _initial_validation_of_uploaded_file(record)
        if prevalidated_races:
            prevalidated_file_races.append(prevalidated_races)
            
    print
    print "READY TO START UPLOADING"
    print
    
    error_list = [x.errorenum for x in upload_records if x.errorenum]
    
    context = {'upload_records':upload_records,
               'general_error':len(error_list) > 0,
               'general_error_message':None }
    return render_to_response('easyupload/easyupload_validate.html',
                              context,
                              context_instance=RequestContext(request))

def _initial_validation_of_uploaded_file(easy_upload_record):
    """
    Helper function to provide initial validation of the uploaded race file.
    """
    logger = logging.getLogger("uploadprocessing")
    # Get the uploaded file name from the database.
    filename = os.path.join(settings.MEDIA_USER_UPLOAD, easy_upload_record.filename)
    
    # =======================================================================
    # Phase A) validate I can retrieve the file and parse it.
    #    I expect most problems to be in the category (did they upload shit).
    # =======================================================================
    try:
        prevalidation_race_list = _parse_file(filename)
    except IOError:
        logger.error("Invalid filename=" + filename)
        easy_upload_record.errorenum = 1
        easy_upload_record.save()
        return
    except Exception as e:
        exc_type, exc_value, exc_traceback = sys.exc_info()
        trace = traceback.format_exception(exc_type, exc_value, exc_traceback)
        logger.error("Unable to process file: {0} exception:{1} \n {2}".format(filename, str(e), trace))
        easy_upload_record.errorenum = 2
        easy_upload_record.save()
        return

    # =======================================================================
    # Phase B) sanity check that there is a race, it has a trackname, and the same trackname.
    # =======================================================================
    # There must be at least 1 race.
    if (len(prevalidation_race_list) < 1):
        logger.error("No races found in the file=" + filename)
        easy_upload_record.errorenum = 3
        easy_upload_record.save()
        return
    
    upload_trackname = prevalidation_race_list[0].trackName
    
    # We are going to force them to have a trackname already set. 
    #     It makes this code so much simpler, if they need to change 
    #     the trackname (then I can easily replace it and save the 
    #     modified version).
    if (upload_trackname.strip() == ""):
        logger.error("There was no trackname set in the file=" + filename)        
        easy_upload_record.errorenum = 4
        easy_upload_record.save()
        return
    
    # Validate all the track names are the same. 
    #     I don't think this would ever happen but I am going 
    #     to check because I don't want people doing it.    
    for race in prevalidation_race_list:
        if (race.trackName != upload_trackname):
            logger.error("Not all races have the same trackname in the file=" + filename)        
            easy_upload_record.errorenum = 5
            easy_upload_record.save()
            return

    return prevalidation_race_list


def _parse_file(filename):
    """
    There a many possible scenarios that could cause this to fail,
    we want to record as much as possible so either the admin or
    the user can make a change and hopefully succeed.
    
    I expect that people will accidentally (hopefully) throw a number
    invalid files at this. 
    """
    raceresults_list = []    
            
    with open(filename) as f: 
        content = f.readlines()
        
        currentRaceStartIndex = 0
        lastRace = ""
      
        #Process the first race.
        for i in range(1, len(content)):
            
            if (content[i].find('www.RCScoringPro.com') != -1):
                # This means we have found a new race in the file.
          
                # print "=" * 100
                # print content[currentRaceStartIndex:i]
              
                # This is a special check, if they have modified the race
                # manually, there will two results for the same race and
                # we want to take the second.
                if (lastRace == content[currentRaceStartIndex + 4]):
                    currentRaceStartIndex = i
                    continue
          
                singlerace = RCScoringProTXTParser(filename, content[currentRaceStartIndex:i])
                raceresults_list.append(singlerace)
                
                lastRace = content[currentRaceStartIndex + 4]
                currentRaceStartIndex = i
  
        # This triggers when we have found the final race in the file.
        singlerace = RCScoringProTXTParser(filename, content[currentRaceStartIndex:len(content)])
        raceresults_list.append(singlerace)
    
    return raceresults_list