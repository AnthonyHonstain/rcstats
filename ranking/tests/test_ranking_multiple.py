'''
Created on Aug 19, 2012

@author: Anthony Honstain

Basic test to see that C,B,A mains are collapsed into a single stack for ranking.

NOT going to rank as three separate races.

This also depends on chronological order, if your pc time clock is
bouncing all over the place, we are not going to help you.
'''
from rcstats.rcdata.models import LapTimes
from rcstats.rcdata.models import SingleRaceDetails
from rcstats.rcdata.models import SingleRaceResults
from rcstats.rcdata.models import SupportedTrackName
from rcstats.rcdata.models import TrackName
from rcstats.rcdata.models import RacerId

from rcstats.ranking.models import RankedClass
from rcstats.ranking.models import RankEvent
from rcstats.ranking.models import RankEventDetails
from rcstats.ranking.models import Ranking

from rcstats.ranking.views import process_ranking 
import rcstats.uploadresults.tests as uploadresultstests


class RankMultipleRace(uploadresultstests.GeneralRaceUploader):
    
    singlerace_testfile1 = '''Scoring Software by www.RCScoringPro.com                7:27:45 PM  7/9/2011

                             RankingTestTrack

RankingTestClass C Main                                                        Round# 1, Race# 1

________________________Driver___Car#____Laps____RaceTime____Fast Lap___Behind_
              RankedRacer Four    #2      12     6:22.032     30.964           
               RankedRacer Six    #1      10     6:17.466     34.078           
             RankedRacer Seven    #3       5     2:43.317     31.628           

 ___1___ ___2___ ___3___ ___4___ ___5___ ___6___ ___7___ ___8___ ___9___ ___10__
 1/15.27 2/16.03 3/16.80                                                        
 2/38.46 1/33.71 3/38.81                                                        
 3/38.15 2/38.22 1/31.62                                                        
 3/44.80 1/30.96 2/44.17                                                        
 3/39.02 1/31.12 2/31.89                                                        
 2/43.29 1/31.67                                                                
 2/49.39 1/32.09                                                                
 2/37.37 1/32.39                                                                
 2/34.07 1/35.47                                                                
 2/37.60 1/33.41                                                                
         1/32.41                                                                
         1/34.50                                                                
 ------- ------- ------- ------- ------- ------- ------- ------- ------- -------
     10/     12/      5/                                                        
  6:17.4  6:22.0  2:43.3 
'''

    singlerace_testfile2 = '''Scoring Software by www.RCScoringPro.com                7:37:45 PM  7/9/2011

                             RankingTestTrack

RankingTestClass B Main                                                        Round# 1, Race# 2

________________________Driver___Car#____Laps____RaceTime____Fast Lap___Behind_
             RankedRacer Three    #2      12     6:22.032     30.964           
              RankedRacer Four    #1      10     6:17.466     34.078           
              RankedRacer Five    #3       5     2:43.317     31.628           

 ___1___ ___2___ ___3___ ___4___ ___5___ ___6___ ___7___ ___8___ ___9___ ___10__
 1/15.27 2/16.03 3/16.80                                                        
 2/38.46 1/33.71 3/38.81                                                        
 3/38.15 2/38.22 1/31.62                                                        
 3/44.80 1/30.96 2/44.17                                                        
 3/39.02 1/31.12 2/31.89                                                        
 2/43.29 1/31.67                                                                
 2/49.39 1/32.09                                                                
 2/37.37 1/32.39                                                                
 2/34.07 1/35.47                                                                
 2/37.60 1/33.41                                                                
         1/32.41                                                                
         1/34.50                                                                
 ------- ------- ------- ------- ------- ------- ------- ------- ------- -------
     10/     12/      5/                                                        
  6:17.4  6:22.0  2:43.3 
'''

    singlerace_testfile3 = '''Scoring Software by www.RCScoringPro.com                7:47:45 PM  7/9/2011

                             RankingTestTrack

RankingTestClass A Main                                                        Round# 1, Race# 3

________________________Driver___Car#____Laps____RaceTime____Fast Lap___Behind_
                  RankedRacer One    #2      12     6:22.032     30.964           
                  RankedRacer Two    #1      10     6:17.466     34.078           
                RankedRacer Three    #3       5     2:43.317     31.628           

 ___1___ ___2___ ___3___ ___4___ ___5___ ___6___ ___7___ ___8___ ___9___ ___10__
 1/15.27 2/16.03 3/16.80                                                        
 2/38.46 1/33.71 3/38.81                                                        
 3/38.15 2/38.22 1/31.62                                                        
 3/44.80 1/30.96 2/44.17                                                        
 3/39.02 1/31.12 2/31.89                                                        
 2/43.29 1/31.67                                                                
 2/49.39 1/32.09                                                                
 2/37.37 1/32.39                                                                
 2/34.07 1/35.47                                                                
 2/37.60 1/33.41                                                                
         1/32.41                                                                
         1/34.50                                                                
 ------- ------- ------- ------- ------- ------- ------- ------- ------- -------
     10/     12/      5/                                                        
  6:17.4  6:22.0  2:43.3 
'''
    
    racelist_to_upload = [{'filename':'upload1', 'filecontent':singlerace_testfile1},
                          {'filename':'upload2', 'filecontent':singlerace_testfile2},
                          {'filename':'upload3', 'filecontent':singlerace_testfile3},]
    
    
    
    
    def test_multipleraces_upload(self):
        #=====================================================
        # Validate Race Details
        #=====================================================
        # Validate the race details have been uploaded.
        raceobj1 = SingleRaceDetails.objects.get(trackkey=self.trackname_obj,
                                                 racedata="RankingTestClass",
                                                 racenumber=1,
                                                 roundnumber=1,
                                                 racelength=6,
                                                 winninglapcount=12,
                                                 mainevent=3)
        raceobj3 = SingleRaceDetails.objects.get(trackkey=self.trackname_obj,
                                                 racedata="RankingTestClass",
                                                 racenumber=3,
                                                 roundnumber=1,
                                                 racelength=6,
                                                 winninglapcount=12,
                                                 mainevent=1)
        
        #=====================================================
        # Validate Ranking
        #=====================================================
        
        # Create a RankedClass
        rnk_class = RankedClass(trackkey = self.trackname_obj,
                                raceclass = "RankingTestClass",
                                startdate = '2010-01-01 01:01:01',
                                lastdate = '2010-01-01 01:01:01',
                                experation = 10,
                                requiredraces = 1) 
        rnk_class.save()
        
        # Run ranking for that class
        process_ranking(rnk_class)
        
        # We want their to be only one ranking for each of these racers (there events should
        # have been collapsed into a single race).
        racer1 = Ranking.objects.get(raceridkey = RacerId.objects.get(racerpreferredname='RankedRacer One').id)
        racer2 = Ranking.objects.get(raceridkey = RacerId.objects.get(racerpreferredname='RankedRacer Two').id)
        racer3 = Ranking.objects.get(raceridkey = RacerId.objects.get(racerpreferredname='RankedRacer Three').id)
        racer4 = Ranking.objects.get(raceridkey = RacerId.objects.get(racerpreferredname='RankedRacer Four').id)
        racer5 = Ranking.objects.get(raceridkey = RacerId.objects.get(racerpreferredname='RankedRacer Five').id)
        racer6 = Ranking.objects.get(raceridkey = RacerId.objects.get(racerpreferredname='RankedRacer Six').id)
        racer7 = Ranking.objects.get(raceridkey = RacerId.objects.get(racerpreferredname='RankedRacer Seven').id)
        
        self.assertAlmostEqual(racer1.displayrank, 17.1445048619, places=4)
        self.assertAlmostEqual(racer7.displayrank, -3.91463635265, places=4)
        