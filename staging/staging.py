#!/usr/bin/env python

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

