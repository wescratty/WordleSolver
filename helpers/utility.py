#!/usr/bin/env python3
"""
Author:
Created: 1/3/2024
File: utility.py

Description: Collection of helper classes

"""
from enum import Enum


class LogType(Enum):
    task = 0
    info = 1
    warning = 2
    error = 3
    exception = 4


class Theme(Enum):
    newspaper = 0
    retroMac = 1
    inverse_newspaper = 2
    dungeon = 3


class HttpMethod(Enum):
    GET = 0
    PATCH = 1
    POST = 2
    PUT = 3
    DELETE = 4
