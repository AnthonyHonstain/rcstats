'''
Created on July 2012
Modified on April 2013 - moved to a seperate file for better organization.

@author: Anthony Honstain
'''

from rcstats.rcdata.models import LapTimes
from rcstats.rcdata.models import SingleRaceDetails
from rcstats.rcdata.models import SingleRaceResults

from rcstats.rcdata.models import RacerId
    
from rcstats.uploadresults.tests.general_race_uploader import GeneralRaceUploader


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
    

    def test_multipleraces_upload(self):
        #====================================================
        # Validate Race Details
        #====================================================
        # Validate the race details have been uploaded.
        #
        # WARNING - if this fails it means one of the uploads probably failed.
        #
        raceobj1 = SingleRaceDetails.objects.get(trackkey=self.trackname_obj,
                                                 racedata="SC Pro 4",
                                                 racenumber=7,
                                                 roundnumber=3,
                                                 racelength=6,
                                                 winninglapcount=18,
                                                 mainevent=1)
        
        #====================================================
        # Validate Racers
        #====================================================
        # The race should now be uploaded, we want to validate it is in the system.
        car10 = RacerId.objects.get(racerpreferredname="Brown, Shaun")
        car11 = RacerId.objects.get(racerpreferredname="Andres, Jonathan")
                
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