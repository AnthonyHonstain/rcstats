'''
Created on Aug 19, 2012

@author: Anthony Honstain
'''
from django.test import TestCase
from django.test.client import Client

from rcstats.rcdata.models import LapTimes
from rcstats.rcdata.models import SingleRaceDetails
from rcstats.rcdata.models import SingleRaceResults
from rcstats.rcdata.models import SupportedTrackName
from rcstats.rcdata.models import TrackName
from rcstats.rcdata.models import RacerId

import rcstats.uploadresults.tests as uploadresultstests

from rcstats.rcdata.database_cleanup import _ProcessRacerId, collapse_racer_names

class TestProcessRacerIdSimple(TestCase):

    def setUp(self):        
        db_results = [[1, 'honstain, anthony', 5], [2, 'anthony houstain', 1], [3, 'Brandon Collins', 2]]
        self.processracerid = _ProcessRacerId(db_results)
        
    def test_misspell_count(self):
        
        self.assertEqual(self.processracerid._misspell_count("abc", "adc"), 2)
        self.assertEqual(self.processracerid._misspell_count("ab", "abcd"), 2)
        self.assertEqual(self.processracerid._misspell_count("ab  ", "  ab"), 0)
        
    def test_check_edit_distance(self):
        
        self.assertEqual(self.processracerid._check_edit_distance("anthony houstain"), "anthony honstain")
        
        # Not checking a distance of 2 yet.
        self.assertEqual(self.processracerid._check_edit_distance("brandon collonz"), "")
        
        
class TestProcessRacerId_E2E_simple(TestCase):

    def setUp(self):        
        db_results = [[1, 'honstain, anthony', 100], 
                      [2, 'john doe', 50],
                      [3, 'anthony houstain', 25],
                      [4, 'ANTHONY HONSTAIN', 20], 
                      [5, 'Brandon Collins', 10],
                      [6, 'Collins, Brandon', 5]]
        self.processracerid = _ProcessRacerId(db_results)
        
    def test_primaryName_dict(self):
        
        self.assertDictEqual(self.processracerid._primaryName_dict, {'anthony honstain':[[1, 'honstain, anthony', 100],
                                                                                         [3, 'anthony houstain', 25],
                                                                                         [4, 'ANTHONY HONSTAIN', 20]],
                                                                     'john doe':[[2, 'john doe', 50],],
                                                                     'brandon collins':[[5, 'Brandon Collins', 10],
                                                                                        [6, 'Collins, Brandon', 5]]})

class TestProcessRacerId_E2E_detailed(TestCase):

    def setUp(self):        
        db_results = [[1, 'honstain, anthony', 100], 
                      [2, 'Charlie, Jon', 2],
                      [3, 'anthony houstain', 25],
                      [4, 'ANTHONY HONSTAIN', 20],
                      [5, 'Charlee, Jon', 1]]
        self.processracerid = _ProcessRacerId(db_results)
        
    def test_primaryName_dict(self):
        
        self.assertDictEqual(self.processracerid._primaryName_dict, {'anthony honstain':[[1, 'honstain, anthony', 100],
                                                                                         [3, 'anthony houstain', 25],
                                                                                         [4, 'ANTHONY HONSTAIN', 20]],
                                                                     'jon charlie':[[2, 'Charlie, Jon', 2], 
                                                                                    [5, 'Charlee, Jon', 1]],})



class CollapseRacerNames(uploadresultstests.GeneralRaceUploader):
    
    singlerace_testfile1 = '''Scoring Software by www.RCScoringPro.com                9:26:42 PM  7/17/2012

                   TACOMA R/C RACEWAY

MODIFIED BUGGY A Main                                         Round# 3, Race# 2

________________________Driver___Car#____Laps____RaceTime____Fast Lap___Behind_
Anthony Honstain            #2         28         8:18.588         17.042                  
lowercase jim            #4         27         8:08.928         17.116                  
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
lowercase jim            #3         19         6:07.101         18.455                  
Charlie, Jon            #1         19         6:14.602         18.466             7.501
Anthony Honstain            #5         18         6:05.124         18.480                  
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
    
    singlerace_testfile3 = '''Scoring Software by www.RCScoringPro.com                9:30:47 PM  08/08/2012

                     TACOMA R/C RACEWAY

MODIFIED BUGGY A Main                                         Round# 3, Race# 2

