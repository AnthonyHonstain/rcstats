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
from models import UploadedRaces
from rcstats.ranking.models import RankedClass
from rcstats.ranking.views import process_ranking 

from rcstats.rcdata.views import collapsenames

from rcstats.rcdata.models import SupportedTrackName
from rcstats.rcdata.models import TrackName
from rcstats.rcdata.models import RacerId
from rcstats.rcdata.models import SingleRaceDetails
from rcstats.rcdata.models import SingleRaceResults
from rcstats.rcdata.models import LapTimes
from rcstats.python_scripts.ProcessRawLaps.rcscoringprotxtparser import RCScoringProTXTParser

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
    
    def __init__(self, *args, **kwargs):
        super(TrackNameForm, self).__init__(*args, **kwargs)

        # This is a one-liner to get all the track id and names into a list of tuples.
        # Required formating for ChoiceField.
        # Example [(1, "TRCR"), (2, "BRCR"), ...]        
        supportedtrack_choices = map(lambda x : (x['trackkey__id'], x['trackkey__trackname']), 
                       SupportedTrackName.objects.all().select_related().values("trackkey__id", "trackkey__trackname"))
        self.fields['track_id'] = forms.ChoiceField(choices=supportedtrack_choices)
        

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

    # General Error message in case processing of the file fails for any reason.    
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
    # the upladed file and if NOT, we have returned and communicated/logged
    # the problem.
    # ***************************************************************
    if request.method == 'POST':
        form = TrackNameForm(request.POST)  
        if (form.is_valid()):
            # Note - They have clicked on the submit button and have set a desired trackname
            # We want to process and upload the file.
            cd = form.cleaned_data
            track = get_object_or_404(TrackName, pk=cd['track_id'])
            
            # Now we know the trackname that the file should be using.
            # We want to save this information from the user to a new file.
            #     This is to hopefully simplify restoring data in the event of
            #     an emergency (all that would be needed would be these text files).
            _modify_trackname(upload_record.filename, upload_trackname, track.trackname)
            
            uploaded_races_list = []
            # Process each race and load it into the DB.             
            for race in prevalidation_race_list:
                # Set the new trackname on each of the race objects.
                race.trackName = track.trackname
                        
                try:
                    new_singleracedetails = _process_singlerace(race)
                    # We are going to track who uploaded this race.
                    UploadedRaces.objects.create(upload=upload_record, racedetails=new_singleracedetails)
                    uploaded_races_list.append((race.raceClass, new_singleracedetails.id))
                except FileAlreadyUploadedError:
                    logger.error("This race has already been uploaded, filename=" + filename + " raceobject:" + str(race))        
                    return render_to_response('upload_validate.html',
                                              {'state':"This race has ALREADY been uploaded. " + state,},
                                              context_instance=RequestContext(request)) 
                except Exception as e:
                    exc_type, exc_value, exc_traceback = sys.exc_info()
                    trace = traceback.format_exception(exc_type, exc_value, exc_traceback)
                    logger.error("Unable to process file: {0} exception:{1} \n {2}".format(filename, str(e), trace))
                    return render_to_response('upload_validate.html',
                                              {'state':state,},
                                              context_instance=RequestContext(request)) 
                    
                    
            # Log this upload as processed (we do NOT want to support
            # multiple attempts at uploading the file).
            upload_record.processed = True
            upload_record.save()
            
            return render_to_response('upload_complete.html',
                                      {'uploaded_races_list':uploaded_races_list},
                                      context_instance=RequestContext(request))
    
            
            
        else:
            logger.error("Invalid form, file=" + filename + " form.error:" + str(form.errors))        
            return render_to_response('upload_validate.html',
                                      {'state':"Invalid option selected.",},
                                      context_instance=RequestContext(request))
    
    # We are always going to require that the select a trackname, at least for now.
    # I can see this behavior changing the future to streamline the process.
    form = TrackNameForm()
                   
    return render_to_response('upload_validate.html',
                              {'form':form,
                               'uploadtrackname': upload_trackname,
                               'prevalidation_race_list':prevalidation_race_list,},
                              context_instance=RequestContext(request))


