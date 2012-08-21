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
        
        #====================================================
        # Validate Racers
        #====================================================
        # The race should now be uploaded, we want to validate it is in the system.
        car2 = RacerId.objects.get(racerpreferredname="RacerFirstCar2, Jon")
        car5 = RacerId.objects.get(racerpreferredname="RacerThirdCar5, Jon")
        car1 = RacerId.objects.get(racerpreferredname="RacerFifthCar1, Jon")
        
        #====================================================
        # Validate Race Details
        #====================================================
        # Validate the race details have been uploaded.
        raceobj = SingleRaceDetails.objects.get(trackkey=trackname_obj,
                                                 racedata="MODIFIED BUGGY A Main",
                                                 racenumber=2,
                                                 roundnumber=3,
                                                 racelength=8,
                                                 winninglapcount=28)
        
        #====================================================
        # Validate Race Laps
        #====================================================        
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
        
        
        #====================================================
        # Validate Race Results
        #====================================================
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
        
        #====================================================
        # Validate Racers
        #====================================================
        # The race should now be uploaded, we want to validate it is in the system.
        car1 = RacerId.objects.get(racerpreferredname="Alpha, Jon")
        car2 = RacerId.objects.get(racerpreferredname="Hotel, Jon")
        
        #====================================================
        # Validate Race Details
        #====================================================
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
        
        #====================================================
        # Validate Race Laps
        #====================================================        
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
        
        #====================================================
        # Validate Race Results
        #====================================================
        SingleRaceResults.objects.get(racerid=car1,
                                      raceid=raceobj1,
                                      carnum=2,
                                      lapcount=28)
        
        SingleRaceResults.objects.get(racerid=car2,
                                      raceid=raceobj2,
                                      carnum=6,
                                      lapcount=17)
        
        

