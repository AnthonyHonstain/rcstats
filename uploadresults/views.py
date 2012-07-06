from django.shortcuts import render_to_response
from django.contrib.auth import authenticate, login
from django.template import RequestContext

from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django import forms


class UploadFileForm(forms.Form):
    #title = forms.CharField(max_length=50)
    file  = forms.FileField()


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

    
@login_required(login_url='/login')
def upload_start(request):    
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
                
        # What causes the form to not be valid?
        if form.is_valid():
            # Need to make sure the key used for FILES[ ] matches up with the
            # form in the template.
            handle_uploaded_file(request.FILES['file'])
            return HttpResponseRedirect('/upload_start')
        else:
            error = "Failed to upload file:" + request.FILES['file'].name
            return render_to_response('upload_start.html', {'form':form, 'error_status': error}, context_instance=RequestContext(request))

    else:
        form = UploadFileForm()
    return render_to_response('upload_start.html', {'form': form}, context_instance=RequestContext(request))



def handle_uploaded_file(f):           
    #print "name:", f.name
    #print "size:", f.size
   
    with open('/home/asymptote/Desktop/rcstats/rcdata_media/fileupload/testfile.txt', 'wb+') as destination:
        for chunk in f.chunks():
            destination.write(chunk)



