#!/usr/bin/env python
import future
from abc import ABCMeta, abstractmethod
import executor

class Staging(object):
    """
    This class defines the common interface that any staging provider must implement.
    We are unable to mandate the return type for the subclasses here, but we
    require them to be :
    if ok :
           { status : True,
             version : <>,
             staging_time : <>
            }
    else  :
           { status : False,
             errcode : <>,
             errstring : <> }
    """
    __metaclass__ = ABCMeta

    @abstractmethod
    def stage_in(self):
        return

    @abstractmethod
    def stage_out(self):
        return
    
    @abstractmethod
    def version_info(self):
        return


class GitStaging(Staging):

    """
    Support fetching code from a github repository to a the PWD and track the commit used.
    We basically have to do:
    git clone self.src self.dest
    print(ret)
    assert ret['exitcode'] == 0
    git --git-dir=<DIR>/.git/ --work-tree=<DIR>/ checkout b7bf44e6f5e69cdb86c60e54a7b2a304822f02a6
    """

    def __init__ (self, defn):
        self.src    = defn["src"]
        self.dest   = defn["dest"]
        self.branch = defn.get("branch", None)
        self.commit = defn.get("commit", None)
        self.version = None

    def stage_in (self):
        print("Git stage in")
        cmd = "git clone {0} {1}".format(self.src, self.dest)
        ret = execute_wait(cmd);
        
        return { 'status' : True,
                 'version' : version_info(),
                 'staging_time' : 
            }

    def stage_out(self):
        print("Git stage out")
        return { 'status' : False,
                 'errcode' : 1005,
                 'errstring' : "Git stageout not implemented" }

    def version_info(self):
        if not self.version :
            cmd = "git --git-dir={0} --work-tree={0} rev-parse HEAD"
            self.version = "XXXX"

        return self.version




if __name__ == "__main__" :

    print("Testing")
