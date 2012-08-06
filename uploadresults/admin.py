from models import UploadRecord, UploadedRaces
from django.contrib import admin


class UploadRecordAdmin(admin.ModelAdmin):
    list_display = ('filename', 'user', 'ip', 'filesize', 'filemd5', 'uploaddate')
    list_filter = ['user', 'ip']

class UploadedRacesAdmin(admin.ModelAdmin):
    list_display = ('upload', 'racedetails') 

admin.site.register(UploadRecord, UploadRecordAdmin)
admin.site.register(UploadedRaces, UploadedRacesAdmin)
