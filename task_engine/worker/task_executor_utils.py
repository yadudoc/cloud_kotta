#!/usr/bin/env python
import urllib

def download_file(URL, filename):
    urllib.urlretrieve(URL, filename)

