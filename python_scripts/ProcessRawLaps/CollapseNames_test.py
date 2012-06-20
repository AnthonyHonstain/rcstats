'''
Created on Jun 19, 2012

@author: Anthony Honstain
'''

import unittest
import CollapseNames


class TestCollapseNamesSimple(unittest.TestCase):

    def setUp(self):        
        db_results = [[1, 'honstain, anthony', 5], [2, 'anthony houstain', 1], [3, 'Brandon Collins', 2]]
        self.processracerid = CollapseNames.ProcessRacerId(db_results)
        
    def test_misspell_count(self):
        
        self.assertEqual(self.processracerid._misspell_count("abc", "adc"), 2)
        self.assertEqual(self.processracerid._misspell_count("ab", "abcd"), 2)
        self.assertEqual(self.processracerid._misspell_count("ab  ", "  ab"), 0)
        
    def test_check_edit_distance(self):
        
        self.assertEqual(self.processracerid._check_edit_distance("anthony houstain"), "anthony honstain")
        
        # Not checking a distance of 2 yet.
        self.assertEqual(self.processracerid._check_edit_distance("brandon collonz"), "")
        
        
class TestCollapseNamesE2E(unittest.TestCase):

    def setUp(self):        
        db_results = [[1, 'honstain, anthony', 100], 
                      [2, 'john doe', 50],
                      [3, 'anthony houstain', 25],
                      [4, 'ANTHONY HONSTAIN', 20], 
                      [5, 'Brandon Collins', 10],
                      [6, 'Collins, Brandon', 5]]
        self.processracerid = CollapseNames.ProcessRacerId(db_results)
        
    def test_primaryName_dict(self):
        
        self.assertDictEqual(self.processracerid._primaryName_dict, {'anthony honstain':[[1, 'honstain, anthony', 100],
                                                                                         [3, 'anthony houstain', 25],
                                                                                         [4, 'ANTHONY HONSTAIN', 20]],
                                                                     'john doe':[[2, 'john doe', 50],],
                                                                     'brandon collins':[[5, 'Brandon Collins', 10],
                                                                                        [6, 'Collins, Brandon', 5]]})
        

if __name__ == '__main__':  
    unittest.main()   