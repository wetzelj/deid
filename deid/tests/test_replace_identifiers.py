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

from collections import OrderedDict

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
        """ RECIPE RULE
        ADD 11112221 SIMPSON
        """

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
        """ RECIPE RULE
        ADD PatientIdentityRemoved Yeppers!
        """

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
        """ RECIPE RULE
        REPLACE AccessionNumber 987654321
        REPLACE 00190010 NEWVALUE!
        """

        from deid.dicom import get_identifiers
        from deid.dicom import replace_identifiers
        print("Test replace tags with constant values")
        dicom_file = get_file(self.dataset)

        newfield1 = 'AccessionNumber'
        newvalue1 = '987654321'
        newfield2 = '00190010'
        newvalue2 = 'NEWVALUE!'

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
        """ RECIPE RULE
        REMOVE InstitutionName
        REMOVE 00190010
        """

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
        """ RECIPE RULE
        ADD 11112221 var:myVar
        ADD PatientIdentityRemoved var:myVar
        """

        from deid.dicom import get_identifiers
        from deid.dicom import replace_identifiers
        print("Test add tag constant value from variable")
        dicom_file = get_file(self.dataset)

        actions = [{'action': 'ADD',
                'field' : '11112221',
                'value' : 'var:myVar'},
                {'action': 'ADD',
                'field' : 'PatientIdentityRemoved',
                'value' : 'var:myVar'}]
        recipe = create_recipe(actions)
        ids = get_identifiers(dicom_file)
        ids[dicom_file]['myVar'] = 'SIMPSON'
        
        result = replace_identifiers(dicom_files=dicom_file,
                            ids=ids,
                            deid=recipe, 
                            save=False,
                            remove_private=False,
                            strip_sequences=False)
        self.assertEqual(1, len(result))
        self.assertEqual('SIMPSON', result[0]['11112221'].value)
        self.assertEqual('SIMPSON', result[0]['PatientIdentityRemoved'].value)

    def test_jitter_date(self):
        # DICOM datatype DA
        """ RECIPE RULE
        JITTER StudyDate 1
        """

        from deid.dicom import get_identifiers
        from deid.dicom import replace_identifiers
        print("Test date jitter")
        dicom_file = get_file(self.dataset)

        actions = [{'action': 'JITTER',
                'field' : 'StudyDate',
                'value' : '1'}]
        recipe = create_recipe(actions)
        ids = get_identifiers(dicom_file)
                
        result = replace_identifiers(dicom_files=dicom_file,
                            ids=ids,
                            deid=recipe, 
                            save=False,
                            remove_private=False,
                            strip_sequences=False)
        self.assertEqual(1, len(result))
        self.assertEqual('20230102', result[0]['StudyDate'].value)

    def test_jitter_timestamp(self):
        # DICOM datatype DT
        """ RECIPE RULE
        JITTER AcquisitionDateTime 1
        """

        from deid.dicom import get_identifiers
        from deid.dicom import replace_identifiers
        print("Test timestamp jitter")
        dicom_file = get_file(self.dataset)

        actions = [{'action': 'JITTER',
                'field' : 'AcquisitionDateTime',
                'value' : '1'}]
        recipe = create_recipe(actions)
        ids = get_identifiers(dicom_file)
                
        result = replace_identifiers(dicom_files=dicom_file,
                            ids=ids,
                            deid=recipe, 
                            save=False,
                            remove_private=False,
                            strip_sequences=False)
        self.assertEqual(1, len(result))
        self.assertEqual('20230102011721.621000', result[0]['AcquisitionDateTime'].value)

    def test_expanders(self):
        ''' RECIPE RULES
        REMOVE contains:Collimation
        REMOVE endswith:Diameter
        REMOVE startswith:Exposure
        '''

        from deid.dicom import get_identifiers
        from deid.dicom import replace_identifiers
        print("Test contains, endswith, and startswith expanders")
        dicom_file = get_file(self.dataset)

        actions = [{'action': 'REMOVE',
                'field' : 'contains:Collimation'},
                {'action': 'REMOVE',
                'field' : 'endswith:Diameter'},
                {'action': 'REMOVE',
                'field' : 'startswith:Exposure'}]
        recipe = create_recipe(actions)
        ids = get_identifiers(dicom_file)
        result = replace_identifiers(dicom_files=dicom_file,
                            ids=ids,
                            deid=recipe, 
                            save=False,
                            remove_private=False,
                            strip_sequences=False)
        self.assertEqual(1, len(result))
        self.assertEqual(153, len(result[0]))
        with self.assertRaises(KeyError):
            check1 = result[0]['ExposureTime'].value
        with self.assertRaises(KeyError):
            check2 = result[0]['TotalCollimationWidth'].value
        with self.assertRaises(KeyError):
            check3 = result[0]['DataCollectionDiameter'].value

    def test_expander_except(self):
        ''' RECIPE RULE
        REMOVE except:Manufacturer
        '''

        from deid.dicom import get_identifiers
        from deid.dicom import replace_identifiers
        print("Test except expander")
        dicom_file = get_file(self.dataset)

        actions = [{'action': 'REMOVE',
                'field' : 'except:Manufacturer'}]
        recipe = create_recipe(actions)
        ids = get_identifiers(dicom_file)
        result = replace_identifiers(dicom_files=dicom_file,
                            ids=ids,
                            deid=recipe, 
                            save=False,
                            remove_private=False,
                            strip_sequences=False)
        self.assertEqual(1, len(result))
        self.assertEqual(2, len(result[0]))
        self.assertEqual('SIEMENS', result[0]['Manufacturer'].value)
        with self.assertRaises(KeyError):
            check1 = result[0]['ExposureTime'].value
        with self.assertRaises(KeyError):
            check2 = result[0]['TotalCollimationWidth'].value
        with self.assertRaises(KeyError):
            check3 = result[0]['DataCollectionDiameter'].value

    def test_fieldset_public_only(self):
        '''  RECIPE        
        %fields field_set1
        FIELD Manufacturer
        FIELD contains:Time
        %header
        REMOVE fields:field_set1
        '''

        from deid.dicom import get_identifiers
        from deid.dicom import replace_identifiers
        print("Test public tag fieldset")
        dicom_file = get_file(self.dataset)

        actions = [{'action': 'REMOVE',
                'field' : 'fields:field_set1'}]
        fields = OrderedDict()
        fields['field_set1'] = [{'field': 'Manufacturer', 'action': 'FIELD'},
                                {'field': 'contains:Collimation', 'action': 'FIELD'}]
        recipe = create_recipe(actions, fields)
        ids = get_identifiers(dicom_file)
        result = replace_identifiers(dicom_files=dicom_file,
                            ids=ids,
                            deid=recipe, 
                            save=False,
                            remove_private=False,
                            strip_sequences=False)
        self.assertEqual(1, len(result))
        self.assertEqual(157, len(result[0]))
        with self.assertRaises(KeyError):
            check1 = result[0]['Manufacturer'].value
        with self.assertRaises(KeyError):
            check2 = result[0]['TotalCollimationWidth'].value
        with self.assertRaises(KeyError):
            check3 = result[0]['SingleCollimationWidth'].value

    def test_valueset_public_only(self):
        '''
        %values value_set1
        FIELD contains:Manufacturer
        SPLIT contains:Physician by="^";minlength=3
        %header REMOVE values:value_set1
        '''

        from deid.dicom import get_identifiers
        from deid.dicom import replace_identifiers
        print("Test public tag valueset")
        dicom_file = get_file(self.dataset)

        actions = [{'action': 'REMOVE',
                'field' : 'values:value_set1'}]
        values = OrderedDict()
        values['value_set1'] = [{'field': 'contains:Manufacturer', 'action': 'FIELD'},
                                {'value': 'by="^";minlength=3', 'field': 'contains:Physician', 'action': 'SPLIT'}]
        recipe = create_recipe(actions, values=values)
        ids = get_identifiers(dicom_file)
        result = replace_identifiers(dicom_files=dicom_file,
                            ids=ids,
                            deid=recipe, 
                            save=False,
                            remove_private=False,
                            strip_sequences=False)
        self.assertEqual(1, len(result))
        self.assertEqual(146, len(result[0]))
        with self.assertRaises(KeyError):
            check1 = result[0]['00090010'].value
        with self.assertRaises(KeyError):
            check2 = result[0]['Manufacturer'].value
        with self.assertRaises(KeyError):
            check3 = result[0]['PhysiciansOfRecord'].value

    def test_fieldset_public_private(self):
        '''
        %fields field_set2_private
        FIELD 00090010
        FIELD PatientID
        %header
        REMOVE fields:field_set2_private
        '''

        from deid.dicom import get_identifiers
        from deid.dicom import replace_identifiers
        print("Test private tag fieldset")
        dicom_file = get_file(self.dataset)

        actions = [{'action': 'REMOVE',
                'field' : 'fields:field_set2_private'}]
        fields = OrderedDict()
        fields['field_set2_private'] = [{'field': '00090010', 'action': 'FIELD'},
                                {'field': 'PatientID', 'action': 'FIELD'}]
        recipe = create_recipe(actions, fields)
        ids = get_identifiers(dicom_file)
        result = replace_identifiers(dicom_files=dicom_file,
                            ids=ids,
                            deid=recipe, 
                            save=False,
                            remove_private=False,
                            strip_sequences=False)
        self.assertEqual(1, len(result))
        self.assertEqual(158, len(result[0]))
        with self.assertRaises(KeyError):
            check1 = result[0]['00090010'].value
        with self.assertRaises(KeyError):
            check2 = result[0]['PatientID'].value

    def test_valueset_private(self):
        '''
        %values value_set2_private
        FIELD 00311020
        SPLIT 00090010 by=" ";minlength=4
        %header
        REMOVE values:value_set2_private
        '''

        from deid.dicom import get_identifiers
        from deid.dicom import replace_identifiers
        print("Test private tag valueset")
        dicom_file = get_file(self.dataset)

        actions = [{'action': 'REMOVE',
                'field' : 'values:value_set2_private'}]
        values = OrderedDict()
        values['value_set2_private'] = [{'field': '00311020', 'action': 'FIELD'},
                                {'value': 'by=" ";minlength=4', 'field': '00090010', 'action': 'SPLIT'}]
        recipe = create_recipe(actions, values=values)
        ids = get_identifiers(dicom_file)
        result = replace_identifiers(dicom_files=dicom_file,
                            ids=ids,
                            deid=recipe, 
                            save=False,
                            remove_private=False,
                            strip_sequences=False)
        self.assertEqual(1, len(result))
        # TODO - I think this fails because of the _ in (0008, 0102)
        self.assertEqual(148, len(result[0]))
        with self.assertRaises(KeyError):
            check1 = result[0]['OtherPatientIDs'].value
        with self.assertRaises(KeyError):
            check2 = result[0]['Manufacturer'].value
        with self.assertRaises(KeyError):
            check3 = result[0]['00190010'].value

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

def create_recipe(actions, fields=None, values=None):
    """helper method to create a recipe file 
    """
    from deid.config import DeidRecipe

    recipe = DeidRecipe()
    recipe.deid['header'].clear()
    recipe.deid['header'] = actions

    if fields is not None:
        recipe.deid['fields'] = fields

    if values is not None: 
        recipe.deid['values'] = values

    return recipe

def get_file(dataset):
    """helper to get a dicom file 
    """
    from deid.dicom import get_files

    dicom_files = get_files(dataset)
    return next(dicom_files)


if __name__ == "__main__":
    unittest.main()