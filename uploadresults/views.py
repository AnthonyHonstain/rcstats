'''
Created on July 2012

@author: Anthony Honstain
'''

from django.shortcuts import render_to_response, get_object_or_404
from django.contrib.auth import authenticate, login
from django.core.urlresolvers import reverse
from django.template import RequestContext

from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django import forms

from django.conf import settings
from models import UploadRecord
from rcdata.models import SupportedTrackName
from rcdata.models import TrackName
from python_scripts.ProcessRawLaps.singlerace import SingleRace
from python_scripts.ProcessRawLaps.rcscoringprotxtparser import RCScoringProTXTParser

import bleach
import hashlib
import logging
import os.path
import re
import sys
import time
import traceback


def login_user(request):
    state = "Please log in below..."
    username = password = ''
    if request.POST:
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(username=username, password=password)
        if user is not None:
            if user.is_active:
                login(request, user)
                state = "You're successfully logged in!"
                return render_to_response('upload_start.html', {}, context_instance=RequestContext(request))
            
            else:
                state = "Your account is not active, please contact the site admin."
        else:
            state = "Your username and/or password were incorrect."

    return render_to_response('auth.html',
                              {'state':state, 'username': username},
                              context_instance=RequestContext(request))


class UploadFileForm(forms.Form):
    #title = forms.CharField(max_length=50)
    file = forms.FileField()
    
    
@login_required(login_url='/login')
def upload_start(request):    
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
                
        # What causes the form to not be valid? You can check by putting
        # {{ form.errors }} {{ form.non_field_errors }} in the template.
        
        if (form.is_valid() and 'file' in request.FILES):
            # Need to make sure the key used for FILES[ ] matches up with the
            # form in the template.
            
            # Record the information we need about the fileupload. Not everything
            # is immediately record (we record the hash and local file name later).
            log_entry = UploadRecord(origfilename=request.FILES['file'].name,
                               ip=request.get_host(),
                               user=request.user,
                               filesize=request.FILES['file'].size,
                               uploaddate=time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()),
                               processed=False)
            log_entry.save()
            
            # Set the filename, for now I want to use the primary key, but in the future I may change it.
            # WARNING - do not use any user date for the filename.            
            md5hexdigest = _handle_uploaded_file(request.FILES['file'], str(log_entry.id))
                                    
            updatelog = UploadRecord.objects.get(pk=log_entry.id)
            updatelog.filename = str(log_entry.id)
            updatelog.filemd5 = md5hexdigest
            updatelog.save()
            
            return HttpResponseRedirect('/upload_start/' + str(log_entry.id))
        else:
            error = "Failed to upload file."
            return render_to_response('upload_start.html', {'form':form, 'error_status': error}, context_instance=RequestContext(request))

    else:
        form = UploadFileForm()
    return render_to_response('upload_start.html',
                              {'form': form},
                              context_instance=RequestContext(request))


def _handle_uploaded_file(f, filename):           
    md5 = hashlib.md5()   
    with open(os.path.join(settings.MEDIA_USER_UPLOAD, filename), 'wb+') as destination:
        for chunk in f.chunks():
            destination.write(chunk)
            md5.update(chunk)
            
    # Note - we are using a hex digest here instead of plain 'digest'
    # so that we can store it as a string in the db without dealing with
    # encoding it.
    return md5.hexdigest()



class TrackNameForm(forms.Form):
    supported_tracks = map(lambda x : (x['trackkey__id'], x['trackkey__trackname']), 
                       SupportedTrackName.objects.all().select_related().values("trackkey__id", "trackkey__trackname"))
    
    track_id = forms.ChoiceField(choices=supported_tracks)

    