________________________Driver___Car#____Laps____RaceTime____Fast Lap___Behind_
Honstain, Anthony            #6         21         6:16.975         16.834                  
LOWERCASE JIM            #1         21         6:20.362         17.051             3.387
Charlee, Jon            #5         20         6:04.767         16.597                  
Delta, Jon            #2         12         6:14.426         17.986                  
Echo, Jon            #3          3         1:05.720         17.099                  

 ___1___ ___2___ ___3___ ___4___ ___5___ ___6___ ___7___ ___8___ ___9___ ___10__
 2/25.08 3/26.31 4/26.90         5/27.86 1/23.78                                
 2/17.39 3/18.59 5/21.71         4/17.93 1/16.83                                
 2/17.67 4/18.77 5/17.09         3/17.63 1/18.67                                
 2/17.92 4/21.24                 3/16.80 1/17.89                                
 2/17.39 4/18.23                 3/17.02 1/17.27                                
 1/17.72 4/19.22                 2/16.89 3/20.55                                
 1/17.65 4/21.71                 2/17.18 3/17.05                                
 1/17.35 4/17.98                 2/17.18 3/17.33                                
 1/17.54 4/153.6                 3/19.80 2/18.14                                
 1/17.51 4/20.63                 2/17.53 3/18.49                                
 1/17.53 4/18.62                 2/17.31 3/17.55                                
 1/17.87 4/19.36                 3/21.14 2/17.25                                
 1/17.37                         3/17.25 2/17.17                                
 1/17.45                         3/16.59 2/17.25                                
 1/17.25                         3/16.97 2/17.95                                
 1/17.24                         3/17.68 2/16.91                                
 1/17.05                         3/17.30 2/17.74                                
 1/19.48                         3/17.59 2/17.02                                
 1/17.40                         3/20.20 2/17.71                                
 1/17.41                         3/16.83 2/16.88                                
 2/20.98                                 1/17.44                                
 ------- ------- ------- ------- ------- ------- ------- ------- ------- -------
     21/     12/      3/             20/     21/                                
  6:20.3  6:14.4  1:05.7          6:04.7  6:16.9                                

    '''
    
    racelist_to_upload = [{'filename':'upload1', 'filecontent':singlerace_testfile1},
                          {'filename':'upload2', 'filecontent':singlerace_testfile2},
                          {'filename':'upload3', 'filecontent':singlerace_testfile3},]
    
    
    def test_multipleraces_upload(self):
        
        # Basic checks befor we collapse the names.
        
        #=====================================================
        # Validate Racers
        #=====================================================
        # The race should now be uploaded, we want to validate it is in the system.
        car1 = RacerId.objects.get(racerpreferredname="Anthony Honstain")
        car2 = RacerId.objects.get(racerpreferredname="Hotel, Jon")
        
        #=====================================================
        # Validate Race Details
        #=====================================================
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
        
        raceobj3 = SingleRaceDetails.objects.get(trackkey=self.trackname_obj,
                                                 racedata="MODIFIED BUGGY A Main",
                                                 racenumber=2,
                                                 roundnumber=3,
                                                 racelength=6,
                                                 winninglapcount=21)
        
        #=====================================================
        # Validate Race Laps
        #=====================================================        
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
        
        #=====================================================
        # Validate Race Results
        #=====================================================
        SingleRaceResults.objects.get(racerid=car1,
                                      raceid=raceobj1,
                                      carnum=2,
                                      lapcount=28)
        
        SingleRaceResults.objects.get(racerid=car2,
                                      raceid=raceobj2,
                                      carnum=6,
                                      lapcount=17)
                
        #=====================================================
        # Collapse the names
        #     Not necessary, it happens at upload time
        #=====================================================
        #collapse_racer_names()
        
        #=====================================================
        # Validate that "Honstain, Anthony" was collapsed to "Anthony Honstain"
        #=====================================================
        SingleRaceResults.objects.get(racerid=car1,
                                      raceid=raceobj3,
                                      carnum=6,
                                      lapcount=21)
        
        LapTimes.objects.get(raceid=raceobj3,
                             racerid=car1,
                             racelap=0,
                             raceposition=1,
                             racelaptime='23.78')
        
        removed_racerid_queryset = RacerId.objects.filter(racerpreferredname__contains="Honstain, Anthony")
        self.assertEqual(len(removed_racerid_queryset), 0)
        
        #=====================================================
        # Validate that "Charlee, John" was collapsed to "Charlie, Jon"
        #=====================================================
        # Helpful information to look at when investigating.
        #for racerid in RacerId.objects.all():
        #    print racerid
            
        car3 = RacerId.objects.get(racerpreferredname="Charlie, Jon")
                
        SingleRaceResults.objects.get(racerid=car3,
                                      raceid=raceobj3,
                                      carnum=5,
                                      lapcount=20)
        
        #=====================================================
        # Validate that "LOWERCASE JIM" was collapsed to "lowercase jim"
        #=====================================================
        car4 = RacerId.objects.get(racerpreferredname="lowercase jim")
                
        SingleRaceResults.objects.get(racerid=car4,
                                      raceid=raceobj3,
                                      carnum=1,
                                      lapcount=21)
        
        