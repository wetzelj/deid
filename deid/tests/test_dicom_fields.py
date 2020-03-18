#!/usr/bin/env python

"""
Testing field parsing and expansion

Copyright (c) 2020 Vanessa Sochat

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
from deid.dicom.tags import get_private
from pydicom.tag import BaseTag


class TestDicomFields(unittest.TestCase):
    def setUp(self):
        self.pwd = get_installdir()
        self.deid = os.path.abspath("%s/../examples/deid/deid.dicom" % self.pwd)
        self.dataset = get_dataset("animals")  # includes private tags
        self.tmpdir = tempfile.mkdtemp()
        print("\n######################START######################")

    def tearDown(self):
        shutil.rmtree(self.tmpdir)
        print("\n######################END########################")

    def test_field_expansion(self):
        print("Test deid.dicom.fields expand_field_expression")
        from deid.dicom.fields import expand_field_expression
        from deid.dicom.fields import dicom_dir

        dicom = get_dicom(self.dataset)
        #contenders = dicom.dir()
        contenders = dicom_dir(dicom)

        print("Testing that field expansion works for basic tags")
        expand_field_expression(
            dicom=dicom, field="endswith:Time", contenders=contenders
        )

        print("Testing that field expansion works including private tags")
        contenders += [e.tag for e in get_private(dicom)]
        expand_field_expression(
            dicom=dicom, field="endswith:Time", contenders=contenders
        )

        print("Testing that we can also search private tags based on numbers.")
        fields = expand_field_expression(
            dicom=dicom, field="contains:0019", contenders=contenders
        )

        # We should have a tag object in the list now!
        assert isinstance(fields[0], BaseTag)

    
    def test_skip_list(self):
        # Demonstrates the bug with deid/dicom/fields.py - ln 222
        print("Test exclusion of items from skip list")
        from deid.dicom.fields import dicom_dir

        skip = ['PixelData']

        dicom = get_dicom(self.dataset)
        contenders = dicom_dir(dicom)        
        newcontenders = []

        for contender in contenders:
            if contender in skip:
                continue
            else:
                newcontenders.append(contender)

        with self.assertRaises(ValueError) as exc:
            pixeldata = newcontenders.index('PixelData')
        
        self.assertEqual("'PixelData' is not in list", str(exc.exception))
    
    def test_conditional_expansion(self):
        # Demonstrates the bug with deid/dicom/actions.py - ln 105
        # When this code is executed, we're performing a specific action
        #      REMOVE CodeValue
        # Ultimately, at this point in the code, we're trying to remove 
        # expanded CodeValues
        #      FieldA__CodeValue
        #      FieldB__CodeValue

        print("Test for comparison of items to expanded sequences")
        from deid.dicom.fields import dicom_dir
        from deid.dicom.fields import get_fields
        import re

        dicom = get_dicom(self.dataset)
        fields = get_fields(dicom, expand_sequences=True)
        field = 'CodeValue'
        
        expanded_regexp = "__%s$" % field
        
        expanded_fields = [x for x in fields if re.search(expanded_regexp, x)] 
        
        # TODO - Determine what needs to be checked.  Currently throws an exception
        self.assertTrue(True)


def get_dicom(dataset):
    """helper function to load a dicom
    """
    from deid.dicom import get_files
    from pydicom import read_file

    dicom_files = get_files(dataset)
    return read_file(next(dicom_files))


if __name__ == "__main__":
    unittest.main()

