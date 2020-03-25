"""

Copyright (c) 2017-2020 Vanessa Sochat

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

from deid.logger import bot
from pydicom.sequence import Sequence
from pydicom.dataset import RawDataElement, Dataset
from pydicom.tag import Tag
import re


def extract_item(item, prefix=None, entry=None):
    """a helper function to extract sequence, will extract values from 
       a dicom sequence depending on the type.

       Parameters
       ==========
       item: an item from a sequence.
    """
    # First call, we define entry to be a lookup dictionary
    if entry is None:
        entry = {}

    # Skip raw data elements
    if not isinstance(item, RawDataElement):
        if item.keyword == '':            
            tagstring = str(item.tag).replace('(', '').replace(')', '').replace(',', '').replace(' ', '')
            header = str(tagstring)
        else:
            header = item.keyword

        # If there is no header or field, we can't evaluate
        if header in [None, ""]:
            return entry

        if prefix is not None:
            header = "%s__%s" % (prefix, header)

        value = item.value
        if isinstance(value, bytes):
            value = value.decode("utf-8")
        if isinstance(value, Sequence):
            return extract_sequence(value, prefix=header)

        entry[header] = value
    return entry


def extract_sequence(sequence, prefix=None):
    """return a pydicom.sequence.Sequence recursively
       as a flattened list of items. For example, a nested FieldA and FieldB
       would return as:

       {'FieldA[x]__FieldB': '111111'}

       Parameters
       ==========
       sequence: the sequence to extract, should be pydicom.sequence.Sequence
       prefix: the parent name
    """
    items = {}
    occurrence = 0
    for item in sequence:
        pre = "{}[{}]".format(prefix, str(occurrence))
        # If it's a Dataset, we need to further unwrap it
        if isinstance(item, Dataset):
            for subitem in item:
                items.update(extract_item(subitem, prefix=pre))
        else:
            bot.warning(
                "Unrecognized type %s in extract sequences, skipping." % type(item)
            )
        occurrence = occurrence + 1
    return items


def find_by_values(values, dicom):
    """Given a list of values, find fields in the dicom that contain any
       of those values, as determined by a regular expression search.
    """
    # Values must be strings
    values = [str(x) for x in values]

    fields = []
    contenders = get_fields(dicom)

    # Create single regular expression to search by
    regexp = "(%s)" % "|".join(values)
    for field, value in contenders.items():
        if re.search(regexp, str(value), re.IGNORECASE):
            fields.append(field)

    return fields


def expand_field_expression(field, dicom, contenders=None):
    """Get a list of fields based on an expression. If 
       no expression found, return single field. Options for fields include:

        endswith: filter to fields that end with the expression
        startswith: filter to fields that start with the expression
        contains: filter to fields that contain the expression
        allfields: include all fields
        exceptfields: filter to all fields except those listed ( | separated)   
    """
    # Expanders that don't have a : must be checked for
    expanders = ["all"]

    # if no contenders provided, use all in dicom headers
    if contenders is None:
        contenders = dicom.iterall()

    # Case 1: field is an expander without an argument (e.g., no :)
    if field.lower() in expanders:

        if field.lower() == "all":
            fields = []
            for x in contenders:
                if x.keyword == '':            
                    tagstring = str(x.tag).replace('(', '').replace(')', '').replace(',', '').replace(' ', '')
                    tagid = str(tagstring)
                else:
                    tagid = x.keyword
                fields.append(tagid)
        return fields

    # Case 2: The field is a specific field OR an expander with argument (A:B)
    fields = field.split(":")
    if len(fields) == 1:
        return fields

    # if we get down here, we have an expander and expression
    expander, expression = fields
    expression = expression.lower()
    fields = []

    # Expanders here require an expression, and have <expander>:<expression>
    if expander.lower() == "endswith":
        fields = []
        for x in contenders:
            if re.search("(%s)$" % expression, x.keyword.lower()) or re.search("(%s)$" % expression, str(x.tag)):
                if x.keyword == '':            
                    tagstring = str(x.tag).replace('(', '').replace(')', '').replace(',', '').replace(' ', '')
                    tagid = str(tagstring)
                else:
                    tagid = x.keyword
                fields.append(tagid)

    elif expander.lower() == "startswith":
        fields = []
        for x in contenders:
            if re.search("^(%s)" % expression, x.keyword.lower()) or re.search("^(%s)" % expression, str(x.tag)):
                if x.keyword == '':            
                    tagstring = str(x.tag).replace('(', '').replace(')', '').replace(',', '').replace(' ', '')
                    tagid = str(tagstring)
                else:
                    tagid = x.keyword
                fields.append(tagid)

    elif expander.lower() == "except":
        fields = []
        for x in contenders:
            if not re.search(expression, x.keyword.lower()) and not re.search(expression, str(x.tag)):
                if x.keyword == '':            
                    tagstring = str(x.tag).replace('(', '').replace(')', '').replace(',', '').replace(' ', '')
                    tagid = str(tagstring)
                else:
                    tagid = x.keyword
                fields.append(tagid)

    elif expander.lower() == "contains":
        fields = []
        for x in contenders:
            if (re.search(expression, x.keyword.lower()) or re.search(expression, str(x.tag))) and x.value not in [None, ""] :
                if x.keyword == '':            
                    tagstring = str(x.tag).replace('(', '').replace(')', '').replace(',', '').replace(' ', '')
                    tagid = str(tagstring)
                else:
                    tagid = x.keyword
                fields.append(tagid)

    return fields


def get_fields(dicom, skip=None, expand_sequences=True):
    """get fields is a simple function to extract a dictionary of fields
       (non empty) from a dicom file.

       Parameters
       ==========
       dicom: the dicom file to get fields for.
       skip: an optional list of fields to skip
       expand_sequences: if True, expand values that are sequences.
    """
    if skip is None:
        skip = []
    if not isinstance(skip, list):
        skip = [skip]

    fields = dict()

    for elem in dicom.iterall():
        if elem.keyword in skip or str(elem.tag) in skip:
            continue

        if elem.keyword == '':            
            tagstring = str(elem.tag).replace('(', '').replace(')', '').replace(',', '').replace(' ', '')
            key = str(tagstring)
        else:
            key = elem.keyword

        value = elem.value
        
        # Adding expanded sequences
        if isinstance(value, Sequence) and expand_sequences is True:
            fields.update(extract_sequence(value, key))

        if elem.value not in [None, ""]:
            if isinstance(elem.value, bytes):
                try:
                    value = elem.value.decode("utf-8")
                except:
                    # TODO - need to look into this bug.  Some byte values cannot be decoded 
                    # to utf-8, we willl probably need to check encoding
                    pass 
                    
            fields[key] = elem.value 

    return fields