def _process_singlerace(race):
    '''
    Insert the information in the singlerace object into the DB.
    
    Conditions - The trackname is already in the db.
    '''
    
    # ====================================================
    # Trackname
    # ====================================================
    # Track - We assume it has already been validated that this is a known track.
    #    NOTE - we do not want to be creating new tracks in this code, if the track
    #    is new it probably means they are not uploading appropriately.
    track_obj = TrackName.objects.get(trackname=race.trackName)
            
    # ====================================================
    # Insert Racers
    # ====================================================
    # We want to add a new racerid if one does not already exist.
    for racer in race.raceHeaderData:
        racer_obj, created = RacerId.objects.get_or_create(racerpreferredname=racer['Driver'])
        racer['racer_obj'] = racer_obj
        
    # ====================================================
    # Insert Race Details
    # ====================================================
    # Find race length
    racelength = _calculate_race_length(race.raceHeaderData)
    
    # Find Winning lap count
    maxlaps = 0;
    for racer in race.raceHeaderData:
        if (racer['Laps'] > maxlaps):
            maxlaps = racer['Laps']
      
    # Parse this '10:32:24 PM  8/13/2011'
    timestruct = time.strptime(race.date, "%I:%M:%S %p %m/%d/%Y")    
    # Format the time to get something like this '2012-01-04 20:20:20-01'
    formatedtime = time.strftime('%Y-%m-%d %H:%M:%S', timestruct)
    currenttime = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
    
    # We want to stop if this race is already in the database
    
    test_objs = SingleRaceDetails.objects.filter(trackkey=track_obj,
                                            racedata=race.raceClass,    
                                            roundnumber=race.roundNumber,
                                            racenumber=race.raceNumber,
                                            racedate=formatedtime,
                                            racelength=racelength,
                                            winninglapcount=maxlaps)
    if (len(test_objs) != 0):    
        # We want to tell the user since this not what they wanted.
        # We can be reasonably certain this file has already been uploaded.
        raise FileAlreadyUploadedError(race, "File already uploaded")
        
    details_obj = SingleRaceDetails(trackkey=track_obj,
                                    racedata=race.raceClass,
                                    roundnumber=race.roundNumber,
                                    racenumber=race.raceNumber,
                                    racedate=formatedtime,
                                    uploaddate=currenttime,
                                    racelength=racelength,
                                    winninglapcount=maxlaps)
    details_obj.save()
    
    # ====================================================
    # Insert Race Laps
    # ====================================================    
    # For each racer in the raceHeaderData
    for racer in race.raceHeaderData:        
        # Upload each lap for this racer, their care number - 1 indicates
        # the index of their laps in the lapRowsTime list.
        index = racer['Car#'] - 1
        
        # This would be a good place to check and see if there are enough laps, it
        # has been observed that the parser can fail to get everyone's lap data (another
        # pending bug).        
        for row in range(0, len(race.lapRowsTime[index])):
            # print "Debug: ", racer
            # print "Debug: ", lapRowsPosition[index]
            if (race.lapRowsPosition[index][row] == ''):
                race.lapRowsPosition[index][row] = None
                race.lapRowsTime[index][row] = None

            lap_obj = LapTimes(raceid=details_obj, 
                               racerid=racer['racer_obj'], 
                               racelap=row, 
                               raceposition=race.lapRowsPosition[index][row],
                               racelaptime=race.lapRowsTime[index][row])
            lap_obj.save()
            
    # ====================================================
    # Insert Race Results
    # ====================================================
    '''
        Example of the data structure we will work with here:
                          [{"Driver":"TOM WAGGONER", 
                          "Car#":"9", 
                          "Laps":"26", 
                          "RaceTime":"8:07.943", 
                          "Fast Lap":"17.063", 
                          "Behind":"6.008",
                          "Final Position":9} , ...]
    '''
    for racer in race.raceHeaderData:
        if (racer['RaceTime'] == ''):
            racer['RaceTime'] = None
        if (racer['Fast Lap'] == ''):
            racer['Fast Lap'] = None
        if (racer['Behind'] == ''):
            racer['Behind'] = None
           
        individual_result = SingleRaceResults(raceid=details_obj, 
                                              racerid=racer['racer_obj'],
                                              carnum=racer['Car#'], 
                                              lapcount=racer['Laps'], 
                                              racetime=racer['RaceTime'],
                                              fastlap=racer['Fast Lap'],
                                              behind=racer['Behind'],
                                              finalpos=racer['Final Position'])
        individual_result.save()       


    # ===============================================================
    # Collapse alias names.
    # ===============================================================
    collapsenames()

    # ===============================================================
    # Do we need to update ranking?
    # TESTING/PROTOTYPE - have not decided if this is the best place for this.
    # WARNING - The names need to be collapsed first, or it will confuse the ranking.
    # ===============================================================
    # Lookup if this class is being ranked.
    pattern = re.compile("[A-Z][1-9]? main", re.IGNORECASE)
    start_index = pattern.search(race.raceClass).start(0)
    trimmed_class = race.raceClass[:start_index].strip('+- ')
    
    rankedclass = RankedClass.objects.filter(trackkey__exact=track_obj.id,
                                             raceclass__icontains=trimmed_class)
    if (len(rankedclass) > 0):
        # We found a ranked class to process its ranking data.
        process_ranking(rankedclass[0])

    return details_obj


def _calculate_race_length(raceHeaderData):
    '''
    Look at all the racetimes and take largest number of minutes (note: we only
    look at the number of minutes in the race, not the number of seconds).
    
    Some people may be recorded as not going the entire race time, or have no
    race time at all.
    '''
    maxNumMinutes = 0
    
    for racer in raceHeaderData:
        if (racer["RaceTime"] == ''):
            continue
        else:
            numMin = int(racer["RaceTime"].split(':')[0])
            if numMin > maxNumMinutes:
                maxNumMinutes = numMin
    
    return maxNumMinutes


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


class Error(Exception):
    """Base class for exceptions in this module."""
    pass

class FileAlreadyUploadedError(Error):
    """Exception raised when a race has already been placed in the system..

    Attributes:
        singlerace -- singlerace object that was being processed.
    """

    def __init__(self, singlerace, msg):
        self.singlerace = singlerace
        self.msg = msg
        