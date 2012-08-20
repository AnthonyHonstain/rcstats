'''
Created on July 2012

@author: Anthony Honstain
'''
from django.conf import settings
from django.contrib.auth.models import User
from django.test import TestCase
from django.test.client import Client

import datetime
import os
import time

import models
from rcstats.rcdata.models import LapTimes
from rcstats.rcdata.models import SingleRaceDetails
from rcstats.rcdata.models import SingleRaceResults
from rcstats.rcdata.models import SupportedTrackName
from rcstats.rcdata.models import TrackName
from rcstats.rcdata.models import RacerId

class SingleRace(TestCase):

    singlerace_testfile = '''Scoring Software by www.RCScoringPro.com                9:26:42 PM  7/17/2012

                   TACOMA R/C RACEWAY

MODIFIED BUGGY A Main                                         Round# 3, Race# 2

________________________Driver___Car#____Laps____RaceTime____Fast Lap___Behind_
RacerFirstCar2, Jon            #2         28         8:18.588         17.042                  
RacerSecondCar4, Jon            #4         27         8:08.928         17.116                  
RacerThirdCar5, Jon            #5         26         8:00.995         17.274                  
RacerFourthCar3, Jon            #3         25         8:02.680         17.714                  
RacerFifthCar1, Jon            #1          1           35.952         35.952                  

 ___1___ ___2___ ___3___ ___4___ ___5___ ___6___ ___7___ ___8___ ___9___ ___10__
 5/35.95 1/26.24 4/30.95 2/27.01 3/29.63                                        
         1/17.47 4/18.67 2/19.47 3/17.76                                        
         1/17.33 4/17.71 2/17.83 3/17.55                                        
         1/17.27 4/19.73 2/17.85 3/17.92                                        
         1/17.08 4/19.64 2/18.29 3/17.88                                        
         1/17.07 4/18.33 2/17.92 3/17.82                                        
         1/17.66 4/17.83 2/17.66 3/17.89                                        
         1/17.39 4/17.82 2/17.37 3/17.67                                        
         1/17.54 4/18.88 2/17.79 3/17.75                                        
         1/17.04 4/18.62 2/17.41 3/17.67                                        
         1/17.30 4/17.72 2/17.52 3/18.81                                        
         1/19.07 4/20.62 2/17.82 3/18.23                                        
         1/17.30 4/20.27 2/17.46 3/17.35                                        
         1/17.05 4/18.85 2/17.63 3/18.45                                        
         1/17.10 4/19.43 2/17.59 3/17.61                                        
         1/17.46 4/18.10 2/17.96 3/18.86                                        
         1/17.17 4/17.82 2/17.68 3/17.67                                        
         1/17.28 4/17.86 2/17.96 3/17.27                                        
         1/17.05 4/17.89 2/17.43 3/17.47                                        
         1/17.16 4/18.43 2/17.34 3/17.60                                        
         1/17.39 4/23.66 2/18.26 3/17.73                                        
         1/17.44 4/18.52 2/17.51 3/18.30                                        
         1/17.28 4/19.18 2/18.22 3/21.11                                        
         1/17.39 4/18.03 2/17.65 3/17.46                                        
         1/17.48 4/18.05 2/17.83 3/17.74                                        
         1/17.14         2/17.25 3/19.69                                        
         1/17.61         2/17.11                                                
         1/20.71                                                                
 ------- ------- ------- ------- ------- ------- ------- ------- ------- -------
      1/     28/     25/     27/     26/                                        
    35.9  8:18.5  8:02.6  8:08.9  8:00.9    
    '''

    def test_singlerace_upload(self):
        
        # Setup
        self.singlerace_db_objs = []

        uploaduser = User.objects.create_user('temporary', 'temporary@gmail.com', 'temporary')
        self.singlerace_db_objs.append(uploaduser)
        self.client.login(username='temporary', password='temporary')
        
        
        self.assertEqual(1 + 1, 2)
        
        # Need to fake the file upload.
        #     Make sure its is created in the right location
        #     Make sure there is a record of its upload in the logs.
        filename = "singlerace_testfile"
        with open(os.path.join(settings.MEDIA_USER_UPLOAD, filename), "wb") as f:
            f.write(self.singlerace_testfile)
                
        log_entry = models.UploadRecord(origfilename="NO_origional_filename",
                                        ip="1.1.1.1",
                                        user=uploaduser,
                                        filesize="56",
                                        filename=filename,
                                        uploaddate=time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()),
                                        processed=False)
        log_entry.save()
        self.singlerace_db_objs.append(log_entry)
                        
        # Need a supported track in the system.
        trackname_obj = TrackName(trackname="TACOMA R/C RACEWAY")
        trackname_obj.save()
        self.singlerace_db_objs.append(trackname_obj)
        
        sup_trackname_obj = SupportedTrackName(trackkey=trackname_obj)
        sup_trackname_obj.save()
        self.singlerace_db_objs.append(sup_trackname_obj)
        
        response = self.client.get("/upload_start/2/")
        self.assertEqual(response.status_code, 404)
        
        response = self.client.get("/upload_start/" + str(log_entry.id) + "/")
        self.assertEqual(response.status_code, 200)
        
        response = self.client.post('/upload_start/' + str(log_entry.id) + '/', {'track_id': sup_trackname_obj.id})
        #print "Content:", response.content
        self.assertEqual(response.status_code, 200)
        
        
        #----------------------------------------------------
        # Validate Racers
        #----------------------------------------------------
        # The race should now be uploaded, we want to validate it is in the system.
        car2 = RacerId.objects.get(racerpreferredname="RacerFirstCar2, Jon")
        car5 = RacerId.objects.get(racerpreferredname="RacerThirdCar5, Jon")
        car1 = RacerId.objects.get(racerpreferredname="RacerFifthCar1, Jon")
        
        #----------------------------------------------------
        # Validate Race Details
        #----------------------------------------------------
        # Validate the race details have been uploaded.
        raceobj = SingleRaceDetails.objects.get(trackkey=trackname_obj,
                                                 racedata="MODIFIED BUGGY A Main",
                                                 racenumber=2,
                                                 roundnumber=3,
                                                 racelength=8,
                                                 winninglapcount=28)
        
        #----------------------------------------------------
        # Validate Race Laps
        #----------------------------------------------------        
        # Validate the corner cases for the lap times and positions
        LapTimes.objects.get(raceid=raceobj,
                             racerid=car1,                             
                             racelap=0,
                             raceposition=5,
                             racelaptime='35.95')
        
        LapTimes.objects.get(raceid=raceobj,
                             racerid=car2,
                             racelap=0,
                             raceposition=1,
                             racelaptime='26.24')
        
        LapTimes.objects.get(raceid=raceobj,
                             racerid=car2,
                             racelap=27,
                             raceposition=1,
                             racelaptime='20.71')
        
        LapTimes.objects.get(raceid=raceobj,
                             racerid=car5,
                             racelap=0,
                             raceposition=3,
                             racelaptime='29.63')
        
        LapTimes.objects.get(raceid=raceobj,
                             racerid=car5,
                             racelap=25,
                             raceposition=3,
                             racelaptime='19.69')
        
        LapTimes.objects.get(raceid=raceobj,
                             racerid=car5,
                             racelap=26)
        
        
        #----------------------------------------------------
        # Validate Race Results
        #----------------------------------------------------
        #________________________Driver___Car#____Laps____RaceTime____Fast Lap___Behind_
        #RacerFirstCar2, Jon            #2         28         8:18.588         17.042                  
        #RacerSecondCar4, Jon            #4         27         8:08.928         17.116                  
        #RacerThirdCar5, Jon            #5         26         8:00.995         17.274                  
        #RacerFourthCar3, Jon            #3         25         8:02.680         17.714                  
        #RacerFifthCar1, Jon            #1          1           35.952         35.952 
        SingleRaceResults.objects.get(racerid=car1,
                                      raceid=raceobj,
                                      carnum=1,
                                      lapcount=1)
        
        SingleRaceResults.objects.get(racerid=car2,
                                      raceid=raceobj,
                                      carnum=2,
                                      lapcount=28)
        
        SingleRaceResults.objects.get(racerid=car5,
                                      raceid=raceobj,
                                      carnum=5,
                                      lapcount=26)
        
        # Quick end to end test, verify we now have a results page for the new race.
        #response = self.client.get("/displayresults/singleracedetailed/1/")
        #self.assertEqual(response.status_code, 200)
        
        # Teardown
        for obj in self.singlerace_db_objs:
            obj.delete()


