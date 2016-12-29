#!/usr/bin/env python
from __future__ import print_function
from staging import Staging
from executor import execute_wait
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
        self.version = self.commit

    def stage_in (self):
        """
        If a specific version is requested we fetch that, otherwise
        we get the latest.
        """
        #print("Git stage in")
        if self.commit :            
            #Requesting a specific git version
            cmd = """git clone {0} {1};
            git --git-dir={1}/.git/ --work-tree={1}/ checkout {2}
            """.format(self.src,  # Source git
                       self.dest, # Dest dir
                       self.commit # Commit hash
            )            
            ret = execute_wait(cmd);
        else:
            # Get the latest but record the git version
            cmd = "git clone {0} {1}".format(self.src, self.dest)
            ret = execute_wait(cmd);
            self.version_info()

        return ret

    def stage_out(self):
        #print("Git stage out")
        return { 'status'    : False,
                 'errcode'   : 1005,
                 'errstring' : "Git stageout not implemented" }

    def version_info(self):
        if not self.version :
            commit_hash = None
            ret = None
            cmd = "git --git-dir={0}/.git/ --work-tree={0}/ rev-parse HEAD ".format("TuringClient")
            with open("commit_hash.txt", 'w') as info_file:
                ret = execute_wait(cmd, None, stdout_fp=info_file)
                #print(ret)
                if ret['status'] == True:                
                    with open("commit_hash.txt", 'r') as info_file:
                        commit_hash = info_file.readlines()[0].strip()

            self.version = commit_hash

        return self.version





def test1():
    # No commit 
    ret = execute_wait("rm -rf TuringClient", None)

    print("Testing: plain src, dest")
    defn   = {"src"  : "https://github.com/yadudoc/TuringClient.git",
              "dest" : "TuringClient"}
    obj    = GitStaging(defn)
    status = obj.stage_in()
    print(obj.version_info())
    print(status)

def test2():
    # With commit
    ret = execute_wait("rm -rf TuringClient", None)
    
    print("Testing: plain src, dest, commit")
    defn   = {"src"  : "https://github.com/yadudoc/TuringClient.git",
              "commit" : "b7bf44e6f5e69cdb86c60e54a7b2a304822f02a6", # Commit hash
              "dest" : "TuringClient"}
    obj    = GitStaging(defn)
    status = obj.stage_in()
    print(obj.version_info())
    print(status)

def test3():
    # Bad src
    ret = execute_wait("rm -rf TuringClient", None)
    
    print("Testing: Bad git repo")
    defn   = {"src"  : "https://github.com/yadudoc/TuringBad.git",
              "dest" : "TuringClient"}
    obj    = GitStaging(defn)
    status = obj.stage_in()
    print(status)
    

if __name__ == "__main__" :


    test1()
    test2()
    test3()

    #shutil.rmtree(defn["dest"])
