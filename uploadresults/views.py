from django.shortcuts import render_to_response, get_object_or_404
from django.contrib.auth import authenticate, login
from django.template import RequestContext

from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django import forms

from django.conf import settings
from models import UploadRecord
from python_scripts.ProcessRawLaps.singlerace import SingleRace
from python_scripts.ProcessRawLaps.rcscoringprotxtparser import RCScoringProTXTParser

import bleach
import hashlib
import logging
import os.path
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


@login_required(login_url='/login')
def upload_validate(request, upload_id):
    """    
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
    
    logger = logging.getLogger("uploadprocessing")
    
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
    for race in prevalidation_race_list:
        print race.lapRowsTime
    
    return render_to_response('upload_validate.html',
                              {'prevalidation_race_list':prevalidation_race_list,},
                              context_instance=RequestContext(request))


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