'''
Created on Aug 19, 2012

@author: Anthony Honstain
'''
from rcstats.rcdata.models import SingleRaceDetails
from rcstats.rcdata.models import RacerId

from rcstats.ranking.models import RankedClass
from rcstats.ranking.models import Ranking

from rcstats.ranking.views import process_ranking 
import rcstats.uploadresults.tests.general_race_uploader as uploadresultstests


class RankSingleRace(uploadresultstests.GeneralRaceUploader):
    
    singlerace_testfile1 = '''Scoring Software by www.RCScoringPro.com                7:27:45 PM  7/9/2011

                             RankingTestTrack

RankingTestClass A Main                                                        Round# 1, Race# 1

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
    
    racelist_to_upload = [{'filename':'upload1', 'filecontent':singlerace_testfile1},]
    
    
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

        # Validate that the three racers are now ranked.        
        racer1 = Ranking.objects.get(raceridkey = RacerId.objects.filter(racerpreferredname='RankedRacer One')[0].id)
        racer2 = Ranking.objects.get(raceridkey = RacerId.objects.filter(racerpreferredname='RankedRacer Two')[0].id)
        racer3 = Ranking.objects.get(raceridkey = RacerId.objects.filter(racerpreferredname='RankedRacer Three')[0].id)
        
        self.assertAlmostEqual(racer1.displayrank, 11.6069655461, places=4)
        self.assertAlmostEqual(racer2.displayrank, 6.22000799505, places=4)
        self.assertAlmostEqual(racer3.displayrank, -1.89718140627, places=4)
        