#!/usr/bin/env python3
"""
Auther: Wes Cratty
Created: 1/3/2024
File: format.py

Description: Handle file read / writes

"""

import os
import json
import re



def get_file_contents(_path):
    """Return the contents of a file."""
    _fl_str = ""
    if os.path.exists(_path):
        with open(_path, 'r') as temp_txt:
            _fl_str = temp_txt.read()
    return _fl_str


def write_file(contents, path, output='w', encoding='utf-8'):
    """Overwrite contents to a file."""
    # Check if directory exists
    if not os.path.exists(os.path.dirname(path)):
        # Create missing directories
        os.makedirs(os.path.dirname(path))

    with open(path, output, encoding=encoding) as out_file:
        out_file.write(contents)
