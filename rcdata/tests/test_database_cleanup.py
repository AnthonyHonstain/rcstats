'''
Created on Aug 24, 2012

@author: Anthony Honstain
'''
from django.test import TestCase
from django.test.client import Client

import rcstats.rcdata.database_cleanup as database_cleanup
import rcstats.rcdata.models as models

import datetime


class CollapseClassNamesTestCases(TestCase):
    
    def test_collapse_classnames_simple(self):
        trackname_obj = models.TrackName.objects.create(id=1, trackname="TACOMA R/C RACEWAY")
        
        officialclass = models.OfficialClassNames(raceclass="Mod Buggy")
        officialclass.save()
        
        alias = models.AliasClassNames(raceclass="modified buggy", officialclass=officialclass)
        alias.save()
        
        classnames = [['mod buggy', None, 'Mod Buggy'],
                      ['modified buggy', None, 'Mod Buggy'],]
        
        self._create_and_validate_classnames(trackname_obj, classnames)
    
    
    def test_collapse_classnames_multipleclasses(self):
        trackname_obj = models.TrackName.objects.create(id=1, trackname="TACOMA R/C RACEWAY")
        
        officialclass = models.OfficialClassNames(raceclass="Mod Buggy")
        officialclass.save()
        
        alias = models.AliasClassNames(raceclass="modified buggy", officialclass=officialclass)
        alias.save()
        
        officialclass = models.OfficialClassNames(raceclass="4wd Short Course")
        officialclass.save()
        
        alias = models.AliasClassNames(raceclass="Pro 4", officialclass=officialclass)
        alias.save()
        alias = models.AliasClassNames(raceclass="4x4 SC", officialclass=officialclass)
        alias.save()
        
        
        classnames = [['mod buggy', None, 'Mod Buggy'],
                      ['modified buggy', None, 'Mod Buggy'],
                      ['MODIFIED BUGGY', None, 'Mod Buggy'],
                      ['Pro 4', None, '4wd Short Course'],
                      ['Pro 4', None, '4wd Short Course'],
                      ['MODIFIED BUGGY', None, 'Mod Buggy'],
                      ['4WD SHORT COURSE', None, '4wd Short Course'],
                      ['4x4 SC', None, '4wd Short Course'],]
        
        self._create_and_validate_classnames(trackname_obj, classnames)    
        
    
    def _create_and_validate_classnames(self, trackname_obj, classnames):
        # Create all the required singleracedetail objects in the DB
        racenum_count = 1
        for classname in classnames:
            classname[1] = self._create_racedetail(trackname_obj, classname[0], racenum_count)
            racenum_count += 1
        
        database_cleanup.collapse_alias_classnames(models.SingleRaceDetails.objects.all())
            
        # Validate that the names were collapse correctly.
        for classname in classnames:
            racedetail = models.SingleRaceDetails.objects.get(pk=classname[1])
            self.assertEqual(classname[2], racedetail.racedata)
            
        
    def _create_racedetail(self, trackname_obj, classname, racenumber):
        racedate = datetime.datetime(year=2011,month=5,day=14,hour=20,minute=9,second=03)
        uploaddate = datetime.datetime(year=2011,month=5,day=15,hour=20,minute=9,second=03)
        
        singlerace = models.SingleRaceDetails(trackkey=trackname_obj,
                                                       racedata=classname,
                                                       racedate=racedate,
                                                       uploaddate=uploaddate,
                                                       racelength='8',
                                                       roundnumber=3,
                                                       racenumber=racenumber,
                                                       winninglapcount='2',
                                                       ) 
        singlerace.save()
        return singlerace.id
