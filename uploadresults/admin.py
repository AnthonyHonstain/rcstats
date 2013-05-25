from models import UploadRecord, UploadedRaces
from models import EasyUploaderPrimaryRecord, EasyUploadRecord, EasyUploadedRaces
from django.contrib import admin


class UploadRecordAdmin(admin.ModelAdmin):
    list_display = ('filename', 'user', 'ip', 'filesize', 'filemd5', 'uploaddate')
    list_filter = ['user', 'ip']
    ordering = ('-uploaddate',)

class UploadedRacesAdmin(admin.ModelAdmin):
    list_display = ('upload', 'racedetails') 

class EasyUploaderPrimaryRecordAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'ip', 'trackname', 'filecount', 'filecountsucceed', 'uploadstart')
    list_filter = ['user', 'ip', 'trackname']
    ordering = ('-uploadstart',)
    
class EasyUploadRecordAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'ip', 'trackname', 'filename', 'filesize', 'filemd5', 'uploadstart', 'errorenum')
    list_filter = ['user', 'ip', 'trackname']
    ordering = ('-uploadstart',)

class EasyUploadedRacesAdmin(admin.ModelAdmin):
    list_display = ('upload', 'get_track', 'get_racedata', 'get_racedate', 'racedetails') 
    
    # http://stackoverflow.com/questions/163823/can-list-display-in-a-django-modeladmin-display-attributes-of-foreignkey-field
    def get_track(self, obj):
        return '%s'%(obj.racedetails.trackkey)
    get_track.short_description = 'Track'
    def get_racedata(self, obj):
        return '%s'%(obj.racedetails.racedata)
    get_racedata.short_description = 'ClassName'
    def get_racedate(self, obj):
        return '%s'%(obj.racedetails.racedate)
    get_racedate.short_description = 'Date'

admin.site.register(EasyUploaderPrimaryRecord, EasyUploaderPrimaryRecordAdmin)
admin.site.register(EasyUploadRecord, EasyUploadRecordAdmin)
admin.site.register(EasyUploadedRaces, EasyUploadedRacesAdmin)
admin.site.register(UploadRecord, UploadRecordAdmin)
admin.site.register(UploadedRaces, UploadedRacesAdmin)