class GeneralRaceUploader(TestCase):

    singlerace_testfile1 = '''Scoring Software by www.RCScoringPro.com                9:26:42 PM  7/17/2012

                   TACOMA R/C RACEWAY

MODIFIED BUGGY A Main                                         Round# 3, Race# 2

________________________Driver___Car#____Laps____RaceTime____Fast Lap___Behind_
Alpha, Jon            #2         28         8:18.588         17.042                  
Beta, Jon            #4         27         8:08.928         17.116                  
Charlie, Jon            #5         26         8:00.995         17.274                  
Delta, Jon            #3         25         8:02.680         17.714                  
Echo, Jon            #1          1           35.952         35.952                  

 ___1___ ___2___ ___3___ ___4___ ___5___ ___6___ ___7___ ___8___ ___9___ ___10__
 5/35.95 1/26.24 4/30.95 2/27.01 3/29.63                                        
         1/17.47 4/18.67 2/19.47 3/17.76                                        
         1/17.33 4/17.71 2/17.83 3/17.55                                        
         1/17.27 4/19.73 2/17.85 3/17.92                                        
         1/17.08 4/19.64 2/18.29 3/17.88                                        
         1/17.07 4/18.33 2/17.92 3/17.82                                        
         1/17.66 4/17.83 2/17.66 3/17.89                                        
         1/17.39 4/17.82 2/17.37 3/17.67                                        
         1/17.54 4/18.88 2/17.79 3/17.75                                        
         1/17.04 4/18.62 2/17.41 3/17.67                                        
         1/17.30 4/17.72 2/17.52 3/18.81                                        
         1/19.07 4/20.62 2/17.82 3/18.23                                        
         1/17.30 4/20.27 2/17.46 3/17.35                                        
         1/17.05 4/18.85 2/17.63 3/18.45                                        
         1/17.10 4/19.43 2/17.59 3/17.61                                        
         1/17.46 4/18.10 2/17.96 3/18.86                                        
         1/17.17 4/17.82 2/17.68 3/17.67                                        
         1/17.28 4/17.86 2/17.96 3/17.27                                        
         1/17.05 4/17.89 2/17.43 3/17.47                                        
         1/17.16 4/18.43 2/17.34 3/17.60                                        
         1/17.39 4/23.66 2/18.26 3/17.73                                        
         1/17.44 4/18.52 2/17.51 3/18.30                                        
         1/17.28 4/19.18 2/18.22 3/21.11                                        
         1/17.39 4/18.03 2/17.65 3/17.46                                        
         1/17.48 4/18.05 2/17.83 3/17.74                                        
         1/17.14         2/17.25 3/19.69                                        
         1/17.61         2/17.11                                                
         1/20.71                                                                
 ------- ------- ------- ------- ------- ------- ------- ------- ------- -------
      1/     28/     25/     27/     26/                                        
    35.9  8:18.5  8:02.6  8:08.9  8:00.9    
    '''
    
    singlerace_testfile2 = '''Scoring Software by www.RCScoringPro.com                9:21:34 PM  08/07/2012

                     TACOMA R/C RACEWAY

MODIFIED BUGGY A Main                                            Round# 3, Race# 1

________________________Driver___Car#____Laps____RaceTime____Fast Lap___Behind_
Beta, Jon            #3         19         6:07.101         18.455                  
Charlie, Jon            #1         19         6:14.602         18.466             7.501
Alpha, Jon            #5         18         6:05.124         18.480                  
Delta, Jon            #2         18         6:11.982         18.716             6.858
Echo, Jon            #4         17         6:02.475         18.941                  
Hotel, Jon            #6         17         6:03.349         19.537             0.874
Golf, Jon            #7         17         6:16.439         18.222            13.964

 ___1___ ___2___ ___3___ ___4___ ___5___ ___6___ ___7___ ___8___ ___9___ ___10__
 3/28.74 2/27.53 1/26.13 6/30.70 5/30.42 7/32.44 4/29.80                        
 2/19.57 3/21.31 1/19.29 6/21.40 4/18.91 7/20.33 5/20.96                        
 2/18.47 3/18.71 1/19.10 7/21.29 4/18.70 6/20.31 5/18.22                        
 2/19.54 3/19.13 1/18.69 7/20.05 4/19.36 6/19.76 5/21.53                        
 2/18.56 3/19.42 1/18.72 5/19.17 4/19.13 7/21.82 6/22.97                        
 2/18.85 4/19.59 1/18.82 5/18.97 3/18.87 7/20.40 6/18.49                        
 2/18.46 3/19.18 1/18.67 5/19.18 4/19.75 7/21.11 6/23.58                        
 2/18.74 4/21.79 1/19.12 5/20.44 3/18.48 7/22.42 6/20.81                        
 2/18.66 4/20.58 1/18.90 5/20.83 3/21.26 6/19.61 7/28.41                        
 2/20.27 4/18.76 1/19.66 5/19.30 3/18.61 6/19.87 7/21.39                        
 2/18.99 3/18.84 1/18.58 5/23.29 4/21.56 6/20.51 7/19.01                        
 2/18.66 4/21.48 1/18.45 5/19.00 3/19.81 6/19.53 7/19.41                        
 2/18.80 4/19.23 1/18.72 5/19.46 3/19.21 6/19.71 7/18.99                        
 2/19.54 4/19.16 1/19.38 5/18.99 3/18.89 6/20.04 7/23.71                        
 2/19.18 4/24.52 1/18.77 5/18.94 3/19.24 6/20.66 7/24.06                        
 2/19.03 4/20.51 1/18.99 6/31.83 3/18.74 5/23.91 7/19.68                        
 2/21.82 6/42.18 1/19.27 4/19.56 3/21.18 5/20.83 7/25.33                        
 2/19.48         1/18.89         3/22.91                                        
 2/19.17         1/18.86                                                        
 ------- ------- ------- ------- ------- ------- ------- ------- ------- -------
     19/     18/     19/     17/     18/     17/     17/                        
  6:14.6  6:11.9  6:07.1  6:02.4  6:05.1  6:03.3  6:16.4   
    '''
    
    racelist_to_upload = [{'filename':'upload1', 'filecontent':singlerace_testfile1},
                         {'filename':'upload2', 'filecontent':singlerace_testfile2},]
    
    def setUp(self):
        uploaduser = User.objects.create_user('temporary', 'temporary@gmail.com', 'temporary')
        self.client.login(username='temporary', password='temporary')

        # Need a supported track in the system.
        trackname_obj = TrackName(trackname="TACOMA R/C RACEWAY")
        trackname_obj.save()
        self.trackname_obj = trackname_obj
        
        sup_trackname_obj = SupportedTrackName(trackkey=trackname_obj)
        sup_trackname_obj.save()
        
                
        # Need to fake the file upload.
        #     Make sure its is created in the right location
        #     Make sure there is a record of its upload in the logs.
        for upload in self.racelist_to_upload:
        
            filename = upload['filename']
            with open(os.path.join(settings.MEDIA_USER_UPLOAD, filename), "wb") as f:
                f.write(upload['filecontent'])
                    
            log_entry = models.UploadRecord(origfilename="NO_origional_filename",
                                            ip="1.1.1.1",
                                            user=uploaduser,
                                            filesize="56",
                                            filename=filename,
                                            uploaddate=time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()),
                                            processed=False)
            log_entry.save()
            
            response = self.client.get("/upload_start/" + str(log_entry.id) + "/")
            self.assertEqual(response.status_code, 200)
            
            response = self.client.post('/upload_start/' + str(log_entry.id) + '/', {'track_id': sup_trackname_obj.id})
            self.assertEqual(response.status_code, 200)

        # The race has now been uploaded into the system.



    def test_multipledraces_upload(self):
        
        #----------------------------------------------------
        # Validate Racers
        #----------------------------------------------------
        # The race should now be uploaded, we want to validate it is in the system.
        car1 = RacerId.objects.get(racerpreferredname="Alpha, Jon")
        car2 = RacerId.objects.get(racerpreferredname="Hotel, Jon")
        
        #----------------------------------------------------
        # Validate Race Details
        #----------------------------------------------------
        # Validate the race details have been uploaded.
        raceobj1 = SingleRaceDetails.objects.get(trackkey=self.trackname_obj,
                                                 racedata="MODIFIED BUGGY A Main",
                                                 racenumber=2,
                                                 roundnumber=3,
                                                 racelength=8,
                                                 winninglapcount=28)
        
        raceobj2 = SingleRaceDetails.objects.get(trackkey=self.trackname_obj,
                                                 racedata="MODIFIED BUGGY A Main",
                                                 racenumber=1,
                                                 roundnumber=3,
                                                 racelength=6,
                                                 winninglapcount=19)
        
        #----------------------------------------------------
        # Validate Race Laps
        #----------------------------------------------------        
        # Validate the corner cases for the lap times and positions
        LapTimes.objects.get(raceid=raceobj1,
                             racerid=car1,
                             racelap=0,
                             raceposition=1,
                             racelaptime='26.24')
        LapTimes.objects.get(raceid=raceobj1,
                             racerid=car1,
                             racelap=27,
                             raceposition=1,
                             racelaptime='20.71')
        
        LapTimes.objects.get(raceid=raceobj2,
                             racerid=car2,
                             racelap=0,
                             raceposition=7,
                             racelaptime='32.44')        
        LapTimes.objects.get(raceid=raceobj2,
                             racerid=car2,
                             racelap=16,
                             raceposition=5,
                             racelaptime='20.83')
        
        #----------------------------------------------------
        # Validate Race Results
        #----------------------------------------------------
        SingleRaceResults.objects.get(racerid=car1,
                                      raceid=raceobj1,
                                      carnum=2,
                                      lapcount=28)
        
        SingleRaceResults.objects.get(racerid=car2,
                                      raceid=raceobj2,
                                      carnum=6,
                                      lapcount=17)
        
        
        