@login_required(login_url='/login')
def upload_validate(request, upload_id):
    """    
    We want to provide a form for the user to change the trackname before
    it is processed and placed in the database.
    
    A large chunk of this code is error handling and file checking
    to make sure the results were parsed correctly (and hopefully
    give enough information for me to fix the problem later or to
    let them make the change and retry the upload).
    
    Overview of the code:
        We get the record of the upload from the DB
        We then get the singlerace objects (parse each item in the file).
        Display these objects to user.
        
        
    """
    upload_record = get_object_or_404(UploadRecord, pk=upload_id)

    # We have already recorded this file as processed, there is nothing more
    # this script can do at this point. It is likely a user error.
    # I only think this will occur if you try to reload the results processing page.
    if (upload_record.processed):
        state = "File has already been processed. If you believe there was an ERROR, than instead " +\
            "of trying to re-upload the race you should contact an administrator for help."
        return render_to_response('upload_validate.html',
                                  {'state':state,},
                                  context_instance=RequestContext(request))
    
    # ***************************************************************
    # Error checking, we will parse the file from memory and log/communicate
    # the problems as best as possible. 
    # LOTS OF VALIDATION PRIOR TO MOVING TO THE NEXT STEP.
    # ***************************************************************
    
    logger = logging.getLogger("uploadprocessing")
    # Get the uploaded file name from the database.
    filename = os.path.join(settings.MEDIA_USER_UPLOAD, upload_record.filename)

    # Error message in case processing of the file fails for any reason.    
    state = "We were unable to process the file you uploaded. Please double " +\
            "check that the file is in the supported format. If you still believe " +\
            "there is an error, please contact the admin."            
    
    try:
        prevalidation_race_list = _parse_file(filename)
    except IOError:
        logger.error("Invalid filename=" + filename)        
        return render_to_response('upload_validate.html',
                                  {'state':state,},
                                  context_instance=RequestContext(request))         
    except Exception as e:
        exc_type, exc_value, exc_traceback = sys.exc_info()
        trace = traceback.format_exception(exc_type, exc_value, exc_traceback)
        logger.error("Unable to process file: {0} exception:{1} \n {2}".format(filename, str(e), trace))
        return render_to_response('upload_validate.html',
                                  {'state':state,},
                                  context_instance=RequestContext(request)) 
        
    # Now that we have a possible set of race result, we are most concerned with
    # making sure they have a valid track name prior to upload. If they have bad
    # class names or other garbage data, it will not be as big a deal.
    
    # There must be at least 1 race.
    if (len(prevalidation_race_list) < 1):
        logger.error("No races found in the file=" + filename)        
        return render_to_response('upload_validate.html',
                                  {'state':state,},
                                  context_instance=RequestContext(request)) 
    
    upload_trackname = prevalidation_race_list[0].trackName
    
    # We are going to force them to have a trackname already set. 
    #     It makes this code so much simpler, if they need to change 
    #     the trackname (then I can easily replace it and save the 
    #     modified version).
    if (upload_trackname.strip() == ""):
        state = "You MUST have a trackname set in the race results to proceed."
        logger.error("There was no trackname set in the file=" + filename)        
        return render_to_response('upload_validate.html',
                                  {'state':state,},
                                  context_instance=RequestContext(request)) 
    
    # Validate all the track names are the same. 
    #     I don't think this would ever happen but I am going 
    #     to check because I don't want people doing it.    
    for race in prevalidation_race_list:
        if (race.trackName != upload_trackname):
            logger.error("Not all races have the same trackname in the file=" + filename)        
            return render_to_response('upload_validate.html',
                                      {'state':state,},
                                      context_instance=RequestContext(request)) 


    # ***************************************************************
    # Basic Validation Complete, we have been able to at least parse
    # the upladed file and if NOT we have returned and communicated/logged
    # the problem.
    # ***************************************************************
    if request.method == 'POST':
        form = TrackNameForm(request.POST)    
        if (form.is_valid()):
            # Note - They have clicked on the submit button and have set a desired trackname
            # We not want to process and upload the file.
            cd = form.cleaned_data
            #_insert_results_database()
            print "form.track_id:", cd['track_id']
            track = get_object_or_404(TrackName, pk=cd['track_id'])
            
            # Now we know the trackname that the file should be using.
            # We want to save this information from the user to a new file.
            #     This is to hopefully simplify restoring data in the event of
            #     an emergency (all that would be needed would be these text files).
            _modify_trackname(upload_record.filename, upload_trackname, track.trackname)
            
            # Process each race and load it into the DB.             
            for race in prevalidation_race_list:
                # Set the new trackname on each of the race objects.
                race.trackName = track.trackname
                        
                print "UPLOAD FILE TO DB!- ", race.raceClass
                _process_singlerace(race)
            
            # Log this upload as processed (we do NOT want to support
            # multiple attempts at uploading the file).
            upload_record.processed = True
            upload_record.save()
            # WARNING STUB - We want to direct them to the page for the races they uploaded.
            #return HttpResponseRedirect('/displayresults/singleracedetailed/' + str(track.id))
            return HttpResponseRedirect(reverse('rcstats.displayresults.views.singleracedetailed', 
                                                args=(track.id,)))
            
        else:
            logger.error("Invalid form, file=" + filename)        
            return render_to_response('upload_validate.html',
                                      {'state':"Invalid option selected.",},
                                      context_instance=RequestContext(request))
        
    else:             
        # If the track name is not already supported, we will suggest they change it.
        supported_track_obj = SupportedTrackName.objects.filter(trackkey__trackname__exact=upload_trackname)
        if (supported_track_obj == None):
            # They are using an unsupported track, we are going to force them to use a supported track.
            
            # This is where we need to display a special message letting them know how
            # to proceed.
            state = "Warning - The file has a trackname which is not a featured track."
            
            #
            # TODO - This is a stub!
            #
        
        form = TrackNameForm()
                   
            
    return render_to_response('upload_validate.html',
                              {'form':form,
                               'prevalidation_race_list':prevalidation_race_list,},
                              context_instance=RequestContext(request))


