from django.test import TestCase
from django.test.client import Client

import views
import rcstats.rcdata.models
import rcstats.rcdata.tests as basetests
import rcstats.urls

class SimpleTest(basetests.SingleRace):
    urls = 'rcstats.urls'
    
    def test_racers_for_myresults(self):
        """
        A very basic starter test to validate that the test racers were uploaded
        and we can proceed with more advanced tests.
        """
        self.assertIn((u'Racer0', 1), views._get_racer_for_main_table())

    def test_primary_myresults_view(self):
        response = self.client.get("/myresults/")
        self.assertEqual(response.status_code, 200)


    def test_generalstats_view(self):
        response = self.client.get("/myresults/1/")
        self.assertEqual(response.status_code, 200)
        
        
    def test_get_RaceTimeline_JSData(self):
        '''
        Test the helper function used to create a flot graph
        of all the races the user has been in.
        '''
        racerobj = rcstats.rcdata.models.RacerId.objects.get(pk=1)
        expected_js_response = '[{"data": [[1326629343000.0, 1]], "label": "Racer0"}]'
        self.assertEqual(expected_js_response, views._get_RaceTimeline_JSData(racerobj))
        
    
    def test_get_Group_Race_Classes(self):
        racerobj = rcstats.rcdata.models.RacerId.objects.get(pk=1)
        expected_js_response = ({u'TestClassBuggy0': 1}, """[{"data": 1, "label": "TestClassBuggy0: 1"}]""")    
        self.assertEqual(expected_js_response, views._get_Group_Race_Classes(racerobj))
        
        
    def test_get_Cleaned_Class_Names(self):
        dirtynames = [{'dcount': 86, 'racedata': u'STOCK BUGGY A Main'},
                      {'dcount': 56, 'racedata': u'STOCK TRUCK A Main'}]
        
        self.assertDictEqual({"STOCK BUGGY":86, 
                              "STOCK TRUCK":56}, 
                             views._get_Cleaned_Class_Names(dirtynames))
        
        
        