class PaceInfoInLapTimesTest(GeneralRaceUploader):

    singlerace_testfile1 = '''Scoring Software by www.RCScoringPro.com                3:09:41 PM  08/18/2012

                                TACOMA R/C RACEWAY

SC Pro 4 A Main                                               Round# 3, Race# 7

________________________Driver___Car#____Laps____RaceTime____Fast Lap___Behind_
Whetsell, Keith            #5         18         6:05.034         20.690                  
Anton, Mark            #2         18         6:10.838         20.612             5.804
Seim, Roger            #1         17         6:01.006         21.200                  
Sturgell, Dennis            #4         17         6:17.843         20.609            16.837
Botti, Matt            #6         16         6:09.601         21.711                  
Meyer, Jim            #7         16         6:09.805         22.492             0.204
Brown, Shaun            #10        16         6:10.315         22.140             0.714
Andres, Jonathan            #11        16         6:18.721         22.472             9.120
Aldous, Steve            #9         16         6:19.856         22.813            10.255
Casey, Joe            #8         15         6:01.177         22.037                  
Huddleston, Chris            #3          3           51.832         23.550                  

 ___1___ ___2___ ___3___ ___4___ ___5___ ___6___ ___7___ ___8___ ___9___ ___10__
 3/3.587 1/2.487 5/4.240 4/3.792 2/2.899 9/6.557 6/4.734 11/6.85 8/6.290 7/6.126
101/02.5145/01.0 85/00.4 95/00.0125/02.5 55/00.7 77/04.2 53/03.5 58/04.8 59/01.6

 3/21.98 1/21.70 5/24.04 4/22.16 2/21.89 10/30.3 6/23.76 11/31.3 7/24.11 9/28.92
 29/10.7 30/02.8 26/07.6 28/03.4 30/11.8 20/08.6 26/10.5 19/03.1 24/04.9 21/08.0

 2/21.77 3/23.56 5/23.55 4/24.55 1/20.85 9/23.65 6/24.72 10/22.7 7/23.29 11/26.9
 23/03.0 23/06.0 21/02.8 22/10.4 24/05.1 18/03.0 21/12.6 18/06.0 21/15.9 18/11.8

 2/21.61 3/21.35         4/21.67 1/20.79 10/27.1 7/28.14 9/25.03 5/25.76 8/23.82
 21/02.0 21/02.8         20/00.9 22/05.3 17/12.6 18/06.1 17/05.6 19/17.4 17/04.6

 2/22.67 3/22.93         4/24.59 1/20.75 10/21.9 6/23.85 9/22.63 5/22.81 8/22.71
 20/06.5 20/08.1         19/07.7 21/06.1 17/12.7 18/18.8 17/09.4 18/08.2 17/08.9

 2/21.21 3/21.98         4/23.23 1/20.95 6/22.07 7/27.35 8/25.24 5/22.81 10/28.9
 20/16.1 19/01.0         18/00.0 20/00.4 17/13.1 17/15.6 17/19.4 18/15.2 16/06.5

 3/23.74 2/21.25         4/21.12 1/20.71 6/22.91 7/22.70 8/22.03 5/25.44 9/22.36
 19/10.7 19/07.2         18/02.9 20/08.1 17/15.5 17/17.1 17/18.7 17/05.5 16/05.2

 2/22.48 1/21.18         3/21.72 4/41.92 5/22.65 6/23.90 7/24.53 8/31.10 9/22.64
 19/17.8 19/11.6         18/06.4 17/02.8 17/16.7 17/20.7 16/00.9 16/03.3 16/04.8

 2/21.20 1/22.06         3/20.60 4/21.27 5/21.71 6/23.73 8/25.53 9/24.70 7/22.26
 18/00.5 19/16.9         18/06.9 17/02.7 17/15.8 16/00.7 16/06.2 16/06.8 16/03.9

 2/22.23 1/20.95         3/21.85 4/20.77 5/23.92 6/22.51 8/23.24 10/27.1 7/22.74
 18/04.5 19/19.0         18/09.6 17/01.7 17/18.9 16/00.7 16/06.8 16/13.6 16/03.9

 3/25.40 1/23.89         2/22.30 4/22.14 6/26.65 5/22.49 9/27.91 10/25.8 7/27.38
 18/12.9 18/05.5         18/12.5 17/03.1 16/03.0 16/00.6 16/14.0 16/17.1 16/10.6

 2/22.55 1/21.14         3/27.18 4/22.96 6/23.70 5/22.58 9/24.27 10/23.2 7/22.57
 18/15.7 18/06.8         17/01.0 17/05.4 16/04.3 16/00.6 16/15.2 16/16.7 16/09.8

 2/21.24 1/20.86         4/28.33 3/20.69 6/22.84 5/22.56 9/24.75 10/27.3 7/23.31
 18/16.2 18/07.4         17/10.2 17/04.3 16/04.4 16/00.7 16/16.8 16/21.4 16/10.1

 2/21.81 1/20.97         4/21.27 3/21.02 5/23.04 6/29.20 8/23.72 10/23.1 7/24.46
 18/17.4 18/08.2         17/09.6 17/03.8 16/04.7 16/08.3 16/17.0 16/20.6 16/11.6

 2/22.08 1/21.21         4/26.96 3/23.39 5/26.64 6/24.07 10/31.2 9/22.88 7/22.14
 18/18.7 18/09.1         17/15.5 17/06.1 16/08.8 16/09.4 15/01.1 16/19.6 16/10.4

 2/21.40 1/21.70         4/22.41 3/21.02 5/23.78 6/23.43         9/23.91 7/22.99
 18/19.1 18/10.4         17/15.9 17/05.5 16/09.6 16/09.8         16/19.8 16/10.3

 2/23.97 1/20.92         4/24.03 3/20.97                                        
 17/01.0 18/10.8         17/17.8 17/05.0                                        

         1/20.61                                                                
         18/10.8                                                                
 ------- ------- ------- ------- ------- ------- ------- ------- ------- -------
     17/     18/      3/     17/     18/     16/     16/     15/     16/     16/
  6:01.0  6:10.8    51.8  6:17.8  6:05.0  6:09.6  6:09.8  6:01.1  6:19.8  6:10.3


 ___11__ ___12__ ___13__ ___14__ ___15__ ___16__ ___17__ ___18__ ___19__ ___20__
 10/6.60                                                                        
 55/03.0                                                                        

 8/26.83                                                                        
 22/07.8                                                                        

 8/22.47                                                                        
 20/12.7                                                                        

 6/24.16                                                                        
 18/00.3                                                                        

 7/25.98                                                                        
 17/00.6                                                                        

 9/31.26                                                                        
 16/06.1                                                                        

 10/25.3                                                                        
 16/11.8                                                                        

 10/23.4                                                                        
 16/12.1                                                                        

 10/22.5                                                                        
 16/10.9                                                                        

 9/23.96                                                                        
 16/12.2                                                                        

 8/23.87                                                                        
 16/13.0                                                                        

 8/23.97                                                                        
 16/13.9                                                                        

 8/25.07                                                                        
 16/16.0                                                                        

 9/25.07                                                                        
 16/17.8                                                                        

 8/24.50                                                                        
 16/18.8                                                                        

 8/23.59                                                                        
 16/18.7                                                                        

                                                                                
                                                                                

                                                                                
                                                                                
 ------- ------- ------- ------- ------- ------- ------- ------- ------- -------
     16/                                                                        
  6:18.7                                                                        
 '''
    
    racelist_to_upload = [{'filename':'upload1', 'filecontent':singlerace_testfile1},]
    

    def test_multipledraces_upload(self):
        
        #====================================================
        # Validate Racers
        #====================================================
        # The race should now be uploaded, we want to validate it is in the system.
        car10 = RacerId.objects.get(racerpreferredname="Brown, Shaun")
        car11 = RacerId.objects.get(racerpreferredname="Andres, Jonathan")
        
        #====================================================
        # Validate Race Details
        #====================================================
        # Validate the race details have been uploaded.
        raceobj1 = SingleRaceDetails.objects.get(trackkey=self.trackname_obj,
                                                 racedata="SC Pro 4 A Main",
                                                 racenumber=7,
                                                 roundnumber=3,
                                                 racelength=6,
                                                 winninglapcount=18)
        
        #====================================================
        # Validate Race Laps
        #====================================================        
        # Validate the corner cases for the lap times and positions
        LapTimes.objects.get(raceid=raceobj1,
                             racerid=car10,
                             racelap=0,
                             raceposition=7,
                             racelaptime='6.126')
        LapTimes.objects.get(raceid=raceobj1,
                             racerid=car10,
                             racelap=15,
                             raceposition=7,
                             racelaptime='22.99')
        
        LapTimes.objects.get(raceid=raceobj1,
                             racerid=car11,
                             racelap=0,
                             raceposition=10,
                             racelaptime='6.60')        
        LapTimes.objects.get(raceid=raceobj1,
                             racerid=car11,
                             racelap=15,
                             raceposition=8,
                             racelaptime='23.59')
        
        #====================================================
        # Validate Race Results
        #====================================================
        SingleRaceResults.objects.get(racerid=car10,
                                      raceid=raceobj1,
                                      carnum=10,
                                      lapcount=16)
        
        SingleRaceResults.objects.get(racerid=car11,
                                      raceid=raceobj1,
                                      carnum=11,
                                      lapcount=16)