#from rcdata.models import SupportedTrackName
#from rcdata.models import TrackName
from rcdata.models import RacerId
from rcdata.models import SingleRaceDetails
from rcdata.models import SingleRaceResults
from rcdata.models import LapTimes

def _process_singlerace(race):
    '''
    Insert the information in the singlerace object into the DB.
    
    Conditions - The trackname is already in the db.
    '''
    
    # Track - We assume it has already been validated that this is a known track.
    #    NOTE - we do not want to be creating new tracks in this code, if the track
    #    is new it probably means they are not uploading appropriately.
    track_obj = TrackName.objects.get(trackname=race.trackName)
        
    
    # Insert Racers - We want to add a new racerid if one does not already exist.
    racer_obj_list = []
    for racerdata in race.raceHeaderData:
        racer_obj, created = RacerId.objects.get_or_create(racerpreferredname=racerdata['Driver'])
        
    
    # Find race length
    
    # Find Winning lap count
    
    
    # Insert Race Details
    
    # Insert Race Laps
    
    # Insert Race Results

    return


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


def _modify_trackname(uploaded_filename, origional_trackname, new_trackname):
    '''
    _modify_trackname is a helper function handle replacing the trackname
    in the file the user uploaded and creating an updated version of the uploaded
    file. 
    
    This could be done with a one line command in bash, but I think at this
    stage in development, I feel more better having python handle it than 
    trying to run a special command (espcially on the live server).
    '''
    origional_filepath = os.path.join(settings.MEDIA_USER_UPLOAD, uploaded_filename)
    new_filepath = os.path.join(settings.MEDIA_USER_UPLOAD, uploaded_filename + "_validated")
    
    pattern = re.compile(origional_trackname, re.IGNORECASE)
            
    with open(origional_filepath) as f, open(new_filepath, 'wb+') as destination: 
        content = f.readlines()
        for line in content:
            search_result = pattern.search(line)
            if (search_result):
                newline = " " * search_result.start(0)
                newline += new_trackname + "\n"
                destination.write(newline)
            else:
                destination.write(line)
    return
        