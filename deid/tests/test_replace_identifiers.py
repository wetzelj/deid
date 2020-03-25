#!/usr/bin/env python

"""
Test replace_identifiers

The MIT License (MIT)

Copyright (c) 2016-2020 Vanessa Sochat

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

"""

import unittest
import tempfile
import shutil
import json
import os

from deid.utils import get_installdir
from deid.data import get_dataset

global generate_uid


class TestDicomUtils(unittest.TestCase):
    def setUp(self):
        self.pwd = get_installdir()
        self.deid = os.path.abspath("%s/../examples/deid/deid.dicom" % self.pwd)
        self.dataset = get_dataset("humans")
        self.tmpdir = tempfile.mkdtemp()
        print("\n######################START######################")

    def tearDown(self):
        shutil.rmtree(self.tmpdir)
        print("\n######################END########################")

    def test_get_files(self):
        print("Test test_get_files")
        print("Case 1: Test get files from dataset")
        from deid.dicom import get_files
        from deid.config import load_deid

        found = 0
        for dicom_file in get_files(self.dataset):
            found += 1
        expected = 1
        self.assertEqual(found, expected)

        print("Case 2: Ask for files from empty folder")
        found = 0
        for dicom_file in get_files(self.tmpdir):
            found += 1
        expected = 0
        self.assertEqual(found, expected)

    def test_get_files_as_list(self):
        print("Test test_get_files_as_list")
        print("Case 1: Test get files from dataset")
        from deid.dicom import get_files
        from deid.config import load_deid

        dicom_files = list(get_files(self.dataset))
        found = len(dicom_files)
        expected = 1
        self.assertEqual(found, expected)

        print("Case 2: Ask for files from empty folder")
        dicom_files = list(get_files(self.tmpdir))
        found = len(dicom_files)
        expected = 0
        self.assertEqual(found, expected)

    def test_add_private_constant(self):
        from deid.dicom import get_identifiers
        from deid.dicom import replace_identifiers
        print("Test add private tag constant value")
        dicom_file = get_file(self.dataset)

        actions = [{'action': 'ADD',
                'field' : '11112221',
                'value' : 'SIMPSON'}]
        recipe = create_recipe(actions)
        ids = get_identifiers(dicom_file)
        
        result = replace_identifiers(dicom_files=dicom_file,
                            ids=ids,
                            deid=recipe, 
                            save=False,
                            remove_private=False,
                            strip_sequences=False)
        self.assertEqual(1, len(result))
        self.assertEqual('SIMPSON', result[0]['11112221'].value)

    def test_add_public_constant(self):
        from deid.dicom import get_identifiers
        from deid.dicom import replace_identifiers
        print("Test add public tag constant value")
        dicom_file = get_file(self.dataset)

        actions = [{'action': 'ADD',
                'field' : 'PatientIdentityRemoved',
                'value' : 'Yeppers!'}]
        recipe = create_recipe(actions)
        ids = get_identifiers(dicom_file)
        
        result = replace_identifiers(dicom_files=dicom_file,
                            ids=ids,
                            deid=recipe, 
                            save=False,
                            remove_private=False,
                            strip_sequences=False)
        self.assertEqual(1, len(result))
        self.assertEqual('Yeppers!', result[0].PatientIdentityRemoved)

    def test_replace_with_constant(self):
        from deid.dicom import get_identifiers
        from deid.dicom import replace_identifiers
        print("Test replace tags with constant values")
        dicom_file = get_file(self.dataset)

        newfield1 = 'AccessionNumber'
        newvalue1 = '987654321'
        newfield2 = '00190010'
        newvalue2 = 'NEW VALUE!'

        actions = [{'action': 'REPLACE',
                'field' : newfield1,
                'value' : newvalue1},
                {'action': 'REPLACE',
                'field' : newfield2,
                'value' : newvalue2}]
        recipe = create_recipe(actions)
        ids = get_identifiers(dicom_file)

        self.assertNotEqual(newvalue1, ids[dicom_file][newfield1])
        self.assertNotEqual(newvalue2, ids[dicom_file][newfield2])
        result = replace_identifiers(dicom_files=dicom_file,
                            ids=ids,
                            deid=recipe, 
                            save=False,
                            remove_private=False,
                            strip_sequences=False)
        self.assertEqual(1, len(result))
        self.assertEqual(newvalue1, result[0][newfield1].value)
        self.assertEqual(newvalue2, result[0][newfield2].value)

    def test_remove(self):
        from deid.dicom import get_identifiers
        from deid.dicom import replace_identifiers
        print("Test remove of public and private tags")
        dicom_file = get_file(self.dataset)

        field1 = 'InstitutionName'
        field2 = '00190010'
        
        actions = [{'action': 'REMOVE',
                'field' : field1},
                {'action': 'REMOVE',
                'field' : field2}]
        recipe = create_recipe(actions)
        ids = get_identifiers(dicom_file)

        self.assertIsNotNone(ids[dicom_file][field1])
        self.assertIsNotNone(ids[dicom_file][field2])
        result = replace_identifiers(dicom_files=dicom_file,
                            ids=ids,
                            deid=recipe, 
                            save=False,
                            remove_private=False,
                            strip_sequences=False)
        self.assertEqual(1, len(result))
        with self.assertRaises(KeyError):
            check1 = result[0][field1].value
        with self.assertRaises(KeyError):
            check2 = result[0][field2].value

    def test_add_tag_variable(self):
        # Add to public and private tag
        self.assertTrue(True)
    
    def test_jitter_date(self):
        # DICOM datatype DA
        self.assertTrue(True)

    def test_jitter_timestamp(self):
        # DICOM datatype DT
        self.assertTrue(True)

    def test_expanders(self):
        # Include contains, endswith, startswith
        '''
        #REMOVE contains:Collimation
        #REMOVE endswith:Diameter
        #REMOVE startswith:Study
        '''
        self.assertTrue(True)

    def test_expander_except(self):
        #REMOVE except:Manufacturer
        self.assertTrue(True)

    def test_fieldset_public_only(self):
        '''
        %fields field_set1
        FIELD Manufacturer
        FIELD contains:Time
        '''
        #REMOVE fields:field_set1
        self.assertTrue(True)

    def test_valueset_public_only(self):
        '''
        %values value_set1
        FIELD contains:Manufacturer
        SPLIT contains:Physician by="^";minlength=3
        '''
        #REMOVE values:value_set1
        self.assertTrue(True)

    def test_fieldset_public_private(self):
        '''
        %fields field_set2_private
        FIELD 00090010
        FIELD PatientID
        '''
        #REMOVE fields:field_set2_private
        self.assertTrue(True)

    def test_valueset_private(self):
        '''
        %values value_set2_private
        FIELD 00311020
        SPLIT 00090010 by=" ";minlength=4
        '''
        #REMOVE values:value_set2_private
        self.assertTrue(True)

    def test_tag_expanders_taggroup(self):
        #REMOVE contains:0009
        self.assertTrue(True)

    def test_tag_expanders_midtag(self):
        #mid tag (0028,0010) - this tag should not be included
        #REMOVE contains:8001
        self.assertTrue(True)

    def test_tag_expanders_tagelement(self):
        #includes public and private, groups and element numbers
        #REMOVE contains:0010
        self.assertTrue(True)

    def test_remove_all_func(self):
        #REMOVE ALL func:sometimes_returntrue_sometimes_returnfalse
        self.assertTrue

    # MORE TESTS NEED TO BE WRITTEN TO TEST SEQUENCES

def create_recipe(actions):
    """helper method to create a recipe file 
    """
    from deid.config import DeidRecipe

    recipe = DeidRecipe()
    recipe.deid['header'].clear()
    recipe.deid['header'] = actions

    return recipe

def get_file(dataset):
    """helper to get a dicom file 
    """
    from deid.dicom import get_files

    dicom_files = get_files(dataset)
    return next(dicom_files)


if __name__ == "__main__":
    unittest.main()