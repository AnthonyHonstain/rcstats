from django.test import TestCase
from django.test.client import Client

import rcstats.rcdata.models as models

import datetime
        

class SingleRace(TestCase):
    '''
    Simple race result manually pushed in the rcdata tables.
    
    Push a basic race into the DB for testing. This is a simple race for testing
    the basic functionality in the other views/apps that build off of this one.
    
    Race that this test case will setup into the system:
    
    Scoring Software by www.RCScoringPro.com                8:09:03 PM  01/14/2012
    
                                   Test_Track_0
    
    TestClassBuggy0                                         Round# 3, Race# 16
    
    ________________________Driver___Car#____Laps____RaceTime____Fast Lap___Behind_
    Racer0            #2         28         8:10.270         16.939                  
    Racer1            #1         27         8:11.756         16.900            10.468
    
     ___1___ ___2___ ___3___ ___4___ ___5___ ___6___ ___7___ ___8___ ___9___ ___10__
     10/24.5 1/20.58 
     8/18.04 1/17.09 
     8/17.53 1/16.93
     5/17.34 1/17.11
     4/17.13 1/17.25
     4/17.30 1/17.25
     4/17.21 1/16.99
     2/17.42 1/17.44
     2/17.14 1/17.33
     2/17.18 1/17.56
     2/17.47 1/17.31
     2/17.01 1/17.35
     2/17.21 1/18.07
     2/19.16 1/17.31
     2/17.03 1/18.23
     4/19.43 1/17.40
     4/17.24 1/17.32
     4/17.43 1/17.15
     4/17.31 1/17.31
     4/16.90 1/17.47
     4/17.33 1/17.31
     4/17.17 1/17.42
     4/24.36 1/18.37
     5/21.31 1/17.47
     5/17.24 1/17.34
     4/17.02 1/17.36
     5/20.17 1/17.27
             1/17.14
     ------- ------- ------- ------- ------- ------- ------- ------- ------- -------
         27/     28/
      8:11.7  8:10.2
    '''        
    def setUp(self):
        # Every test needs a client.
        self.client = Client()
        
        self.track = models.TrackName.objects.create(id=1, trackname="Test_Track_0")
        
        self.racer0 = models.RacerId.objects.create(id=1, racerpreferredname="Racer0")
        self.racer1 = models.RacerId.objects.create(id=2, racerpreferredname="Racer1")
        
        self.singlerace = models.SingleRaceDetails.objects.create(id=1, 
                                                                  trackkey=self.track,
                                                                  racedata="TestClassBuggy0 A main",
                                                                  racedate=datetime.datetime(year=2012,
                                                                                             month=1,
                                                                                             day=14, 
                                                                                             hour=20,
                                                                                             minute=9,
                                                                                             second=03,),
                                                                  uploaddate=datetime.datetime(year=2012,
                                                                                             month=1,
                                                                                             day=15, 
                                                                                             hour=20,
                                                                                             minute=9,
                                                                                             second=03, 
                                                                                             ),
                                                                  racelength='8',
                                                                  roundnumber=3,
                                                                  racenumber=16,
                                                                  winninglapcount='2',
                                                                  mainevent=1,)
           
        self.results = []
        result0 = models.SingleRaceResults.objects.create(id=1,
                                 raceid=self.singlerace,
                                 racerid=self.racer0,
                                 carnum=2,
                                 lapcount=28,
                                 racetime=datetime.time(second=20),
                                 fastlap="16.939",
                                 finalpos=1)
        
        result1 = models.SingleRaceResults.objects.create(id=2,
                                 raceid=self.singlerace,
                                 racerid=self.racer1,
                                 carnum=1,
                                 lapcount=27,
                                 racetime=datetime.time(second=20),
                                 fastlap="16.900",
                                 finalpos=2)
        self.results.append(result0)
        self.results.append(result1)
        
        lapid = 1
                
        self.racer0_laps = []
        expectedLaps_Racer0 = ["20.58", "17.09", "16.93", "17.11", "17.25", "17.25", "16.99", "17.44", "17.33", "17.56", "17.31", "17.35", "18.07", "17.31", "18.23", "17.40", "17.32", "17.15", "17.31", "17.47", "17.31", "17.42", "18.37", "17.47", "17.34", "17.36", "17.27", "17.14"]
        prepared_laps = map(lambda x: float(x) if x != "" else None, expectedLaps_Racer0)
        
        lapcount = 0
        for lap in prepared_laps:
            racer0_lap = models.LapTimes.objects.create(id=lapid,
                            raceid=self.singlerace, 
                            racerid=self.racer0,
                            racelap=lapcount,
                            raceposition=1,
                            racelaptime=float(lap))
            self.racer0_laps.append(racer0_lap)
            lapcount += 1
            lapid += 1

        self.racer1_laps = []
        expectedLaps_Racer1 = ["24.5", "18.04", "17.53", "17.34", "17.13", "17.30", "17.21", "17.42", "17.14", "17.18", "17.47", "17.01", "17.21", "19.16", "17.03", "19.43", "17.24", "17.43", "17.31", "16.90", "17.33", "17.17", "24.36", "21.31", "17.24", "17.02", "20.17", ""]
        # This step is required since the expectedLaps list isnt in the right format for the DB
        prepared_laps = map(lambda x: float(x) if x != "" else None, expectedLaps_Racer1)
        
        lapcount = 0
        for lap in prepared_laps:            
            racer1_lap = models.LapTimes.objects.create(id=lapid,
                            raceid=self.singlerace, 
                            racerid=self.racer1,
                            racelap=lapcount,
                            raceposition=2,
                            racelaptime=lap)
            self.racer1_laps.append(racer1_lap)
            lapcount += 1
            lapid += 1
                                                                  
    
    def tearDown(self):
        
        for lap in self.racer0_laps:
            lap.delete()
        
        for lap in self.racer1_laps:
            lap.delete()
        
        for result in self.results:
            result.delete()
        
        self.singlerace.delete()
                
        self.racer0.delete()
        self.racer1.delete()
        
        self.track.delete()
        
    
    
    def test_basic_racedata(self):
        """
        Sanity Check - Validate the basic track information is loaded.
        """
        self.assertEqual(models.TrackName.objects.get(pk=1).trackname, "Test_Track_0")
        
        
        
        