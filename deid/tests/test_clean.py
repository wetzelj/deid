#!/usr/bin/env python

"""
Test DICOM Cleaner

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
import numpy as np

from deid.utils import get_installdir
from deid.data import get_dataset
from deid.dicom.parser import DicomParser
from deid.dicom import get_identifiers, replace_identifiers
from pydicom import read_file
from pydicom.sequence import Sequence

from collections import OrderedDict

global generate_uid


class TestClean(unittest.TestCase):
    def setUp(self):
        self.pwd = get_installdir()
        self.deid = os.path.abspath("%s/../examples/deid/deid.dicom-mini" % self.pwd)
        self.dataset = get_dataset("animals")
        self.tmpdir = tempfile.mkdtemp()
        print("\n######################START######################")

    def tearDown(self):
        shutil.rmtree(self.tmpdir)
        print("\n######################END########################")

    def test_pixel_cleaner(self):
        """ Test the pixel cleaner to ensure it functions on 2d images.
        """
        from deid.config import DeidRecipe
        from deid.dicom import DicomCleaner

        dicom_file = get_file(self.dataset)

        client = DicomCleaner(output_folder=self.tmpdir, deid=self.deid)
        out = client.detect(dicom_file)
        self.assertTrue(out["flagged"])

        client.clean()
        cleanedfile = client.save_dicom()

        outputfile = read_file(cleanedfile)
        outputpixels = outputfile.pixel_array

        inputfile = read_file(dicom_file)
        inputpixels = inputfile.pixel_array
        compare = inputpixels == outputpixels

        self.assertFalse(compare.all())


def get_file(dataset):
    """helper to get a dicom file"""
    from deid.dicom import get_files

    dicom_files = get_files(dataset)
    return next(dicom_files)


if __name__ == "__main__":
    unittest.main()
