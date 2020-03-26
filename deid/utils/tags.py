"""

Copyright (c) 2018-2020 Vanessa Sochat

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
from pydicom.dataset import RawDataElement, DataElement
import re

def get_tag_key(tag):
    """get_tag_key strips all characters from a dicom tag that are introduced for readability and returns
       a string which can be utilized as the accessor key to retrieve a specific tag from a pydicom Dataset object.
    """
    result = str(tag).replace('(', '').replace(')', '').replace(',', '').replace(' ', '')
    if not re.search("^([0-9]|[A-F]|[a-f]){8}$", result):
        raise ValueError('Input value resulted in an invalid tag key. - %s' % result)

    return result

def get_tag_identifier(element):
    """get_tag_identifier returns either the tag.keyword or element number for a pydicom 
       DataElement object.  The use of this method allows for public tags to be referred to by
       keyword name, but reverts to the hex tag number when no keyword is present (as is the case
       for private tags)
    """
    result = ''
    if isinstance(element, DataElement) or isinstance(element, RawDataElement):
        if element.keyword in ['', None]:
            result = get_tag_key(element.tag)
        else:
            result = element.keyword
    else:
        raise ValueError('Input must be a DataElement or RawDataElement.')

    return result
