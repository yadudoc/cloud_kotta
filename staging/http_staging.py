#!/usr/bin/env python
from __future__ import print_function
from staging import Staging
from executor import execute_wait
from urllib2 import urlopen, HTTPError, URLError
import hashlib
import os

class HTTPStaging(Staging):

    """
    Support fetching an object from an HTTP URL
    """

    def __init__ (self, defn):
        self.src    = defn["src"]
        self.dest   = defn["dest"]
        self.version = None

    def stage_in (self):
        """
        If a specific version is requested we fetch that, otherwise
        we get the latest.
        """
        ret = { 'status'    : True,
                'errcode'   : None,
                'errstring' : None }
        try:
            #urllib.urlretrieve(self.src, self.dest)
            data = urlopen(self.src)
            with open(self.dest, 'wb') as local_file:
                local_file.write(data)

        except HTTPError as e:
            print("Caught HTTPError")
            ret = { 'status'  : False,
                    'errcode' : e.code,
                    'errstring' : "Caught an HTTPError: {0}".format(e.reason) }
        except URLError as e:
            print("Caught URLError")
            ret = { 'status'  : False,
                    'errcode' : 10001,
                    'errstring' : "Caught URLError: {0}".format(e.reason) }
        except Exception as e:
            # This block should never be reached
            print("Caught Blanket Error")
            ret = { 'status'  : False,
                    'errcode' : 10000,
                    'errstring' : "{0}".format(e) }

            
        return ret

    def stage_out(self):
        #print("Git stage out")
        return { 'status'    : False,
                 'errcode'   : 10005,
                 'errstring' : "HTTP stageout not implemented" }

    def version_info(self):
        if not self.version :
            if os.path.exists(self.dest):
                self.version = hashlib.md5(self.dest).hexdigest()
            
        return self.version


def test1():
    # No commit 
    print("Testing: plain src, dest")
    defn   = {"src"  : "https://raw.githubusercontent.com/yadudoc/cloud_kotta/master/LICENCE",
              "dest" : "LICENCE"}
    obj    = HTTPStaging(defn)
    status = obj.stage_in()
    assert status['errcode'] == None and status['status'] == True

def test2():
    # With commit
    print("Testing: plain src, alternate dest")
    defn   = {"src"  : "https://raw.githubusercontent.com/yadudoc/cloud_kotta/master/LICENCE",
              "dest" : "LICENCE.2"}
    obj    = HTTPStaging(defn)
    status = obj.stage_in()
    assert status['errcode'] == None and status['status'] == True
    assert os.path.exists('LICENCE.2')

def test3():
    # Bad src
    print("Testing: Bad http repo")
    defn   = {"src"  : "https://raw.githubusercontent.com/yadudoc/cloud_kotta/master/LICENCE2",
              "dest" : "LICENCE.3"}
    obj    = HTTPStaging(defn)
    status = obj.stage_in()

    print(status)
    assert status['errcode'] != None and status['status'] == False


def test4():
    # Bad src
    print("Testing: Bad http repo")
    defn   = {"src"  : "hts://raw.githubusercontent.com/yadudoc/cloud_kotta/master/LICENCE2",
              "dest" : "LICENCE.2"}
    obj    = HTTPStaging(defn)
    status = obj.stage_in()
    print(status)
    

if __name__ == "__main__" :


    test1()
    test2()
    test3()
    test4()

    #shutil.rmtree(defn["dest"])
