# -*- coding: utf-8 -*-
"""
:samp:`Various utility functions`

"""
import hashlib
import mimetypes
import time
import os
import urllib.parse
import urllib.request
from datetime import datetime
from functools import partial


def sanitize_url_path(value):
    if value:
        value = urllib.parse.quote(value.replace("\\", "/"))
    return sanitize_string(value)


def sanitize_string(value):
    if (not value):
        value = ""
    return value


def w3c_datetime(i):
    """ given seconds since the epoch, return a dateTime string.
    from: https://gist.github.com/mnot/246088
    """
    assert type(i) in [int, float]
    year, month, day, hour, minute, second, wday, jday, dst = time.gmtime(i)
    o = str(year)
    if (month, day, hour, minute, second) == (1, 1, 0, 0, 0): return o
    o += '-%2.2d' % month
    if (day, hour, minute, second) == (1, 0, 0, 0): return o
    o += '-%2.2d' % day
    if (hour, minute, second) == (0, 0, 0): return o
    o += 'T%2.2d:%2.2d' % (hour, minute)
    if second != 0:
        o += ':%2.2d' % second
    o += 'Z'
    return o


def w3c_now():
    return w3c_datetime(datetime.now().timestamp())

def file_modification_date(filename=''):
  if filename =='':
    str1 = time.asctime()
  else:
    str1 = time.ctime(os.path.getmtime(filename))
  return str1

def reformat_datetime(str1):
  datetime_object = datetime.strptime(str1, '%a %b %d %H:%M:%S %Y')
  return datetime_object.strftime("%Y-%m-%dT%H:%M:%SZ")

def md5_for_file(filename, block_size=2**14):
    """Compute MD5 digest for a file

    Optional block_size parameter controls memory used to do MD5 calculation.
    This should be a multiple of 128 bytes.
    """
    with open(filename, mode='rb') as f:
        d = hashlib.md5()
        for buf in iter(partial(f.read, block_size), b''):
            d.update(buf)
    #return base64.b64encode(d.digest()).decode('utf-8')
    return d.hexdigest()


def mime_type(filename):
    """ Not too reliable mime type analyzer."""
    url = urllib.request.pathname2url(filename)
    return mimetypes.guess_type(url)[0]

